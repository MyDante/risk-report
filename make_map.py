import folium
import pandas as pd
import json
from datetime import datetime, timedelta
from math import sqrt

MAJOR_CITIES = [ ... ]  # твій список

# 1) Зчитаємо історію атак
df_att = pd.read_csv('attacks_history.csv', parse_dates=['date'])

# 2) Фільтруємо тільки останні 7 днів
today = datetime.utcnow().date()
cutoff = today - timedelta(days=7)
recent = df_att[df_att['date'].dt.date >= cutoff]

# 3) Відбираємо лише великі міста і рахуємо події
recent = recent[recent['city'].isin(MAJOR_CITIES)]
counts = recent.groupby('city').size().rename('count').reset_index()

# 4) Зчитаємо координати великих міст
coords = pd.read_csv('city_coords.csv')
coords = coords[coords['city'].isin(MAJOR_CITIES)]

df = coords.merge(counts, on='city', how='left').fillna({'count':0})

# 5) Налаштовуємо карту
m = folium.Map(location=[48.5, 31.5], zoom_start=6)

# 6) Класичні кордони областей (локальний файл)
with open('oblast.geojson','r',encoding='utf-8') as f:
    oblasts = json.load(f)
folium.GeoJson(oblasts, style_function=lambda f: {
    'fillColor':'none','color':'black','weight':1
}).add_to(m)

# 7) Масштабування радіусу:
max_count = df['count'].max()
# AB: якщо max_count==0, поставимо хоча б 1, щоб не ділити на нуль
if max_count == 0:
    max_count = 1

# 8) Додаємо маркери
for _, r in df.iterrows():
    c = int(r['count'])
    if c>0:
        # радіус: sqrt(count/max_count) * 30px
        radius = sqrt(c / max_count) * 30
        folium.CircleMarker(
            location=[r.latitude, r.longitude],
            radius=radius,
            color='crimson',
            fill=True, fill_opacity=0.6,
            tooltip=f"{r['city']}: {c} attacks last 7d"
        ).add_to(m)

# 9) Легенда: можна у заголовку або як HTML
legend_html = f'''
  <div style="position: fixed;
              bottom: 50px; left: 50px; width: 180px; height: 90px;
              background: white; border:2px solid grey; z-index:9999;
              font-size:14px;">
    &nbsp;<b>Attacks (7d)</b><br>
    &nbsp;● = fewer &nbsp;(1)<br>
    &nbsp;● = more &nbsp;({max_count})
  </div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# 10) Зберігаємо
m.save('attack_map.html')
print("✅ Карта оновлена — точки за останні 7 днів, радіус пропорційний частоті.")
