import streamlit as st
import yaml

st.set_page_config(page_title="Home", layout="wide", initial_sidebar_state="collapsed")

st.title("🕊️GeoRoost Dashboard Demo🕊️")

# YAMLファイルを読み込む関数
def load_chart_list():
    with open("pages/page_list.yaml", "r", encoding="utf-8") as file:
        return yaml.safe_load(file)["charts"]

# YAMLからチャートリストを取得
chart_list = load_chart_list()

# 縦並びでリスト表示
for chart in chart_list:
    col1, col2 = st.columns([3, 1])  # 左3:右1の比率で分割
    
    with col1:
        st.markdown(f"#### {chart['title']}")
        st.markdown(chart["description"])
    
    with col2:
        if st.button(f"Go to 「{chart['title']}」", key=chart["page"], use_container_width=True):
            st.switch_page(chart["page"])

    st.markdown("---")  # 区切り線
