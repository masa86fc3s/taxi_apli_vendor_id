import pandas as pd
import dash
from dash import html, dcc
import plotly.express as px
from dash.dependencies import Input, Output

# データ読み込み
df = pd.read_csv("taxi_apli_vendor_id.csv")
df["date"] = pd.to_datetime(df["date"])

# アプリの初期化
app = dash.Dash(__name__)
app.title = "タクシー可視化ダッシュボード"

# レイアウト定義（背景色を薄い青に設定）
app.layout = html.Div(style={
    'backgroundColor': '#e6f2ff',  # ← ここが背景色の設定
    'padding': '30px',
    'fontFamily': 'Arial'
}, children=[
    html.H1(
        "タクシーデータ可視化ダッシュボード",
        style={'textAlign': 'center', 'color': '#444'}
    ),

    html.Div([
        html.Label("会社を選択:", style={'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='company-dropdown',
            options=[{"label": c, "value": c} for c in df["company"].unique()],
            value=df["company"].unique()[0],
            clearable=False,
            style={'width': '300px'}
        ),
    ], style={'marginBottom': '30px'}),

    dcc.Graph(id='trip-graph')
])

# コールバック
@app.callback(
    Output("trip-graph", "figure"),
    Input("company-dropdown", "value")
)
def update_graph(selected_company):
    filtered_df = df[df["company"] == selected_company]
    fig = px.line(
        filtered_df,
        x="date",
        y="trip_count",
        title=f"{selected_company} の乗車数推移",
        template="plotly_white"
    )
    fig.update_layout(
        title={'x': 0.5},
        xaxis_title="日付",
        yaxis_title="乗車数",
        margin=dict(l=40, r=40, t=50, b=40),
    )
    return fig

# 実行
if __name__ == "__main__":
    app.run_server(debug=True)
