import pandas as pd
from datetime import datetime

# 1) Завантажуємо дані з попереднього кроку
df = pd.read_csv('news_with_signals.csv')

# 2) Групуємо по містах
group = df.groupby('city').agg(
    events = ('text', 'count'),
    signals = ('preparation_signal', 'sum')
).reset_index()

# 3) Розрахунок простого індексу ризику
#    risk_score = events + 2 * signals  (сигнал важливіший за подію)
group['risk_score'] = group['events'] + 2 * group['signals']

# 4) Визначаємо рівні ризику
def risk_level(score):
    if score >= 4: return 'Високий'
    if score >= 2: return 'Середній'
    return 'Низький'

group['risk_level'] = group['risk_score'].apply(risk_level)

# 5) Сортуємо за ризиком
report = group.sort_values(['risk_score','signals','events'], ascending=False)

# 6) Вивід у термінал
print(f"\n🗓 Щоденний звіт – {datetime.now().strftime('%Y-%m-%d')}\n")
print(report[['city','events','signals','risk_score','risk_level']].to_string(index=False))

# 7) Збереження в CSV та HTML
report.to_csv('daily_risk_report.csv', index=False, encoding='utf-8')
report.to_html('daily_risk_report.html', index=False)

print("\n✅ Звіт збережено у файлах:")
print("   • daily_risk_report.csv")
print("   • daily_risk_report.html")
