import pandas as pd
import joblib
from datetime import datetime

def main():
    # 1) Завантажуємо модельний датасет
    df = pd.read_csv('model_dataset.csv', parse_dates=['date'])

    # 2) Визначаємо "сьогодні" (UTC) у форматі YYYY-MM-DD
    date_str = datetime.utcnow().strftime('%Y-%m-%d')

    # 3) Беремо дані саме за останню дату в датасеті
    last_data_date = df['date'].max()
    today_df = df[df['date'] == last_data_date].copy()

    # 4) Завантажуємо модель
    model = joblib.load('attack_predictor.pkl')

    # 5) Готуємо фічі для прогнозу
    features = [
        'cnt_1d','cnt_7d','cnt_30d',
        'sig_1d','sig_7d','sig_30d',
        'latitude','longitude'
    ]
    X_today = today_df[features]

    # 6) Робимо прогноз ймовірності атаки
    today_df['risk_proba'] = model.predict_proba(X_today)[:,1]

    # 7) Форматуємо результат
    report = today_df[['city','risk_proba']].sort_values('risk_proba', ascending=False)
    report['risk_proba'] = (report['risk_proba']*100).round(1).astype(str) + '%'

    # 8) Зберігаємо під іменем за сьогоднішньою датою
    csv_name  = f'predictions_{date_str}.csv'
    html_name = f'predictions_{date_str}.html'
    report.to_csv(csv_name, index=False, encoding='utf-8')
    report.to_html(html_name, index=False)

    print(f"✅ Прогноз збережено у {csv_name} та {html_name}")

if __name__ == '__main__':
    main()
