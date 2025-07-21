import streamlit as st
import yaml

# キャッシュのリセット
if st.session_state.get("current_page") != "home":
    # 他のページから来た場合、キャッシュをクリア
    st.cache_data.clear()
    st.session_state.clear()
    st.session_state["current_page"] = "home"

# Markdownファイルを読み込む関数
def load_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# YAMLファイルを読み込む関数
def load_yaml(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


# タイトルと説明の表示
col1, col2, col3 = st.columns([1, 3, 1])
col2.image(    
    "images/GeoRoost_Long.png", 
    use_container_width=True,
    caption="【社内用】地理情報を活用したデータ分析プラットフォーム"
)

# st.markdown(load_markdown('README.md'), unsafe_allow_html=True)

# YAMLからチャートリストを取得
dict_section = load_yaml("pages/page_list.yaml")


# Analysisセクションの取得
analysis_section = dict_section["Analysis"]
analysis_tiles = len(analysis_section)
# タイルの分割
rows = [st.columns(2) for _ in range(analysis_tiles // 2)]
if analysis_tiles % 2 == 1: # 奇数の場合、最後の行は1列
    rows.append([st.columns([1, 2, 1])[1]])  # 最後の行は1列
# タイルに挿入
tile_index = 0
for cols in rows:
    for col in cols:   
        tile = col.container()
        chart = analysis_section[tile_index]
        with tile:
            st.markdown(f"#### {chart['title']}")
            subcol1, subcol2, subcol3 = st.columns([1, 2, 1])
            subcol2.image(chart["image"], use_container_width=True)
            st.markdown(chart["description"])
            if st.button(f"Go to 「{chart['title']}」", key=chart["page"], use_container_width=True):
                st.switch_page(chart["page"])
        tile_index += 1

    

