import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score
import joblib

def main():
    # 1) Завантажуємо модельний датасет
    df = pd.read_csv('model_dataset.csv', parse_dates=['date'])
    # Переконаємось, що y_next існує та приводимо в бінарний формат
    # 1 – якщо кількість атак наступного дня ≥1, інакше 0
    df['y_next_bin'] = (df['y_next'] >= 1).astype(int)

    # 2) Вибір ознак і таргету
    features = [
        'cnt_1d','cnt_7d','cnt_30d',
        'sig_1d','sig_7d','sig_30d',
        'latitude','longitude'
    ]
    X = df[features]
    y = df['y_next_bin']

    # 3) Розбиваємо на train/test за датою
    split_date = pd.Timestamp('2025-01-01')
    train_mask = df['date'] < split_date
    X_train, X_test = X[train_mask], X[~train_mask]
    y_train, y_test = y[train_mask], y[~train_mask]

    # 4) Навчаємо XGBoost-класіфікатор
    model = XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        eval_metric='auc'
    )
    model.fit(X_train, y_train)

    # 5) Прогноз ймовірностей для класу “1”
    probs = model.predict_proba(X_test)  # shape = (n_samples, 2)
    preds = probs[:, 1]                  # ймовірність атаки

    # 6) Обчислюємо ROC-AUC
    auc = roc_auc_score(y_test, preds)
    print(f"Test ROC-AUC: {auc:.3f}")

    # 7) Зберігаємо модель
    joblib.dump(model, 'attack_predictor.pkl')
    print("✅ Модель збережена в attack_predictor.pkl")

if __name__ == "__main__":
    main()
