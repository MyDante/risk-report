import folium
import pandas as pd
import requests

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

# 4) Створюємо Folium-карту
m = folium.Map(location=[48.5, 31.5], zoom_start=6)

# 5) Накладаємо кордони областей
url_oblasts = "https://raw.githubusercontent.com/leakyMirror/map-of-ukraine/master/ukraine.geojson"
oblasts = requests.get(url_oblasts).json()
folium.GeoJson(
    oblasts,
    style_function=lambda feat: {
        'fillColor': 'none',
        'color': 'black',
        'weight': 1
    }
).add_to(m)

# 6) Накладаємо лінію фронту
url_front = "https://data.humdata.org/dataset/8b4e4f4f-1ae2-46bc-bf3a3e18242b/resource/2b9ad770-6be6-46e1-9ea3-e0618fa36f13/download/ukraine_admin0_prov_lines.geojson"
front = requests.get(url_front).json()
folium.GeoJson(
    front,
    name="Front line",
    style_function=lambda feat: {
        'color': 'red',
        'weight': 2
    }
).add_to(m)

# 7) Додаємо буфер навколо фронту (20 км)
from shapely.geometry import shape
from shapely.ops import transform
import pyproj

# Об’єднати всі лінії фронту в один MultiLineString
from shapely.geometry import mapping
geoms = [shape(feat["geometry"]) for feat in front["features"]]
front_union = geoms[0]
for g in geoms[1:]:
    front_union = front_union.union(g)

# Створюємо буфер (20 000 м)
buffer = front_union.buffer(20000)

# Проєкція для Folium: повертаємо в WGS84
project = pyproj.Transformer.from_crs("EPSG:3857","EPSG:4326",always_xy=True).transform
buff_geojson = mapping(transform(lambda x, y: pyproj.Transformer.from_crs("EPSG:4326","EPSG:3857",always_xy=True).transform(x,y), buffer))

folium.GeoJson(
    buff_geojson,
    name="Buffer 20km",
    style_function=lambda feat: {
        'fillColor': 'orange',
        'color': 'orange',
        'weight': 0,
        'fillOpacity': 0.2
    }
).add_to(m)

# 8) Додаємо маркери з розміром від count
for _, r in df.iterrows():
    if r['count']>0:
        folium.CircleMarker(
            location=[r.latitude,r.longitude],
            radius=5 + r['count'],
            color='blue',
            fill=True, fill_opacity=0.6,
            tooltip=f"{r['city']}: {int(r['count'])} attacks"
        ).add_to(m)

# 9) Легенда і шари
folium.LayerControl().add_to(m)

# 10) Зберігаємо
m.save('attack_map.html')
print("✅ Карта з фронтом, буфером і містами збережена в attack_map.html")
