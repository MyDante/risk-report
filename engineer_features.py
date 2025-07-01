import pandas as pd
from datetime import timedelta

def main():
    # 1) Завантажуємо історію атак
    attacks = pd.read_csv('attacks_history.csv', parse_dates=['date'])

    # 2) Генеруємо грід міст×дат
    all_dates  = pd.date_range(attacks['date'].min(), attacks['date'].max(), freq='D')
    all_cities = attacks['city'].unique()
    grid = pd.MultiIndex.from_product([all_cities, all_dates], names=['city','date'])
    df = pd.DataFrame(index=grid).reset_index()

    # 3) Рахуємо загальні атаки і по кожному типу
    types = attacks['attack_type'].unique().tolist()
    cnt = attacks.groupby(['city','date']).size().rename('attacks').reset_index()
    df = df.merge(cnt, on=['city','date'], how='left').fillna({'attacks':0})
    for t in types:
        cnt_t = (
            attacks[attacks['attack_type']==t]
                   .groupby(['city','date'])
                   .size().rename(t).reset_index()
        )
        df = df.merge(cnt_t, on=['city','date'], how='left').fillna({t:0})

    # 4) Rolling-ознаки за 1,7,30 днів
    windows = [1,7,30]
    feat_cols = []
    for w in windows:
        df[f'att_{w}d'] = df.groupby('city')['attacks'].transform(
            lambda x: x.rolling(w, min_periods=1).sum()
        )
        feat_cols.append(f'att_{w}d')
        for t in types:
            col = f'{t}_{w}d'
            df[col] = df.groupby('city')[t].transform(
                lambda x: x.rolling(w, min_periods=1).sum()
            )
            feat_cols.append(col)

    # 5) Створюємо таргет next_type — тип атаки наступного дня або 'none'
    # зібрати списки attack_type по city & date
    grouped = attacks.groupby(['city','date'])['attack_type'].agg(list)
    idx = pd.MultiIndex.from_frame(df[['city','date']])
    next_map = grouped.reindex(idx)
    # замінюємо NaN на порожній список
    next_map = next_map.map(lambda x: x if isinstance(x, list) else [])
    # вибираємо перший елемент списку або 'none'
    df['next_type'] = next_map.map(lambda lst: lst[0] if lst else 'none').values

    # 6) Зберігаємо фінальний датасет
    out = df[['city','date'] + feat_cols + ['next_type']]
    out.to_csv('model_dataset.csv', index=False)
    print("✅ Збережено model_dataset.csv з", len(feat_cols), "фічами і next_type")

if __name__ == "__main__":
    main()
