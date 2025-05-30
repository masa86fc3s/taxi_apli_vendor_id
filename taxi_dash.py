import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import pickle

import boto3
import pickle
import io

# S3の情報
bucket_name = 'taxi-model-storage'
object_key = 'lgb_model.pkl'

# S3クライアント作成
s3 = boto3.client('s3', region_name='ap-southeast-2') 

# S3オブジェクトをメモリに読み込む
response = s3.get_object(Bucket=bucket_name, Key=object_key)
body = response['Body'].read()

# メモリ上のバイナリデータをpickleでロード
model = pickle.load(io.BytesIO(body))

"""""
# モデル読み込み
with open('lgb_model.pkl', 'rb') as f:
    model = pickle.load(f)
"""

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("🚕 タクシー料金予測アプリ", style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.Label("🚗 Trip Distance (例: 2.5):"),
            html.Br(),  # 👈 改行を追加
            dcc.Input(id='trip_distance', type='number', step=0.1),
            html.Div(id='trip_distance-error', style={'color': 'red', 'fontSize': '16px'})
        ]),

        html.Div([
            html.Label("📍 Pickup Location ID (1〜265):"),
            html.Br(),  # 👈 改行を追加
            dcc.Input(id='pickup_id', type='number'),
            html.Div(id='pickup_id-error', style={'color': 'red', 'fontSize': '16px'})
        ]),

        html.Div([
            html.Label("🏁 Dropoff Location ID (1〜265):"),
            html.Br(),  # 👈 改行を追加
            dcc.Input(id='dropoff_id', type='number'),
            html.Div(id='dropoff_id-error', style={'color': 'red', 'fontSize': '16px'})
        ]),

        html.Div([
            html.Label("📆 曜日 (0=Mon〜6=Sun):"),
            html.Br(),  # 👈 改行を追加
            dcc.Input(id='weekday', type='number'),
            html.Div(id='weekday-error', style={'color': 'red', 'fontSize': '16px'})
        ]),

        html.Div([
            html.Label("⏰ 時間帯 (0=深夜, 1=朝, 2=昼, 3=夜):"),
            html.Br(),  # 👈 改行を追加
            dcc.Input(id='time_of_day', type='number'),
            html.Div(id='time_of_day-error', style={'color': 'red', 'fontSize': '16px'})
        ]),

        html.Button("予測する", id='predict-button', n_clicks=0, 
                    style={'marginTop': '20px', 'padding': '10px', 'fontSize': '16px'}),
        html.Div(id='output', style={'marginTop': '30px', 'fontWeight': 'bold'})
    ], style={
        'backgroundColor': '#fff8dc',
        'padding': '30px',
        'borderRadius': '10px',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
        'width': '60%',
        'margin': 'auto',
        'display': 'flex',
        'flexDirection': 'column',
        'alignItems': 'center',  # ← ここで中央寄せに！
        'textAlign': 'center',   # ← 子要素のテキストも中央に！
        'gap': '20px'
    })
], style={
    'backgroundColor': '#f0f8ff',
    'minHeight': '100vh',
    'padding': '50px',
    'display': 'flex',
    'flexDirection': 'column',  # 外側も縦方向
    'gap': '20px',
    'alignItems': 'center',     # 中央寄せ
    'borderRadius': '10px',
    'boxShadow': '0px 0px 10px rgba(0, 0, 0, 0.1)'
})



# バリデーション callbacks
@app.callback(Output('trip_distance-error', 'children'), Input('trip_distance', 'value'))
def validate_trip_distance(v):
    if v is None:
        return "Trip Distance を入力してください。"
    if v <= 0:
        return "正の数を入力してください。"
    return ""

@app.callback(Output('pickup_id-error', 'children'), Input('pickup_id', 'value'))
def validate_pickup_id(v):
    if v is None:
        return "Pickup ID を入力してください。"
    if not (1 <= v <= 265):
        return "1〜265の範囲で入力してください。"
    return ""

@app.callback(Output('dropoff_id-error', 'children'), Input('dropoff_id', 'value'))
def validate_dropoff_id(v):
    if v is None:
        return "Dropoff ID を入力してください。"
    if not (1 <= v <= 265):
        return "1〜265の範囲で入力してください。"
    return ""

@app.callback(Output('weekday-error', 'children'), Input('weekday', 'value'))
def validate_weekday(v):
    if v is None:
        return "曜日を入力してください。"
    if v not in range(7):
        return "0〜6の範囲で入力してください。"
    return ""

@app.callback(Output('time_of_day-error', 'children'), Input('time_of_day', 'value'))
def validate_time_of_day(v):
    if v is None:
        return "時間帯を入力してください。"
    if not (0 <= v <= 3):
        return "0〜3の範囲で入力してください。"
    return ""

# 予測処理
@app.callback(
    Output('output', 'children'),
    Input('predict-button', 'n_clicks'),
    State('trip_distance', 'value'),
    State('pickup_id', 'value'),
    State('dropoff_id', 'value'),
    State('weekday', 'value'),
    State('time_of_day', 'value')
)
def predict(n_clicks, trip_distance, pickup_id, dropoff_id, weekday, time_of_day):
    if n_clicks == 0:
        return ""

    # サーバー側で再チェック
    if trip_distance is None or trip_distance <= 0:
        return "エラー: Trip Distance は正の数を入力してください。"
    if pickup_id is None or not (1 <= pickup_id <= 265):
        return "エラー: Pickup ID は 1〜265 の範囲で入力してください。"
    if dropoff_id is None or not (1 <= dropoff_id <= 265):
        return "エラー: Dropoff ID は 1〜265 の範囲で入力してください。"
    if weekday is None or weekday not in range(7):
        return "エラー: 曜日は 0〜6 を入力してください。"
    if time_of_day is None or not (0 <= time_of_day <= 3):
        return "エラー: 時間帯は 0〜3 の範囲で入力してください。"

    try:
        input_data = pd.DataFrame([{
            "trip_distance": trip_distance,
            "pickup_location_id_int": pickup_id,
            "dropoff_location_id_int": dropoff_id,
            "weekday": weekday,
            "time_of_day": time_of_day
        }])
        pred = model.predict(input_data)[0]
        return f"💰 予測された料金は ${round(pred, 2)} です。"
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

# 実行
if __name__ == '__main__':
    app.run_server(debug=True)
