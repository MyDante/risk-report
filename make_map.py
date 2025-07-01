import folium
import pandas as pd
import json
from datetime import timedelta
from math import sqrt

# ---------------------------------------
# 0) Перелік ключових міст (має бути тут!)
MAJOR_CITIES = [
    'Kyiv','Kharkiv','Odesa','Dnipro','Donetsk','Lviv','Zaporizhzhia',
    'Kryvyi Rih','Mykolaiv','Mariupol','Vinnytsia','Kherson',
    'Poltava','Sumy','Chernihiv','Cherkasy','Chernivtsi',
    'Rivne','Ternopil','Uzhhorod','Lutsk','Ivano-Frankivsk'
]
# ---------------------------------------

# 1) Завантажуємо історію атак
df_att = pd.read_csv('attacks_history.csv', parse_dates=['date'])

# 2) Знаходимо останню дату в датасеті та відлічуємо 7 днів назад
last_data_date = df_att['date'].max().date()
cutoff = last_data_date - timedelta(days=7)

# 3) Фільтруємо події за останні 7 днів
recent = df_att[df_att['date'].dt.date >= cutoff]

# 4) Фільтруємо виключно великі міста і рахуємо кількість атак
recent = recent[recent['city'].isin(MAJOR_CITIES)]
counts = recent.groupby('city').size().rename('count').reset_index()

# 5) Завантажуємо координати міст та мерджимо
coords = pd.read_csv('city_coords.csv')
coords = coords[coords['city'].isin(MAJOR_CITIES)]
df = coords.merge(counts, on='city', how='left').fillna({'count':0})

# 6) Ініціалізуємо карту
m = folium.Map(location=[48.5, 31.5], zoom_start=6)

# 7) Додаємо кордони областей з локального файлу
with open('oblast.geojson', 'r', encoding='utf-8') as f:
    oblasts = json.load(f)

folium.GeoJson(
    oblasts,
    style_function=lambda feat: {
        'fillColor': 'none',
        'color': 'black',
        'weight': 1
    }
).add_to(m)

# 8) Масштабування радіусів кіл за count
max_count = int(df['count'].max()) or 1  # щоб не було ділення на нуль

for _, r in df.iterrows():
    c = int(r['count'])
    if c > 0:
        # радіус: sqrt(count/max_count) * 30
        radius = sqrt(c / max_count) * 30
        folium.CircleMarker(
            location=[r.latitude, r.longitude],
            radius=radius,
            color='crimson',
            fill=True, fill_opacity=0.6,
            tooltip=f"{r['city']}: {c} attacks (last 7d)"
        ).add_to(m)

# 9) Додаємо контрол шарів (якщо потрібен)
folium.LayerControl().add_to(m)

# 10) Зберігаємо результат
m.save('attack_map.html')
print("✅ Карта оновлена — attack_map.html (останні 7 днів, пропорційні кола)")
