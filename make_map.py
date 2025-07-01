import folium
import pandas as pd
import json
from shapely.geometry import shape, mapping
from shapely.ops import transform
import pyproj

MAJOR_CITIES = [
    'Kyiv','Kharkiv','Odesa','Dnipro','Donetsk','Lviv','Zaporizhzhia',
    'Kryvyi Rih','Mykolaiv','Mariupol','Vinnytsia','Kherson',
    'Poltava','Sumy','Chernihiv','Cherkasy','Chernivtsi',
    'Rivne','Ternopil','Uzhhorod','Lutsk','Ivano-Frankivsk'
]

# 1) Дані по атаках і координатах
attacks = pd.read_csv('attacks_history.csv', parse_dates=['date'])
coords  = pd.read_csv('city_coords.csv')

# 2) Фільтруємо по великих містах
attacks = attacks[attacks['city'].isin(MAJOR_CITIES)]
coords  = coords[coords['city'].isin(MAJOR_CITIES)]

# 3) Підрахунок атак
counts = attacks.groupby('city').size().rename('count').reset_index()
df = coords.merge(counts, on='city', how='left').fillna({'count':0})

# 4) Створюємо карту
m = folium.Map(location=[48.5, 31.5], zoom_start=6)

# 5) Накладаємо кордони областей з локального файлу
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

# (Якщо є локальний фронт—KMZ треба спочатку конвертувати в GeoJSON.
# Покажемо буфер навколо кордонів областей як приклад:)
# 6) Приклад буфера довкола всієї області (20 км)
# … (цей блок можна тимчасово пропустити)

# 7) Додаємо маркери міст
for _, r in df.iterrows():
    if r['count'] > 0:
        folium.CircleMarker(
            location=[r.latitude, r.longitude],
            radius=5 + r['count'],
            color='blue',
            fill=True, fill_opacity=0.6,
            tooltip=f"{r['city']}: {int(r['count'])} attacks"
        ).add_to(m)

# 8) Легенда
folium.LayerControl().add_to(m)

# 9) Зберігаємо
m.save('attack_map.html')
print("✅ Карта з областями і містами збережена в attack_map.html")
