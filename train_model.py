import pandas as pd
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, log_loss
import joblib

def main():
    # 1) Завантажуємо датасет з фічами по типах
    df = pd.read_csv('model_dataset.csv', parse_dates=['date'])
    df = df.dropna(subset=['next_type'])  # прибираємо дати без мітки

    # 2) Вибираємо фічі та таргет
    # всі стовпці, що закінчуються на '_d' (rolling-ознаки)
    feature_cols = [c for c in df.columns if c.endswith('d')]
    X = df[feature_cols]
    # таргет — next_type (наприклад: 'missile', 'drone', 'none' тощо)
    le = LabelEncoder()
    y = le.fit_transform(df['next_type'])

    # 3) Спліт по часу: train до 2025-01-01, test з 2025-01-01
    split_date = pd.Timestamp('2025-01-01')
    train_mask = df['date'] < split_date
    X_train, X_test = X[train_mask], X[~train_mask]
    y_train, y_test = y[train_mask], y[~train_mask]

    # 4) Навчаємо XGBoost для мультикласу
    model = XGBClassifier(
        objective='multi:softprob',
        num_class=len(le.classes_),
        eval_metric='mlogloss',
        n_estimators=200,
        max_depth=4,
        learning_rate=0.1
    )
    model.fit(X_train, y_train)

    # 5) Оцінюємо на тесті
    probs = model.predict_proba(X_test)
    preds = probs.argmax(axis=1)
    acc = accuracy_score(y_test, preds)
    loss = log_loss(y_test, probs)
    print(f"Test Accuracy: {acc:.3f}")
    print(f"Test LogLoss:  {loss:.3f}")

    # 6) Зберігаємо модель та LabelEncoder
    joblib.dump((model, le), 'attack_multimodel.pkl')
    print("✅ Модель і енкодер збережено в attack_multimodel.pkl")
    print("Classes:", list(le.classes_))

if __name__ == "__main__":
    main()
