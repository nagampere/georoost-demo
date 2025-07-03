import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def create_population_pyramid(df):
    fig = go.Figure()
    age_groups = ["0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75+"]
    all_age_groups = ["pop_all_0_4","pop_all_5_9","pop_all_10_14","pop_all_15_19","pop_all_20_24","pop_all_25_29","pop_all_30_34","pop_all_35_39","pop_all_40_44","pop_all_45_49","pop_all_50_54","pop_all_55_59","pop_all_60_64","pop_all_65_69","pop_all_70_74","pop_all_over_75"]
    male_age_groups = ["pop_male_0_4","pop_male_5_9","pop_male_10_14","pop_male_15_19","pop_male_20_24","pop_male_25_29","pop_male_30_34","pop_male_35_39","pop_male_40_44","pop_male_45_49","pop_male_50_54","pop_male_55_59","pop_male_60_64","pop_male_65_69","pop_male_70_74","pop_male_over_75"]
    female_age_groups = ["pop_female_0_4","pop_female_5_9","pop_female_10_14","pop_female_15_19","pop_female_20_24","pop_female_25_29","pop_female_30_34","pop_female_35_39","pop_female_40_44","pop_female_45_49","pop_female_50_54","pop_female_55_59","pop_female_60_64","pop_female_65_69","pop_female_70_74","pop_female_over_75"]
    all_population = df.loc[all_age_groups].T.values[0]
    male_population = df.loc[male_age_groups].T.values[0] 
    female_population = df.loc[female_age_groups].T.values[0]
    
    # 5歳階級ごとの人口データのdfを表示
    population_df = pd.DataFrame(
        [all_population, male_population, female_population],
        columns=age_groups,
        index=['all', 'male', 'female']
    )
    st.dataframe(population_df.T[::-1])

    fig.add_trace(go.Bar(
        y=age_groups,
        x=-male_population, # 左側に表示するために負の値を取る
        name='Male',
        orientation='h',
        marker=dict(color='blue')
    ))
    
    fig.add_trace(go.Bar(
        y=age_groups,
        x=female_population,
        name='Female',
        orientation='h',
        marker=dict(color='red')
    ))
    
    total_population = max(male_population) + max(female_population)
    if total_population < 100:
        grid_width = 10
    elif total_population < 1000:
        grid_width = 50
    elif total_population < 5000:
        grid_width = 100
    elif total_population < 10000:
        grid_width = 500
    elif total_population < 50000:
        grid_width = 1000
    elif total_population < 100000:
        grid_width = 5000
    elif total_population < 200000:
        grid_width = 10000
    elif total_population < 500000:
        grid_width = 20000
    elif total_population < 1000000:
        grid_width = 50000
    else:
        grid_width = 100000
    grid_lines = list(range((int(min(-male_population))//grid_width+1)*grid_width, 0, grid_width)) + list(range(0, (int(max(female_population))//grid_width+1)*grid_width, grid_width))
    grid_text = [str(x) for x in grid_lines]

    fig.update_layout(
        xaxis=dict(
            title='Population', 
            tickvals=grid_lines,
            ticktext=grid_text,
            showgrid=True,
            gridcolor='lightgray',
            tickmode='array',
            zeroline=True,  # 0を基準とした罫線を引く
            zerolinecolor='black',
            zerolinewidth=1
        ),
        barmode='relative',
        bargap=0.1,
        margin=dict(t=10, b=10, l=50, r=50)  # 左右の余白を増加
    )
    
    st.plotly_chart(fig)
