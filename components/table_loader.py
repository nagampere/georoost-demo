import streamlit as st

# DuckDB からテーブル一覧を取得
def get_tables(con):
    try:
        tables = con.execute("select * from information_schema.tables where table_catalog = 'georoost-demo'").fetchdf()["table_name"].tolist()
        tables.sort()
        return tables if tables else []
    except Exception as e:
        st.error(f"テーブル一覧の取得に失敗しました: {e}")
        return []