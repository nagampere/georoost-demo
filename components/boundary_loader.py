import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.ops import unary_union

def download_boundary(name_list: list[str], level: str, gdf: gpd.GeoDataFrame) -> None:
    """
    選択した地域の境界をダウンロードするための関数
    :param name: 地域名
    :param level: "小地域" or "市区町村" or "都道府県"
    :param gdf: GeoDataFrame
    """
    name = "_".join(name_list)

    if level == "小地域": 
        by = None
        drop_columns = ['id', 'S_NAME', 'S_AREA', 'KEY_CODE']
    elif level == "市区町村": 
        by = 'JCODE'
        drop_columns = ['id', 'S_NAME', 'S_AREA', 'KEY_CODE']
    elif level == "都道府県": 
        by = 'PREF'
        drop_columns = ['id', 'JCODE', 'CITY_NAME', 'CITY', 'S_NAME', 'S_AREA', 'KEY_CODE']
    else:
        raise ValueError('levelは"小地域", "市区町村", "都道府県"のいずれかである必要があります。')

    # GeoDataFrameを作成
    gdf_polygon = gdf.drop(columns=drop_columns) # 不要な列を削除
    obj_cols = gdf_polygon.select_dtypes(include=['object']).columns # 文字列型の列を取得
    agg_obj_cols = {col: 'first' for col in obj_cols} # 文字列型の列を集約するための辞書
    num_cols = gdf_polygon.select_dtypes(include=['number']).columns # 数値型の列を取得
    agg_num_cols = {col: 'sum' for col in num_cols} # 数値型の列を集約するための辞書

    gdf_polygon = gdf_polygon.to_crs('EPSG:6674')
    gdf_polygon['geometry'] = gdf_polygon.buffer(0.00001)  # バッファを追加(Multipolygonの境界線を削除するため)
    gdf_polygon = gdf_polygon.dissolve(by=by, aggfunc={**agg_obj_cols, **agg_num_cols}) # 指定した列で集約
    gdf_polygon['geometry'] = gdf_polygon.buffer(-0.00001)  # バッファを削除
    gdf_polygon = gdf_polygon.to_crs('EPSG:4326')
    st.dataframe(gdf_polygon.drop(columns='geometry'))
    # GeoJSON形式でダウンロード
    geojson_data = gdf_polygon.to_json()
    st.download_button(
        label="GeoJSON形式でダウンロード(EPSG:4326)",
        data=geojson_data.encode("utf-8"),
        file_name=f"{name}.geojson",
        mime="application/geo+json",
    )
