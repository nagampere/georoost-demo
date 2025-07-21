import streamlit as st
from PIL import Image
import yaml

# Streamlitのページ設定
im = Image.open("images/GeoRoost_favicon.ico")
st.set_page_config(
    page_title="GeoRoost", 
    page_icon=im,
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ロゴの設定
st.logo(
    "images/GeoRoost_Sidebar.png", 
    size="large",
    icon_image="images/GeoRoost_favicon.ico"
)



# サイドバーに権利表記を追加し、リンクを設定

st.sidebar.markdown(
    """
    <div style="text-align: center; font-size: 12px; color: gray;">
        © 2025 <a href= "https://amane.ltd/" >株式会社AMANE</a>. All rights reserved.
    </div>
    """, 
    unsafe_allow_html=True
)


# YAMLファイルを読み込む関数
def load_yaml(file_path) -> dict:
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

# YAMLからチャートリストを取得
dict_section = load_yaml("pages/page_list.yaml")

# ページリストを作成
list_section = {}

for section, list_chart in dict_section.items():
    list_section[section] = []

    for chart in list_chart:
        # チャートのページ名を取得
        page = st.Page(chart["page"], title=chart["title"], icon=chart["icon"])
        list_section[section].append(page)

pg = st.navigation(list_section)
pg.run()

