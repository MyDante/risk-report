import pandas as pd

def main():
    # 1. Зчитайте історію
    hist = pd.read_csv('attacks_history.csv', parse_dates=['date'])

    # 2. Зчитайте свіжі події (з вашого скрейпера)
    new = pd.read_csv('news_with_signals.csv', parse_dates=['date'])
    # де news_with_signals.csv містить: date, city, attack_type, text

    # 3. Перетворіть new у той же формат, що hist
    # припустимо, hist має колонки: date,region,location,descr,casualties,city,attack_type,link
    # ви можете дістати лише перші 4–5 колонок для нового рядка

    # Для прикладу — візьмемо date, city, attack_type, залишимо інші поля порожніми
    new_hist = new[['date','city','attack_type']].copy()
    new_hist['region'] = ''
    new_hist['location'] = ''
    new_hist['description'] = new['text']
    new_hist['casualties'] = 0
    new_hist['link'] = ''

    # 4. Об’єднаємо та видалимо дублі
    merged = pd.concat([hist, new_hist], ignore_index=True)
    merged = merged.drop_duplicates(subset=['date','city','attack_type'], keep='last')

    # 5. Збережемо назад в attacks_history.csv
    merged.to_csv('attacks_history.csv', index=False)
    print(f"✅ attacks_history.csv оновлено: {len(new_hist)} нових рядків")

if __name__ == '__main__':
    main()
