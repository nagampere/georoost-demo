import streamlit as st
import pandas as pd
import geopandas as gpd

def download_circle(center_lat, center_lon, radius_m):
    """
    円形領域をダウンロードするための関数
    :param center_lat: 円の中心の緯度
    :param center_lon: 円の中心の経度
    :param radius_m: 半径（メートル）
    """
    # 円形領域を作成
    center = gpd.GeoSeries.from_xy([center_lon], [center_lat]).set_crs(epsg=4612).to_crs(epsg=6674)
    circle = center.buffer(radius_m)
    df_polygon = pd.DataFrame(
        {
            'name': ['円形領域'],
            'latitude': [center_lat],
            'longitude': [center_lon],
            'distance': [radius_m],
            'geometry': circle.to_crs(epsg=4326)[0].wkt
        }
    )
    st.dataframe(df_polygon)
    # GeoDataFrameを作成
    gdf_polygon = gpd.GeoDataFrame(
        df_polygon.drop(columns='geometry'), 
        geometry=gpd.GeoSeries.from_wkt(df_polygon["geometry"]),
        crs="EPSG:4326"
    )
    # GeoJSON形式でダウンロード
    geojson_data = gdf_polygon.to_json()
    st.download_button(
        label="GeoJSON形式でダウンロード(EPSG:4326)",
        data=geojson_data.encode("utf-8"),
        file_name=f"from_{center_lon}_{center_lat}_{radius_m}m.geojson",
        mime="application/geo+json",
    )
