import pandas as pd

# 1) Завантажуємо історію атак
attacks = pd.read_csv('attacks_history.csv', parse_dates=['date'])
attacks['city'] = attacks['city'].str.strip()

# 2) Завантажуємо координати міст
coords = pd.read_csv('city_coords.csv')

# 3) Завантажуємо сигнали підготовки (якщо такий файл є)
try:
    signals = pd.read_csv('news_with_signals.csv', parse_dates=['date'])
    signals = signals[signals['preparation_signal'] == True]
    signals['city'] = signals['city'].str.strip()
except FileNotFoundError:
    signals = pd.DataFrame(columns=['city','date'])

# 4) Створюємо «грид» всіх міст × всіх дат
all_dates  = pd.date_range(attacks['date'].min(), attacks['date'].max(), freq='D')
all_cities = attacks['city'].unique()
grid = pd.MultiIndex.from_product([all_cities, all_dates], names=['city','date'])
df = pd.DataFrame(index=grid).reset_index()

# 5) Додаємо до гриду координати
df = df.merge(coords, on='city', how='left')

# 6) Рахуємо разом зведені таблиці атак і сигналів
att_cnt = attacks.groupby(['city','date']).size().rename('attacks').reset_index()
sig_cnt = signals.groupby(['city','date']).size().rename('signals').reset_index()

df = df.merge(att_cnt, on=['city','date'], how='left').fillna({'attacks': 0})
df = df.merge(sig_cnt, on=['city','date'], how='left').fillna({'signals': 0})

# 7) Створюємо rolling-ознаки
for w in [1, 7, 30]:
    df[f'cnt_{w}d'] = df.groupby('city')['attacks'].transform(
        lambda x: x.rolling(window=w, min_periods=1).sum()
    )
    df[f'sig_{w}d'] = df.groupby('city')['signals'].transform(
        lambda x: x.rolling(window=w, min_periods=1).sum()
    )

# 8) Цільова змінна – чи буде атака наступного дня?
df['y_next'] = df.groupby('city')['attacks'].shift(-1).fillna(0).astype(int)

# 9) Зберігаємо кінцевий датасет
out_cols = [
    'city','date','latitude','longitude',
    'cnt_1d','cnt_7d','cnt_30d',
    'sig_1d','sig_7d','sig_30d','y_next'
]
df[out_cols].to_csv('model_dataset.csv', index=False, encoding='utf-8')
print("✅ Збережено model_dataset.csv з", len(df), "рядків")
