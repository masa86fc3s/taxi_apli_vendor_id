import pandas as pd

import dash
from dash import html, dcc
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

# データ読み込み
df = pd.read_csv("taxi_apli_vendor_id.csv")
df["date"] = pd.to_datetime(df["date"])

# アプリの初期化
app = dash.Dash(__name__)

# レイアウト定義
app.layout = html.Div([
    html.H1("タクシーデータ可視化ダッシュボード"),

    dcc.Dropdown(
        id='company-dropdown',
        options=[{"label": c, "value": c} for c in df["company"].unique()],
        value=df["company"].unique()[0],
        clearable=False
    ),

    dcc.Graph(id='trip-graph')
])

# コールバック（ドロップダウンの選択に応じてグラフ更新）
@app.callback(
    Output("trip-graph", "figure"),
    Input("company-dropdown", "value")
)
def update_graph(selected_company):
    filtered_df = df[df["company"] == selected_company]
    fig = px.line(filtered_df, x="date", y="trip_count", title=f"{selected_company} の乗車数推移")
    return fig

# サーバー実行
if __name__ == "__main__":
    app.run_server(debug=True)
