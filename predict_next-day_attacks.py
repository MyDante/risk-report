import pandas as pd
import joblib
from datetime import datetime

def main():
    # 1) Завантажуємо датасет з фічами
    df = pd.read_csv('model_dataset.csv', parse_dates=['date'])

    # 2) Визначаємо останню дату в датасеті
    last_date = df['date'].max()
    today_df = df[df['date'] == last_date].copy()

    # 3) Підвантажуємо модель і LabelEncoder
    model, le = joblib.load('attack_multimodel.pkl')

    # 4) Формуємо матрицю фіч для прогнозу
    feature_cols = [c for c in df.columns if c.endswith('d')]
    X_today = today_df[feature_cols]

    # 5) Робимо прогноз ймовірностей для кожного класу
    probs = model.predict_proba(X_today)  # (n_cities, n_classes)
    classes = le.inverse_transform(range(len(le.classes_)))

    # 6) Формуємо DataFrame й додаємо загальну P(attack) = 1 – P(none)
    proba_df = pd.DataFrame(probs, columns=classes, index=today_df['city'])
    if 'none' in proba_df:
        proba_df['p_attack'] = 1 - proba_df['none']
    else:
        proba_df['p_attack'] = proba_df.sum(axis=1)

    # 7) Відбираємо топ-10 міст за ймовірністю атаки
    top10 = proba_df.sort_values('p_attack', ascending=False).head(10).copy()

    # 8) Форматуємо всі ймовірності у відсотки
    for col in classes:
        top10[col] = (top10[col] * 100).round(1).astype(str) + '%'
    top10['p_attack'] = (top10['p_attack'] * 100).round(1).astype(str) + '%'

    # 9) Зберігаємо результати у CSV та HTML
    date_str  = last_date.strftime('%Y-%m-%d')
    csv_name  = f'predictions_{date_str}.csv'
    html_name = f'predictions_{date_str}.html'

    out = top10.reset_index().rename(columns={'index':'city'})
    out[['city','p_attack'] + classes.tolist()].to_csv(csv_name, index=False, encoding='utf-8')
    out[['city','p_attack'] + classes.tolist()].to_html(html_name, index=False)

    print(f"✅ Прогноз збережено у {csv_name} та {html_name}")

if __name__ == '__main__':
    main()
