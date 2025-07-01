import folium
import pandas as pd
import json
from datetime import timedelta
from math import sqrt

# 1) Завантажуємо історію атак
df_att = pd.read_csv('attacks_history.csv', parse_dates=['date'])

# 2) Знаходимо останню дату та беремо події за останні 7 днів
last_data_date = df_att['date'].max().date()
cutoff = last_data_date - timedelta(days=7)
recent = df_att[df_att['date'].dt.date >= cutoff]

# ===== ДІАГНОСТИКА ВІДСУТНІХ КООРДИНАТ =====
# Які у нас міста в recent?
attacked = recent['city'].unique().tolist()

# Зчитуємо наявні в city_coords.csv
coords = pd.read_csv('city_coords.csv')

# Різниця — це міста без координат
missing = set(attacked) - set(coords['city'])
print("Cities missing coords:", missing)
# ==========================================

# 3) Тепер фільтруємо coords і далі будуємо карту…
coords = coords[coords['city'].isin(attacked)]

# 4) Порахуймо, скільки атак було в кожному місті
counts = (
    recent
      .groupby('city')
      .size()
      .rename('count')
      .reset_index()
)

# 5) Зчитаємо координати лише атакованих міст
coords = pd.read_csv('city_coords.csv')
# Динамічно беремо ті міста, де count>0
attacked = counts['city'].unique().tolist()
coords = coords[coords['city'].isin(attacked)]

# 6) Merge coords + counts
df = coords.merge(counts, on='city', how='left').fillna({'count': 0})

# 7) Створюємо карту
m = folium.Map(location=[48.5, 31.5], zoom_start=6)

# 8) Додаємо кордони областей (локальний файл)
with open('oblast.geojson', 'r', encoding='utf-8') as f:
    oblasts = json.load(f)

folium.GeoJson(
    oblasts,
    style_function=lambda feat: {
        'fillColor': 'none', 'color': 'black', 'weight': 1
    }
).add_to(m)

# 9) Масштаб радіусів: на найбільше число — 30px
max_count = int(df['count'].max()) or 1

for _, r in df.iterrows():
    c = int(r['count'])
    if c > 0:
        radius = sqrt(c / max_count) * 30
        folium.CircleMarker(
            location=[r.latitude, r.longitude],
            radius=radius,
            color='crimson',
            fill=True, fill_opacity=0.6,
            tooltip=f"{r['city']}: {c} attacks (last 7d)"
        ).add_to(m)

# 10) Легенда
legend_html = f'''
<div style="
    position: fixed; bottom: 50px; left: 50px;
    width: 180px; height: 80px;
    background: white; border:2px solid grey;
    font-size:14px; padding:8px; z-index:9999;">
  <b>Attacks (7d)</b><br>
  <i style="color:crimson">●</i> = fewer (1)<br>
  <i style="color:crimson; font-size:20px">●</i> = more ({max_count})
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# 11) Зберігаємо файл
m.save('attack_map.html')
print("✅ Карта оновлена: attack_map.html (усі атаковані міста за 7 днів)")
