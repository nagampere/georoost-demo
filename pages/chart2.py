import streamlit as st
import duckdb
import pandas as pd
import json

from components.table_loader import get_tables
from components.schema_selector import select_schema
import geopandas as gpd

# キャッシュのリセット
if st.session_state.get("current_page") != "chart2":
    # 他のページから来た場合、キャッシュをクリア
    st.cache_data.clear()
    st.session_state.clear()
    st.session_state["current_page"] = "chart2"

# データベースのパス
MOTHERDUCK_TOKEN = st.secrets["MOTHERDUCK_TOKEN"]
DUCKDB_PATH = f"md:georoost-demo?motherduck_token={MOTHERDUCK_TOKEN}"
con = duckdb.connect(DUCKDB_PATH, read_only=True)
con.sql('INSTALL spatial;')
con.sql('LOAD spatial;')

# Streamlit UI 設定
st.title("DuckDB テーブルエクスポート")

# テーブル選択
tables = get_tables(con)

if tables:
    selected_table = st.selectbox("データテーブルを選択", tables)
else:
    st.warning("利用可能なテーブルがありません。DuckDB のデータを確認してください。")
    selected_table = None

if selected_table:

    # テーブルの列を取得
    columns_query = f"PRAGMA table_info({select_schema(selected_table)}.{selected_table})"
    columns_info = con.execute(columns_query).df()
    columns = columns_info["name"].tolist()

    # 列選択（デフォルトですべて選択）
    selected_columns = st.multiselect("エクスポートする列を選択", columns, default=columns)

    # エクスポート形式を選択
    export_format = st.selectbox("エクスポート形式を選択", ["csv", "geojson", "xlsx"])

    # データを取得
    df = con.execute(f"SELECT {', '.join(selected_columns)} FROM {select_schema(selected_table)}.{selected_table}").df()

    if export_format == "csv":
        df = con.execute(f"SELECT {', '.join(selected_columns)} FROM {select_schema(selected_table)}.{selected_table}").df()
        csv_data = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="CSV をダウンロード",
            data=csv_data,
            file_name=f"{selected_table}.csv",
            mime="text/csv",
        )

    elif export_format == "geojson":
        geom_column = st.selectbox("ジオメトリ列を選択", columns)
        crs_type = st.text_input("座標系を入力", "EPSG:4326")
        df = con.execute(
            f'''
                SELECT 
                    {', '.join(selected_columns)} ,
                    ST_astext({geom_column}) as {geom_column}_wkt
                FROM 
                    {select_schema(selected_table)}.{selected_table}
            ''').df()

        if geom_column:
            # ジオメトリ列を指定してGeoDataFrameを作成
            gdf = gpd.GeoDataFrame(
                df.drop(columns=[geom_column,f"{geom_column}_wkt"]),
                geometry=gpd.GeoSeries.from_wkt(df[f"{geom_column}_wkt"]),
                crs=crs_type
            )

            # GeoDataFrameをGeoJSON形式でエクスポート
            geojson_data = gdf.to_json()
            st.download_button(
                label="GeoJSON をダウンロード",
                data=geojson_data.encode("utf-8"),
                file_name=f"{selected_table}.geojson",
                mime="application/geo+json",
            )
        else:
            st.error("ジオメトリ列が選択されていません。")


    elif export_format == "xlsx":
        
        excel_buffer = pd.ExcelWriter(f"{selected_table}.xlsx", engine="xlsxwriter")
        df.to_excel(excel_buffer, sheet_name=selected_table, index=False)
        excel_buffer.close()
        with open(f"{selected_table}.xlsx", "rb") as file:
            st.download_button(
                label="Excel (XLSX) をダウンロード",
                data=file,
                file_name=f"{selected_table}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

else:
    st.error("DuckDB にテーブルが存在しません。")

st.markdown("---")  # 区切り線

if not df.empty:
    st.write(f"**{selected_table} のデータプレビュー**")
    st.dataframe(df.head())
else:
    st.warning("このテーブルにはデータが含まれていません。")

# 接続を閉じる
con.close()

# ホームに戻るボタン
st.markdown("---")  # 区切り線
if st.button("⬅ Back to Home"): st.switch_page("pages/home.py")