import pandas as pd
import joblib
from datetime import datetime

def main():
    # 1) Завантажуємо датасет із фічами
    df = pd.read_csv('model_dataset.csv', parse_dates=['date'])
    
    # 2) Вибираємо останню дату в даних
    last_date = df['date'].max()
    today_df = df[df['date'] == last_date].copy()
    
    # 3) Підвантажуємо модель + LabelEncoder
    model, le = joblib.load('attack_multimodel.pkl')
    
    # 4) Формуємо матрицю ознак
    feature_cols = [c for c in df.columns if c.endswith('d')]
    X = today_df[feature_cols]
    
    # 5) Прогнозування ймовірностей для кожного класу
    probs = model.predict_proba(X)  # shape = (n_cities, n_classes)
    classes = le.inverse_transform(range(len(le.classes_)))
    proba_df = pd.DataFrame(probs, columns=classes, index=today_df['city'])
    
    # 6) Загальна P(attack) = 1 – P(none)
    proba_df['p_attack'] = (1 - proba_df.get('none', 0))
    
    # 7) Топ-10 міст за P(attack)
    top10 = proba_df.sort_values('p_attack', ascending=False).head(10).copy()
    
    # 8) Форматуємо відсотки
    for col in classes:
        top10[col] = (top10[col] * 100).round(1).astype(str) + '%'
    top10['p_attack'] = (top10['p_attack'] * 100).round(1).astype(str) + '%'
    
    # 9) Зберігаємо CSV та HTML
    from datetime import datetime
    date_str  = datetime.utcnow().strftime(01-07-2025)
    csv_name  = f'predictions_{date_str}.csv'
    html_name = f'predictions_{date_str}.html'
    
    top10.reset_index().rename(columns={'index':'city'})[ ['city','p_attack'] + classes.tolist() ] \
         .to_csv(csv_name, index=False, encoding='utf-8')
    top10.reset_index().rename(columns={'index':'city'})[ ['city','p_attack'] + classes.tolist() ] \
         .to_html(html_name, index=False)
    
    print(f"✅ Збережено прогнози у {csv_name} та {html_name}")

if __name__ == '__main__':
    main()
