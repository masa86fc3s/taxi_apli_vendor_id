import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib

# データ読み込み
df = pd.read_csv("taxi_data_log.csv", nrows=500000)



# 説明変数と目的変数
features = [
    "vendor_id", "pickup_location_id_int", "dropoff_location_id_int",
    "weekday", "time_of_day", "passenger_count"
]
target = "fare_amount"

X = df[features]
y = df[target]

# 学習・テストに分割
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# モデル構築
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 評価
preds = model.predict(X_test)
mse = mean_squared_error(y_test, preds)
rmse = mse ** 0.5
print(f"RMSE: {rmse:.2f}")

# モデル保存
joblib.dump(model, "fare_predictor.pkl")
print("モデルを 'fare_predictor.pkl' として保存しました。")
