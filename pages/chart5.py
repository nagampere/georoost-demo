import streamlit as st
import duckdb
import pandas as pd
import geopandas as gpd
import pydeck as pdk
import folium
from streamlit_folium import st_folium

from components.population_pyramid import create_population_pyramid
from components.population_aggregator import population_aggregate
from components.boundary_loader import download_boundary

# キャッシュのリセット
if st.session_state.get("current_page") != "chart5":
    # 他のページから来た場合、キャッシュをクリア
    st.cache_data.clear()
    st.session_state.clear()
    st.session_state["current_page"] = "chart5"

# DuckDB データベースのパス
MOTHERDUCK_TOKEN = st.secrets["MOTHERDUCK_TOKEN"]
DUCKDB_PATH = f"md:georoost-demo?motherduck_token={MOTHERDUCK_TOKEN}"
con = duckdb.connect(DUCKDB_PATH, read_only=True)
con.sql('INSTALL spatial;')
con.sql('LOAD spatial;')


# 都道府県と市区町村のリストを取得、セッションステートに保存
if 'area_df' in st.session_state:
    area_df = st.session_state['area_df']
else:
    st.session_state["area_df"] = con.sql('''
        SELECT 
            *, 
            PREF || CITY AS JCODE
        FROM main_staging.stg_census2020__map_jcode
        WHERE HCODE = 8101
    ''').df()
    area_df = st.session_state['area_df']

st.title("市区町村・小地域の人口抽出")

pref_dict = dict(area_df[['PREF_NAME', 'PREF']].drop_duplicates().values)

# 都道府県の選択
pref_level = st.selectbox(
    "都道府県名を選択してください", 
    pref_dict.keys(), 
    format_func=lambda x: f"{x} ({pref_dict[x]})"
)
pref_code = pref_dict[pref_level]

# 市区町村の選択
city_dict = dict(area_df[area_df['PREF_NAME'] == pref_level][['CITY_NAME', 'JCODE']].drop_duplicates().values)
city_levels = st.multiselect(
    "市区町村名を選択してください", 
    city_dict.keys(),
    format_func=lambda x: f"{x} ({city_dict[x]})"
)
city_code = [city_dict[x] for x in city_levels]

# 小地域の選択
key_dict = dict(area_df[area_df['JCODE'].isin(city_code)][['S_NAME', 'KEY_CODE']].drop_duplicates().values)
key_levels = st.multiselect(
    "小地域名を選択してください", 
    key_dict.keys(),
    format_func=lambda x: f"{x} ({key_dict[x]})"
)
key_code = [key_dict[x] for x in key_levels]

if st.button("市区町村・小地域のデータを取得"):
    # 選択した地域を抽出
    if key_levels:
        name_list = key_levels
        filtered_df = con.sql('''
            SELECT 
                * EXCLUDE(geom),
                PREF || CITY AS JCODE,
                St_AsText(geom) AS geometry
            FROM main_marts.mrt_census2020__map_with_pop
            WHERE KEY_CODE IN ({})
        '''.format(', '.join(f"'{code}'" for code in key_code))).df()
        # filtered_df = area_df[area_df['KEY_CODE'].isin(key_code)]
        level_name = "小地域"
    elif city_levels:
        name_list = city_levels
        filtered_df = con.sql('''
            SELECT 
                * EXCLUDE(geom),
                PREF || CITY AS JCODE,
                St_AsText(geom) AS geometry
            FROM main_marts.mrt_census2020__map_with_pop
            WHERE JCODE IN ({})
        '''.format(', '.join(f"'{code}'" for code in city_code))).df()
        # filtered_df = area_df[area_df['JCODE'].isin(city_code)]
        level_name = "市区町村"
    else: 
        name_list = pref_level
        filtered_df = con.sql('''
            SELECT 
                * EXCLUDE(geom),
                PREF || CITY AS JCODE,
                St_AsText(geom) AS geometry
            FROM main_marts.mrt_census2020__map_with_pop
            WHERE PREF = {}
        '''.format(pref_code)).df()
        # filtered_df = area_df[area_df['PREF_NAME'].isin(pref_levels)]
        level_name = "都道府県"
    st.session_state["level_name"] = level_name
    st.session_state["name_list"] = name_list

    filtered_gdf = gpd.GeoDataFrame(
        filtered_df.drop(columns='geometry'), 
        geometry=gpd.GeoSeries.from_wkt(filtered_df["geometry"]),
        crs="EPSG:4612"
    )
    st.dataframe(filtered_df)
    # 中心座標を取得
    center_lat = filtered_gdf.geometry.to_crs('EPSG:6674').centroid.to_crs('EPSG:4326').y.mean()
    center_lon = filtered_gdf.geometry.to_crs('EPSG:6674').centroid.to_crs('EPSG:4326').x.mean()
    st.session_state["filtered_gdf"] = filtered_gdf

    # 可視化（Pydeck）
    st.write("### マップ表示")
    if level_name == "小地域": zoom_scale = 14
    elif level_name == "市区町村": zoom_scale = 12
    else: zoom_scale = 10
    # Pydeckレイヤーの作成
    layer = pdk.Layer(
        "GeoJsonLayer",
        filtered_gdf[["S_NAME", "KEY_CODE", "geometry"]],
        get_fill_color=[0, 0, 255, 140],  # 青色
        get_line_color=[255, 255, 255, 200],  # 白色の境界線
        line_width_min_pixels=1,  # 境界線の最小幅
        pickable=True,
        auto_highlight=True,
    )

    # Pydeckのマップの作成
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=zoom_scale, pitch=0),
        tooltip={"text": "{S_NAME}\n{KEY_CODE}"},
        map_style='road'  # ベースマップを白に変更
    )

    # Streamlitアプリの描画
    st.pydeck_chart(deck)


    # 集計 (人口データの統計量)
    st.session_state["agg_df"] = filtered_df.select_dtypes(include=['number']).aggregate(["sum", "mean"]).T
    st.session_state["res_df"] = population_aggregate(st.session_state["agg_df"], name_list)

if 'res_df' in st.session_state:
    res_df = st.session_state['res_df']
    agg_df = st.session_state['agg_df']
    level_name = st.session_state['level_name']
    name_list = st.session_state['name_list']
    filtered_gdf = st.session_state['filtered_gdf']

    st.write("### 人口データの統計量")
    st.dataframe(res_df)

    # 人口ピラミッドの表示
    st.write("### 人口ピラミッド")
    create_population_pyramid(agg_df)

    # 円形領域の可視化
    st.write("### 境界のダウンロード")
    download_boundary(name_list, level_name, filtered_gdf)

# 接続を閉じる
con.close()

# ホームに戻るボタン
st.markdown("---")  # 区切り線
if st.button("⬅ Back to Home"): st.switch_page("pages/home.py")