import streamlit as st
import duckdb
import pandas as pd
import geopandas as gpd
import pydeck as pdk
import folium
from streamlit_folium import st_folium

from components.population_pyramid import create_population_pyramid
from components.population_aggregator import population_aggregate
from components.circle_loader import download_circle

# キャッシュのリセット
if st.session_state.get("current_page") != "chart3":
    # 他のページから来た場合、キャッシュをクリア
    st.cache_data.clear()
    st.session_state.clear()
    st.session_state["current_page"] = "chart3"

# DuckDB データベースのパス
MOTHERDUCK_TOKEN = st.secrets["MOTHERDUCK_TOKEN"]
DUCKDB_PATH = f"md:georoost-demo?motherduck_token={MOTHERDUCK_TOKEN}"
con = duckdb.connect(DUCKDB_PATH, read_only=True)
con.sql('INSTALL spatial;')
con.sql('LOAD spatial;')

st.title("円内の人口抽出")
st.text("処理に時間がかかる場合があります。")

# ユーザー入力（緯度・経度・半径）
col1, col2, col3 = st.columns(3)
with col1:
    center_lat = st.number_input("中心の緯度 (latitude)", format="%.14f", value=35.71012978788501)
with col2:
    center_lon = st.number_input("中心の経度 (longitude)", format="%.14f", value=139.81077085640902)
with col3:
    radius_m = st.number_input("半径 (m)", min_value=10, max_value=10000, value=500)

# 円内のデータを取得
@st.cache_data
def get_data_within_circle(center_lat, center_lon, radius_m):
    
    # 中心点を Point に変換
    center = gpd.GeoSeries.from_xy([center_lon], [center_lat]).set_crs(epsg=4612).to_crs(epsg=6674)
    # メートル単位のバッファ（円形領域）を作成
    circle = center.buffer(radius_m)[0]
    
    clipped_df = con.sql(
        f'''
        WITH source AS (
            SELECT
                *,
                ST_Intersection(ST_GeomFromText('{circle}'), ST_Transform(geom, 'EPSG:4612', 'EPSG:6674', always_xy := true)) as clipped_geom
            FROM
                main_marts.mrt_census2020__map_with_pop
            WHERE
                ST_Intersects(ST_GeomFromText('{circle}'), ST_Transform(geom, 'EPSG:4612', 'EPSG:6674', always_xy := true))
        )
        SELECT
            KEY_CODE,
            PREF,
            CITY,
            S_AREA,
            PREF_NAME,
            CITY_NAME,
            S_NAME,
            HCODE,
            AREA as AREA,
            (pop_all * st_area(clipped_geom) / AREA)::INT as pop_all,
            (pop_all_0_4 * st_area(clipped_geom) / AREA)::INT as pop_all_0_4,
            (pop_all_5_9 * st_area(clipped_geom) / AREA)::INT as pop_all_5_9,
            (pop_all_10_14 * st_area(clipped_geom) / AREA)::INT as pop_all_10_14,
            (pop_all_15_19 * st_area(clipped_geom) / AREA)::INT as pop_all_15_19,
            (pop_all_20_24 * st_area(clipped_geom) / AREA)::INT as pop_all_20_24,
            (pop_all_25_29 * st_area(clipped_geom) / AREA)::INT as pop_all_25_29,
            (pop_all_30_34 * st_area(clipped_geom) / AREA)::INT as pop_all_30_34,
            (pop_all_35_39 * st_area(clipped_geom) / AREA)::INT as pop_all_35_39,
            (pop_all_40_44 * st_area(clipped_geom) / AREA)::INT as pop_all_40_44,
            (pop_all_45_49 * st_area(clipped_geom) / AREA)::INT as pop_all_45_49,
            (pop_all_50_54 * st_area(clipped_geom) / AREA)::INT as pop_all_50_54,
            (pop_all_55_59 * st_area(clipped_geom) / AREA)::INT as pop_all_55_59,
            (pop_all_60_64 * st_area(clipped_geom) / AREA)::INT as pop_all_60_64,
            (pop_all_65_69 * st_area(clipped_geom) / AREA)::INT as pop_all_65_69,
            (pop_all_70_74 * st_area(clipped_geom) / AREA)::INT as pop_all_70_74,
            (pop_all_under_15 * st_area(clipped_geom) / AREA)::INT as pop_all_under_15,
            (pop_all_bet_15_64 * st_area(clipped_geom) / AREA)::INT as pop_all_bet_15_64,
            (pop_all_under_65 * st_area(clipped_geom) / AREA)::INT as pop_all_under_65,
            (pop_all_under_75 * st_area(clipped_geom) / AREA)::INT as pop_all_under_75,
            (pop_all_over_65 * st_area(clipped_geom) / AREA)::INT as pop_all_over_65,
            (pop_all_over_75 * st_area(clipped_geom) / AREA)::INT as pop_all_over_75,
            (pop_male * st_area(clipped_geom) / AREA)::INT as pop_male,
            (pop_male_0_4 * st_area(clipped_geom) / AREA)::INT as pop_male_0_4,
            (pop_male_5_9 * st_area(clipped_geom) / AREA)::INT as pop_male_5_9,
            (pop_male_10_14 * st_area(clipped_geom) / AREA)::INT as pop_male_10_14,
            (pop_male_15_19 * st_area(clipped_geom) / AREA)::INT as pop_male_15_19,
            (pop_male_20_24 * st_area(clipped_geom) / AREA)::INT as pop_male_20_24,
            (pop_male_25_29 * st_area(clipped_geom) / AREA)::INT as pop_male_25_29,
            (pop_male_30_34 * st_area(clipped_geom) / AREA)::INT as pop_male_30_34,
            (pop_male_35_39 * st_area(clipped_geom) / AREA)::INT as pop_male_35_39,
            (pop_male_40_44 * st_area(clipped_geom) / AREA)::INT as pop_male_40_44,
            (pop_male_45_49 * st_area(clipped_geom) / AREA)::INT as pop_male_45_49,
            (pop_male_50_54 * st_area(clipped_geom) / AREA)::INT as pop_male_50_54,
            (pop_male_55_59 * st_area(clipped_geom) / AREA)::INT as pop_male_55_59,
            (pop_male_60_64 * st_area(clipped_geom) / AREA)::INT as pop_male_60_64,
            (pop_male_65_69 * st_area(clipped_geom) / AREA)::INT as pop_male_65_69,
            (pop_male_70_74 * st_area(clipped_geom) / AREA)::INT as pop_male_70_74,
            (pop_male_under_15 * st_area(clipped_geom) / AREA)::INT as pop_male_under_15,
            (pop_male_bet_15_64 * st_area(clipped_geom) / AREA)::INT as pop_male_bet_15_64,
            (pop_male_under_65 * st_area(clipped_geom) / AREA)::INT as pop_male_under_65,
            (pop_male_under_75 * st_area(clipped_geom) / AREA)::INT as pop_male_under_75,
            (pop_male_over_65 * st_area(clipped_geom) / AREA)::INT as pop_male_over_65,
            (pop_male_over_75 * st_area(clipped_geom) / AREA)::INT as pop_male_over_75,
            (pop_female * st_area(clipped_geom) / AREA)::INT as pop_female,
            (pop_female_0_4 * st_area(clipped_geom) / AREA)::INT as pop_female_0_4,
            (pop_female_5_9 * st_area(clipped_geom) / AREA)::INT as pop_female_5_9,
            (pop_female_10_14 * st_area(clipped_geom) / AREA)::INT as pop_female_10_14,
            (pop_female_15_19 * st_area(clipped_geom) / AREA)::INT as pop_female_15_19,
            (pop_female_20_24 * st_area(clipped_geom) / AREA)::INT as pop_female_20_24,
            (pop_female_25_29 * st_area(clipped_geom) / AREA)::INT as pop_female_25_29,
            (pop_female_30_34 * st_area(clipped_geom) / AREA)::INT as pop_female_30_34,
            (pop_female_35_39 * st_area(clipped_geom) / AREA)::INT as pop_female_35_39,
            (pop_female_40_44 * st_area(clipped_geom) / AREA)::INT as pop_female_40_44,
            (pop_female_45_49 * st_area(clipped_geom) / AREA)::INT as pop_female_45_49,
            (pop_female_50_54 * st_area(clipped_geom) / AREA)::INT as pop_female_50_54,
            (pop_female_55_59 * st_area(clipped_geom) / AREA)::INT as pop_female_55_59,
            (pop_female_60_64 * st_area(clipped_geom) / AREA)::INT as pop_female_60_64,
            (pop_female_65_69 * st_area(clipped_geom) / AREA)::INT as pop_female_65_69,
            (pop_female_70_74 * st_area(clipped_geom) / AREA)::INT as pop_female_70_74,
            (pop_female_under_15 * st_area(clipped_geom) / AREA)::INT as pop_female_under_15,
            (pop_female_bet_15_64 * st_area(clipped_geom) / AREA)::INT as pop_female_bet_15_64,
            (pop_female_under_65 * st_area(clipped_geom) / AREA)::INT as pop_female_under_65,
            (pop_female_under_75 * st_area(clipped_geom) / AREA)::INT as pop_female_under_75,
            (pop_female_over_65 * st_area(clipped_geom) / AREA)::INT as pop_female_over_65,
            (pop_female_over_75 * st_area(clipped_geom) / AREA)::INT as pop_female_over_75,
            (hh_all * st_area(clipped_geom) / AREA)::INT as hh_all,
            (hh_fam_rel * st_area(clipped_geom) / AREA)::INT as hh_fam_rel,
            (hh_fam_nuc * st_area(clipped_geom) / AREA)::INT as hh_fam_nuc,
            (hh_fam_cauple * st_area(clipped_geom) / AREA)::INT as hh_fam_cauple,
            (hh_fam_child * st_area(clipped_geom) / AREA)::INT as hh_fam_child,
            (hh_fam_other * st_area(clipped_geom) / AREA)::INT as hh_fam_other,
            (hh_fam_under_6 * st_area(clipped_geom) / AREA)::INT as hh_fam_under_6,
            (hh_fam_under_18 * st_area(clipped_geom) / AREA)::INT as hh_fam_under_18,
            (hh_fam_over_65 * st_area(clipped_geom) / AREA)::INT as hh_fam_over_65,
            (hh_mem_1 * st_area(clipped_geom) / AREA)::INT as hh_mem_1,
            (hh_mem_2 * st_area(clipped_geom) / AREA)::INT as hh_mem_2,
            (hh_mem_3 * st_area(clipped_geom) / AREA)::INT as hh_mem_3,
            (hh_mem_4 * st_area(clipped_geom) / AREA)::INT as hh_mem_4,
            (hh_mem_5 * st_area(clipped_geom) / AREA)::INT as hh_mem_5,
            (pop_hh * st_area(clipped_geom) / AREA)::INT as pop_hh,
            (mem_per_hh * st_area(clipped_geom) / AREA)::INT as mem_per_hh,
            (hh_agr * st_area(clipped_geom) / AREA)::INT as hh_agr,
            (hh_mix * st_area(clipped_geom) / AREA)::INT as hh_mix,
            (hh_nonagr * st_area(clipped_geom) / AREA)::INT as hh_nonagr,
            (hh_nonwork * st_area(clipped_geom) / AREA)::INT as hh_nonwork,
            (hh_unclass * st_area(clipped_geom) / AREA)::INT as hh_unclass,
            (hh_own * st_area(clipped_geom) / AREA)::INT as hh_own,
            (hh_tenants * st_area(clipped_geom) / AREA)::INT as hh_tenants,
            (hh_house * st_area(clipped_geom) / AREA)::INT as hh_house,
            (hh_tenement * st_area(clipped_geom) / AREA)::INT as hh_tenement,
            (hh_apartment * st_area(clipped_geom) / AREA)::INT as hh_apartment,
            (hh_apartment_1_2 * st_area(clipped_geom) / AREA)::INT as hh_apartment_1_2,
            (hh_apartment_3_4 * st_area(clipped_geom) / AREA)::INT as hh_apartment_3_4,
            (hh_apartment_6_10 * st_area(clipped_geom) / AREA)::INT as hh_apartment_6_10,
            (hh_apartment_over_11 * st_area(clipped_geom) / AREA)::INT as hh_apartment_over_11,
            (hh_other * st_area(clipped_geom) / AREA)::INT as hh_other,
            st_astext(ST_Transform(clipped_geom, 'EPSG:6674', 'EPSG:4326', always_xy := true)) as geometry
        FROM
            source
        '''
    ).df()
    
    result_df = gpd.GeoDataFrame(clipped_df.drop(columns='geometry'), 
                                 geometry=gpd.GeoSeries.from_wkt(clipped_df["geometry"]),
                                 crs="EPSG:4326")

    return result_df

# 抽出ボタン
if st.button("円内のデータを取得"):
    filtered_df = get_data_within_circle(center_lat, center_lon, radius_m)
    filtered_df = filtered_df.query("HCODE == 8101") # HCODEが町丁・字等(8101)のものを抽出
    
    # セッションステートに保存
    st.session_state["filtered_df"] = filtered_df
    st.session_state["center_lat"] = center_lat
    st.session_state["center_lon"] = center_lon
    st.session_state["radius_m"] = radius_m

# セッションステートからデータを取得
if "filtered_df" in st.session_state:
    filtered_df = st.session_state["filtered_df"]
    center_lat = st.session_state["center_lat"]
    center_lon = st.session_state["center_lon"]
    radius_m = st.session_state["radius_m"]
    
    st.write(f"**円内のデータ ({len(filtered_df)} 件)**")
    st.dataframe(filtered_df.drop(columns='geometry'))

    # 集計 (カテゴリごとのカウント)
    if "category" in filtered_df.columns:
        summary = filtered_df["category"].value_counts().reset_index()
        summary.columns = ["カテゴリ", "件数"]
        st.write("### カテゴリ別の集計")
        st.dataframe(summary)

    # 集計 (人口データの統計量)
    agg_df = filtered_df.select_dtypes(include=['number']).aggregate(["sum", "mean"]).T
    res_df = population_aggregate(agg_df, [f'半径{radius_m}m'])
    st.write("### 人口データの統計量")
    st.dataframe(res_df)

    # 人口ピラミッドの表示
    st.write("### 人口ピラミッド")
    create_population_pyramid(agg_df)
    
    # 可視化（Pydeck）
    st.write("### マップ表示")
    radius_scale = 10 * (radius_m / 500)
    zoom_scale = 14 - (radius_m / 2500)
    
    # Pydeckレイヤーの作成
    layer1 = pdk.Layer(
        "ScatterplotLayer",
        data=pd.DataFrame(data={"S_NAME":[f"中心座標\n({center_lon},\n{center_lat})"], "coordinates": [[center_lon, center_lat]]}),
        get_position="coordinates",
        get_color=[0, 0, 255, 140],
        pickable=True,
        radius_scale=radius_scale,
    )

    layer2 = pdk.Layer(
        "GeoJsonLayer",
        filtered_df[["S_NAME", "geometry"]],
        get_fill_color=[255, 0, 0, 140],
        pickable=True,
        auto_highlight=True,
    )

    deck = pdk.Deck(
        layers=[layer2, layer1],
        initial_view_state=pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=zoom_scale, pitch=0),
        tooltip={"text": "{S_NAME}"},
        map_style='mapbox://styles/mapbox/light-v10'
    )

    st.pydeck_chart(deck)

    # 円形領域のダウンロード
    st.write("### 円形領域のダウンロード")
    
    # GeoJSONデータを生成
    geojson_data = filtered_df.to_json()
    
    # ダウンロードボタン
    st.download_button(
        label="円形領域をGeoJSONでダウンロード",
        data=geojson_data,
        file_name=f"circle_data_{radius_m}m.geojson",
        mime="application/geo+json"
    )

# 接続を閉じる
con.close()

# ホームに戻るボタン
st.markdown("---")  # 区切り線
if st.button("⬅ Back to Home"): st.switch_page("pages/home.py")