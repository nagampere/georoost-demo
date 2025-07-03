import streamlit as st

# DuckDB からテーブル一覧を取得
def get_tables(con):
    try:
        tables = con.execute("select * from information_schema.tables").fetchdf()["table_name"].tolist()
        return tables if tables else []
    except Exception as e:
        st.error(f"テーブル一覧の取得に失敗しました: {e}")
        return []