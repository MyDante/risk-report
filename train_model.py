import pandas as pd
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, log_loss
import joblib

def main():
    # 1) Завантажуємо фічі з типами атак
    df = pd.read_csv('model_dataset.csv', parse_dates=['date'])
    df = df.dropna(subset=['next_type'])

    # 2) Підготовка X та y
    feature_cols = [c for c in df.columns if c.endswith('d')]
    X = df[feature_cols]

    le = LabelEncoder()
    y = le.fit_transform(df['next_type'])

    # 3) Спліт по даті
    split_date = pd.Timestamp('2025-01-01')
    train_mask = df['date'] < split_date
    X_train, X_test = X[train_mask], X[~train_mask]
    y_train, y_test = y[train_mask], y[~train_mask]

    # 4) Навчаємо мультикласовий XGBoost
    model = XGBClassifier(
        objective='multi:softprob',
        num_class=len(le.classes_),
        eval_metric='mlogloss',
        n_estimators=200,
        max_depth=4,
        learning_rate=0.1
    )
    model.fit(X_train, y_train)

    # 5) Прогноз і оцінка
    probs = model.predict_proba(X_test)       # shape = (n_samples, n_classes)
    preds = probs.argmax(axis=1)

    acc = accuracy_score(y_test, preds)
    # Щоб log_loss спрацював, передаємо повний список міток:
    labels = list(range(len(le.classes_)))
    loss = log_loss(y_test, probs, labels=labels)

    print(f"Test Accuracy: {acc:.3f}")
    print(f"Test LogLoss:  {loss:.3f}")

    # 6) Зберігаємо модель і енкодер
    joblib.dump((model, le), 'attack_multimodel.pkl')
    print("✅ Модель і енкодер збережено в attack_multimodel.pkl")
    print("Classes:", list(le.classes_))

if __name__ == "__main__":
    main()
