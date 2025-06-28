import folium
import pandas as pd

# 1) Ручний парсинг CSV
records = []
with open('news_sample.csv', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        line = line.strip()
        if idx == 0 or not line:
            # пропускаємо заголовок і пусті рядки
            continue
        parts = line.split(',')
        if len(parts) < 5:
            continue

        date       = parts[0]
        city       = parts[1]
        attack_type= parts[-2]
        link       = parts[-1]
        # все, що між другим і передостаннім комами — це текст
        text       = ','.join(parts[2:-2]).strip()

        records.append({
            'date': date,
            'city': city,
            'text': text,
            'attack_type': attack_type,
            'link': link
        })

df = pd.DataFrame(records)

# 2) Діагностика: перевіримо, що тепер у city
print("Список міст у CSV після ручного парсингу:")
print(df['city'].unique())

# 3) Карта
city_coords = {
    'Kharkiv': [49.9935, 36.2304],
    'Odesa': [46.4825, 30.7233],
    'Kyiv': [50.4501, 30.5234],
    'Dnipro': [48.4647, 35.0462],
    'Sumy': [50.9077, 34.7981],
    'Kherson': [46.6354, 32.6169],
    'Mykolaiv': [46.9750, 31.9946],
    'Poltava': [49.5883, 34.5514],
    'Zaporizhzhia': [47.8388, 35.1396],
    'Donetsk': [48.0159, 37.8029]
}

city_counts = df['city'].value_counts()

m = folium.Map(location=[49.0, 32.0], zoom_start=6)
for city, count in city_counts.items():
    coords = city_coords.get(city)
    if not coords:
        continue
    color = 'red' if count >= 2 else 'orange'
    folium.CircleMarker(
        location=coords,
        radius=8 + count * 2,
        popup=f"{city}: {count} атак",
        color=color,
        fill=True,
        fill_color=color
    ).add_to(m)

m.save('attack_map.html')
print("✅ Карта атак збережена у attack_map.html")
