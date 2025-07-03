import pandas as pd

def population_aggregate(df:pd.DataFrame, name_list:list[str]) -> pd.DataFrame:
    name = "_".join(name_list)
    
    d_pop = df['sum'].to_dict()
    if d_pop['pop_all'] == 0 or d_pop['hh_all'] == 0:
        d_agg = {key: 0 for key in [
            '人口総数', '人口密度（人/km^2）', '年少人口比率（0~14歳）', '生産年齢人口比率（15~64歳）',
            '老年人口比率（65歳以上）', '老年人口比率（75歳以上）', '世帯総数', '単身世帯比率',
            '核家族世帯比率', '夫婦のみ世帯比率', '子どもがいる世帯比率', '就労世帯比率',
            '持家世帯比率', '民営借家世帯比率', '戸建て世帯比率', 'アパート世帯比率'
        ]}
    else:
        d_agg = {
            '人口総数': round(d_pop['pop_all']),
            '人口密度（人/km^2）': round(d_pop['pop_all'] / d_pop['AREA'] * 1000**2),
            '年少人口比率（0~14歳）': round(d_pop['pop_all_under_15'] / d_pop['pop_all'] * 100, 1),
            '生産年齢人口比率（15~64歳）': round(d_pop['pop_all_bet_15_64'] / d_pop['pop_all'] * 100, 1),
            '老年人口比率（65歳以上）': round(d_pop['pop_all_over_65'] / d_pop['pop_all'] * 100, 1),
            '老年人口比率（75歳以上）': round(d_pop['pop_all_over_75'] / d_pop['pop_all'] * 100, 1),
            '世帯総数': round(d_pop['hh_all']),
            '単身世帯比率': round(d_pop['hh_mem_1'] / d_pop['hh_all'] * 100, 1),
            '核家族世帯比率': round(d_pop['hh_fam_nuc'] / d_pop['hh_all'] * 100, 1),
            '夫婦のみ世帯比率': round(d_pop['hh_fam_cauple'] / d_pop['hh_all'] * 100, 1),
            '子どもがいる世帯比率': round(d_pop['hh_fam_child'] / d_pop['hh_all'] * 100, 1),
            '就労世帯比率': round((d_pop['hh_agr'] + d_pop['hh_mix'] + d_pop['hh_nonagr']) / d_pop['hh_all'] * 100, 1),
            '持家世帯比率': round(d_pop['hh_own'] / d_pop['hh_all'] * 100, 1),
            '民営借家世帯比率': round(d_pop['hh_tenants'] / d_pop['hh_all'] * 100, 1),
            '戸建て世帯比率': round(d_pop['hh_house'] / d_pop['hh_all'] * 100, 1),
            'アパート世帯比率': round(d_pop['hh_apartment'] / d_pop['hh_all'] * 100, 1)
        }
    df_res = pd.DataFrame.from_dict(d_agg, orient='index', columns=[name])
    return df_res