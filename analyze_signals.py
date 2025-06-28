import pandas as pd

# 1) Ручний парсинг CSV, як раніше
records = []
with open('news_sample.csv', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if idx == 0 or not line.strip(): 
            continue
        parts = line.strip().split(',')
        if len(parts) < 5: 
            continue
        date        = parts[0]
        city        = parts[1]
        attack_type = parts[-2]
        link        = parts[-1]
        text        = ','.join(parts[2:-2]).strip()
        records.append({
            'date': date,
            'city': city,
            'text': text,
            'attack_type': attack_type,
            'link': link
        })

df = pd.DataFrame(records)

# 2) Стеми для пошуку (короткі фрагменти)
stems = [
    "скупч",      # скупчення, скупчень
    "переміщ",    # переміщення, переміщень
    "концентрац", # концентрація, концентровани
    "загроз",     # загроза, загрози
    "тривог",     # тривога, тривогу
    "посил",      # посилили, посилення
    "заяв",       # заяви, заявляє
    "розвід",     # розвідка, розвідувальні
    "бойов"       # бойова, бойовий, боєвий, бойовий
]

def has_signal(text: str) -> bool:
    low = text.lower()
    return any(st in low for st in stems)

df['preparation_signal'] = df['text'].apply(has_signal)

# 3) Вивід результатів
signals = df[df['preparation_signal']]
print("\n🔍 Записи з виявленими сигналами підготовки до атаки:")
if not signals.empty:
    print(signals[['date','city','attack_type','text']].to_string(index=False))
else:
    print("— жодного —")

print(f"\nУсього записів: {len(df)}")
print(f"З них із сигналами: {df['preparation_signal'].sum()}")

# 4) (За бажанням) Зберігаємо для наступних кроків
df.to_csv('news_with_signals.csv', index=False, encoding='utf-8')
print("\n✅ Результати збережено у news_with_signals.csv")
