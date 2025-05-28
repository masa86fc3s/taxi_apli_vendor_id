import dash
from dash import html, dcc, Input, Output, State
import pandas as pd
import joblib
from flask import request, jsonify

# モデル読み込み
model = joblib.load("lgb_model.pkl")

# Dashアプリ初期化
app = dash.Dash(__name__)
server = app.server

# Flask APIエンドポイント
@server.route("/predict", methods=["POST"])
def predict_api():
    try:
        data = request.get_json()
        input_df = pd.DataFrame([data])
        pred = model.predict(input_df)[0]
        return jsonify({"predicted_fare": round(pred, 2)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# レイアウト
app.layout = html.Div([
    html.Div([  # ←内部レイアウト（変更せず）
        html.H1("🚕 NY タクシー料金予測アプリ", style={'textAlign': 'center'}),
        html.Div([
        dcc.Input(id='vendor_id', type='number', placeholder='Vendor ID (1 or 2)', min=1, step=1),
        html.Div(id='vendor_id-error', style={'color': 'red', 'fontSize': '12px'}),

        dcc.Input(id='pickup_id', type='number', placeholder='Pickup Location ID (1~265)'),
        html.Div(id='pickup_id-error', style={'color': 'red', 'fontSize': '12px'}),

        dcc.Input(id='dropoff_id', type='number', placeholder='Dropoff Location ID (1~265)'),
        html.Div(id='dropoff_id-error', style={'color': 'red', 'fontSize': '12px'}),

        dcc.Input(id='weekday', type='number', placeholder='Weekday (0=Mon)', min=0, max=6),
        html.Div(id='weekday-error', style={'color': 'red', 'fontSize': '12px'}),

        dcc.Input(id='time_of_day', type='number', placeholder='Time of Day (0:morning~3:midnight)'),
        html.Div(id='time_of_day-error', style={'color': 'red', 'fontSize': '12px'}),

        dcc.Input(id='passenger_count', type='number', placeholder='Passenger Count (1~6)', min=1),
        html.Div(id='passenger_count-error', style={'color': 'red', 'fontSize': '12px'}),

        html.Button('予測する', id='predict-button', n_clicks=0,
                    style={'marginTop': '10px', 'padding': '10px', 'fontSize': '16px'}),
        html.Div(id='output', style={'marginTop': '20px', 'fontWeight': 'bold'})
    ], style={
            'backgroundColor': 'yellow',
            'padding': '30px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
            'display': 'flex',
            'flexDirection': 'column',
            'gap': '12px',
            'width': '70%' ,
            'margin': 'auto'
        })
    ], style={  # 内側レイアウトのスタイル
        'display': 'flex',
        'flexDirection': 'column',
        'gap': '10px',
        'width': '1000px',
        'margin': 'auto',
        'padding': '20px',
        'backgroundColor': '#f0f8ff',
        'borderRadius': '10px',
        'boxShadow': '0px 0px 10px rgba(0, 0, 0, 0.1)',
        'minHeight': '100vh'
    })
], style={  # ← 外側のwrapperに背景色を設定
    'backgroundColor': '#e6f2ff',  # ← 全体背景（例：淡いブルー）
    'minHeight': '100vh',          # ← 全画面の高さを確保
    'padding': '30px'              # ← 余白もつけるとバランス良く見えます
})


# 各入力欄のリアルタイムバリデーション
@app.callback(Output('vendor_id-error', 'children'), Input('vendor_id', 'value'))
def validate_vendor_id(v):
    if v is None:
        return "Vendor ID を入力してください。"
    if v not in [1, 2]:
        return "Vendor ID は 1 または 2 を入力してください。"
    return ""

@app.callback(Output('pickup_id-error', 'children'), Input('pickup_id', 'value'))
def validate_pickup_id(v):
    if v is None:
        return "Pickup Location ID を入力してください。"
    if not (1 <= v <= 265):
        return "Pickup Location ID は 1 ～ 265 の範囲で入力してください。"
    return ""

@app.callback(Output('dropoff_id-error', 'children'), Input('dropoff_id', 'value'))
def validate_dropoff_id(v):
    if v is None:
        return "Dropoff Location ID を入力してください。"
    if not (1 <= v <= 265):
        return "Dropoff Location ID は 1 ～ 265 の範囲で入力してください。"
    return ""

@app.callback(Output('weekday-error', 'children'), Input('weekday', 'value'))
def validate_weekday(v):
    if v is None:
        return "曜日を入力してください。"
    if v not in list(range(7)):
        return "曜日は 0（Mon）～ 6（Sun）で入力してください。"
    return ""

@app.callback(Output('time_of_day-error', 'children'), Input('time_of_day', 'value'))
def validate_time_of_day(v):
    if v is None:
        return "時間帯を入力してください。"
    if not (0 <= v <= 3):
        return "時間帯は 0 ～ 3 の間で入力してください。"
    return ""

@app.callback(Output('passenger_count-error', 'children'), Input('passenger_count', 'value'))
def validate_passenger_count(v):
    if v is None:
        return "乗客数を入力してください。"
    if v < 1:
        return "乗客数は 1 以上を入力してください。"
    return ""

# 予測ボタン押下時の処理
@app.callback(
    Output('output', 'children'),
    Input('predict-button', 'n_clicks'),
    State('vendor_id', 'value'),
    State('pickup_id', 'value'),
    State('dropoff_id', 'value'),
    State('weekday', 'value'),
    State('time_of_day', 'value'),
    State('passenger_count', 'value')
)
def predict(n_clicks, vendor_id, pickup_id, dropoff_id, weekday, time_of_day, passenger_count):
    if n_clicks == 0:
        return ""

    # サーバー側でも念のためバリデーション
    if vendor_id not in [1, 2]:
        return "エラー: Vendor ID は 1 または 2 を入力してください。"
    if pickup_id is None or not (1 <= pickup_id <= 265):
        return "エラー: Pickup Location ID は 1 ～ 265 の範囲で入力してください。"
    if dropoff_id is None or not (1 <= dropoff_id <= 265):
        return "エラー: Dropoff Location ID は 1 ～ 265 の範囲で入力してください。"
    if weekday is None or weekday not in range(7):
        return "エラー: 曜日は 0～6 を入力してください。"
    if time_of_day is None or not (0 <= time_of_day <= 3):
        return "エラー: 時間帯は 0～3 の範囲で入力してください。"
    if passenger_count is None or passenger_count < 1:
        return "エラー: 乗客数は 1 以上を入力してください。"

    try:
        input_data = pd.DataFrame([{
            "vendor_id": vendor_id,
            "pickup_location_id_int": pickup_id,
            "dropoff_location_id_int": dropoff_id,
            "weekday": weekday,
            "time_of_day": time_of_day,
            "passenger_count": passenger_count
        }])

        pred = model.predict(input_data)[0]
        return f"予測された料金は ${round(pred, 2)} です。"
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

# アプリ起動
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8050)
