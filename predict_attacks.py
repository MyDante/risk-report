import pandas as pd
import joblib
from datetime import datetime

def main():
    # 1) Завантажуємо модельований датасет
    df = pd.read_csv('model_dataset.csv', parse_dates=['date'])
    
    # 2) Визначаємо останню дату (сьогодні)
    last_date = df['date'].max()
    today_df = df[df['date'] == last_date].copy()
    
    # 3) Завантажуємо модель
    model = joblib.load('attack_predictor.pkl')
    
    # 4) Готуємо фічі
    features = [
        'cnt_1d','cnt_7d','cnt_30d',
        'sig_1d','sig_7d','sig_30d',
        'latitude','longitude'
    ]
    X_today = today_df[features]
    
    # 5) Генеруємо прогноз
    today_df['risk_proba'] = model.predict_proba(X_today)[:,1]
    
    # 6) Відсортуємо за ймовірністю
    report = today_df[['city','risk_proba']].sort_values('risk_proba', ascending=False)
    report['risk_proba'] = (report['risk_proba']*100).round(1).astype(str) + '%'
    
    # 7) Збережемо в CSV та HTML
    today_str = last_date.strftime('%Y-%m-%d')
    csv_name = f'predictions_{today_str}.csv'
    html_name = f'predictions_{today_str}.html'
    
    report.to_csv(csv_name, index=False, encoding='utf-8')
    report.to_html(html_name, index=False)
    
    print(f"✅ Прогноз збережено у {csv_name} та {html_name}")

if __name__ == '__main__':
    main()
