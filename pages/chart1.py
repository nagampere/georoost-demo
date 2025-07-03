import streamlit as st
import duckdb
import pandas as pd
import json

from components.table_loader import get_tables
from components.schema_selector import select_schema
import geopandas as gpd

# データベースのパス
MOTHERDUCK_TOKEN = st.secrets["MOTHERDUCK_TOKEN"]
DUCKDB_PATH = f"md:georoost-demo?motherduck_token={MOTHERDUCK_TOKEN}"
con = duckdb.connect(DUCKDB_PATH, read_only=True)
con.sql('INSTALL spatial;')
con.sql('LOAD spatial;')

# Streamlit UI 設定
st.title("DuckDB テーブルビュワー")

# テーブル選択
tables = get_tables(con)

if tables:
    selected_table = st.selectbox("データテーブルを選択", tables)
else:
    st.warning("利用可能なテーブルがありません。DuckDB のデータを確認してください。")
    selected_table = None

if selected_table:
    st.write(f"**{selected_table} のデータプレビュー**")
    st.dataframe(con.execute(f"SELECT * FROM {select_schema(selected_table)}.{selected_table}").fetchdf(), height=600)

# 接続を閉じる
con.close()

# ホームに戻るボタン
if st.button("⬅ Back to Home"): st.switch_page("app.py")