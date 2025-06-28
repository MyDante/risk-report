import pandas as pd
import joblib

def main():
    # 1) Завантажуємо модельований датасет
    df = pd.read_csv('model_dataset.csv', parse_dates=['date'])
    
    # 2) Обираємо останню дату
    last_date = df['date'].max()
    today_df = df[df['date'] == last_date].copy()
    
    # 3) Завантажуємо навчену модель
    model = joblib.load('attack_predictor.pkl')
    
    # 4) Підготовка фіч
    features = [
        'cnt_1d','cnt_7d','cnt_30d',
        'sig_1d','sig_7d','sig_30d',
        'latitude','longitude'
    ]
    X_today = today_df[features]
    
    # 5) Прогноз
    today_df['risk_proba'] = model.predict_proba(X_today)[:,1]
    
    # 6) Форматуємо результат
    report = (today_df[['city','risk_proba']]
              .sort_values('risk_proba', ascending=False))
    report['risk_proba'] = (report['risk_proba']*100).round(1).astype(str) + '%'
    
    # 7) Зберігаємо
    date_str = last_date.strftime('%Y-%m-%d')
    report.to_csv(f'predictions_{date_str}.csv', index=False)
    report.to_html(f'predictions_{date_str}.html', index=False)
    print(f"✅ Прогноз збережено у predictions_{date_str}.csv/html")

if __name__ == '__main__':
    main()
