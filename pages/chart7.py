import streamlit as st
import duckdb
import pandas as pd
import json
import pydeck as pdk

from components.table_loader import get_tables
from components.schema_selector import select_schema
import geopandas as gpd

# キャッシュのリセット
if st.session_state.get("current_page") != "chart7":
    # 他のページから来た場合、キャッシュをクリア
    st.cache_data.clear()
    st.session_state.clear()
    st.session_state["current_page"] = "chart7"

# データベースのパス
MOTHERDUCK_TOKEN = st.secrets["MOTHERDUCK_TOKEN"]
DUCKDB_PATH = f"md:georoost-demo?motherduck_token={MOTHERDUCK_TOKEN}"
con = duckdb.connect(DUCKDB_PATH, read_only=True)
con.sql('INSTALL spatial;')
con.sql('LOAD spatial;')

# Streamlit UI 設定
st.title("シェアサイクルポートの可視化")


area_df = con.sql("SELECT *, st_astext(geom) as geometry FROM  main_marts.mrt_sharecycle__station").df()
pref_list = area_df['pref_name'].drop_duplicates().to_list()


# 都道府県の選択
pref_levels = st.multiselect(
    "都道府県名を選択してください", 
    pref_list
)

if st.button("市区町村・小地域のデータを取得"):
    # 選択した地域を抽出
    if pref_levels: 
        name = ",".join(pref_levels)
        filtered_df = area_df[area_df['pref_name'].isin(pref_levels)]
    else:
        name = "全国"
        filtered_df = area_df
    
    filtered_gdf = gpd.GeoDataFrame(
        filtered_df.drop(columns='geometry'), 
        geometry=gpd.GeoSeries.from_wkt(filtered_df["geometry"]),
        crs="EPSG:4612"
    )

    # 中心座標を取得
    center_lat = filtered_gdf.geometry.to_crs('EPSG:6674').centroid.to_crs('EPSG:4326').y.mean()
    center_lon = filtered_gdf.geometry.to_crs('EPSG:6674').centroid.to_crs('EPSG:4326').x.mean()

    # 可視化（Pydeck）
    st.write("### マップ表示")
    st.dataframe(filtered_df)

    # Pydeckレイヤーの作成
    # docomo: 赤
    # oepnstreet: オレンジ

    # filtered_gdfにoperator_idに基づいてカラーコードを指定した列を追加
    filtered_gdf["operator_color"] = filtered_gdf["operator"].map(
        {
            'docomo':     [189,   0, 38, 140], #　赤色
            'openstreet': [247, 178, 10, 140]  # オレンジ色
        }
    ).apply(lambda x: list(x) if isinstance(x, list) else [255, 255, 255, 140])  # Ensure the column contains lists
    filtered_df = pd.DataFrame(filtered_gdf[["operator", "name", "operator_color", "capacity", "lat", "lon"]])

    layer = pdk.Layer(
        "ScatterplotLayer",
        data =filtered_df,
        get_position=["lon", "lat"],
        get_color="operator_color",
        pickable=True,
        radius_scale=20,
        auto_highroad=True,
    )

    # Pydeckのマップの作成
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=14, pitch=0),
        tooltip={"text": "運行事業者：{operator}\nポート名：{name}\n駐輪可能数：{capacity}"},
        map_style='road'  # ベースマップを白に変更
    )

    # Streamlitアプリの描画
    st.pydeck_chart(deck)

    # GeoDataFrameをGeoJSON形式でエクスポート
    filtered_gdf['last_updated']  = filtered_gdf['last_updated'].astype(str)
    geojson_data = filtered_gdf.drop(columns=['geom']).to_json()
    st.download_button(
        label="GeoJSON をダウンロード",
        data=geojson_data.encode("utf-8"),
        file_name=f"シェアサイクルポート_{name}.geojson",
        mime="application/geo+json",
    )



# 接続を閉じる
con.close()

# 出典情報
references = "【出典】株式会社ドコモ・バイクシェア / 公共交通オープンデータ協議会「ドコモ・バイクシェア バイクシェア関連情報」,</br> OpenStreet株式会社 / 公共交通オープンデータ協議会「OpenStreet（ハローサイクリング） バイクシェア関連情報」"
st.markdown(f"<div style='text-align: right; color: #666; font-size: 0.8em;'>{references}</div>", unsafe_allow_html=True)

# ホームに戻るボタン
st.markdown("---")  # 区切り線
if st.button("⬅ Back to Home"): st.switch_page("pages/home.py")
