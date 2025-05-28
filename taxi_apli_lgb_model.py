import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
import numpy as np
import lightgbm as lgb
import optuna
from sklearn.model_selection import KFold


# データ読み込み
df = pd.read_csv("taxi_data_log.csv")

# 説明変数と目的変数
features = [
    "vendor_id", "pickup_location_id_int", "dropoff_location_id_int",
    "weekday", "time_of_day", "passenger_count"
]
target = "fare_amount"

X = df[features]
y = df[target]

def objective(trial):
    params = {
        'objective': 'regression',
        'metric': 'rmse',
        'boosting_type': 'gbdt',
        'verbosity': -1,
        'random_seed': 0,
        'lambda_l1': trial.suggest_float('lambda_l1', 1e-8, 10.0, log=True),
        'lambda_l2': trial.suggest_float('lambda_l2', 1e-8, 10.0, log=True),
        'num_leaves': trial.suggest_int('num_leaves', 20, 128),
        'feature_fraction': trial.suggest_float('feature_fraction', 0.4, 0.9),
        'bagging_fraction': trial.suggest_float('bagging_fraction', 0.4, 0.8),
        'bagging_freq': trial.suggest_int('bagging_freq', 1, 5),
        'min_child_samples': trial.suggest_int('min_child_samples', 10, 100),
        'device': 'gpu'
    }

    kf = KFold(n_splits=3, shuffle=True, random_state=0)
    rmse_list = []

    for train_idx, valid_idx in kf.split(X):
        X_train, X_valid = X.iloc[train_idx], X.iloc[valid_idx]
        y_train, y_valid = y.iloc[train_idx], y.iloc[valid_idx]

        lgb_train = lgb.Dataset(X_train, y_train)
        lgb_valid = lgb.Dataset(X_valid, y_valid, reference=lgb_train)

        model = lgb.train(
            params,
            lgb_train,
            valid_sets=[lgb_valid],
            num_boost_round=500,
            callbacks=[
                lgb.early_stopping(stopping_rounds=30),
                lgb.log_evaluation(0)
            ]
        )

        y_pred = model.predict(X_valid, num_iteration=model.best_iteration)
        rmse = np.sqrt(mean_squared_error(y_valid, y_pred))  # expなしで統一
        rmse_list.append(rmse)

    return np.mean(rmse_list)


# --- Optunaによるチューニング ---
study = optuna.create_study(direction='minimize')
study.optimize(objective, n_trials=20)

print(f"\n✅ Best trial RMSE: {study.best_value:.4f}")
print("Best parameters:")
for key, value in study.best_trial.params.items():
    print(f"  {key}: {value}")

# --- 自動再学習・全データで評価 ---
best_params = study.best_trial.params
best_params.update({
    'objective': 'regression',
    'metric': 'rmse',
    'boosting_type': 'gbdt',
    'verbosity': -1,
    'random_seed': 0,
    'device': 'gpu'  # GPU使う場合
})

X_full = df[features]
y_full = df[target]
lgb_train_full = lgb.Dataset(X_full, y_full)

final_model = lgb.train(
    best_params,
    lgb_train_full,
    num_boost_round=500
)

# 再学習モデルによる予測とRMSE評価（exp()なし）
y_pred = final_model.predict(X_full)
mse = mean_squared_error(y_full, y_pred)
rmse = mse ** 0.5
print(f"\n✅ Full data training RMSE: {rmse:.4f} ドル")


# モデル保存（LightGBM方式）
joblib.dump(final_model,"lgb_model.pkl")
print("✅ モデルを 'lgb_model.pkl' として保存しました。")

