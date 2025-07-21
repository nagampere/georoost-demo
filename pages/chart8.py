import streamlit as st
import pandas as pd
import re
import pydeck as pdk
import geopandas as gpd

# キャッシュのリセット
if st.session_state.get("current_page") != "chart8":
    # 他のページから来た場合、キャッシュをクリア
    st.cache_data.clear()
    st.session_state.clear()
    st.session_state["current_page"] = "chart8"

def dms_to_decimal_by_point(dms_str): # 例: 139.44.43.55 → 139.7454316
    parts = list(map(float, dms_str.split('.')))
    degrees = parts[0]
    minutes = parts[1]
    seconds = parts[2] + parts[3] / 100
    # miliseconds = 
    return degrees + minutes / 60 + seconds / 3600

def dms_to_decimal_by_space(dms_str): # 例: 139 44 43 55 → 139.7454316
    parts = list(map(float, dms_str.split(' ')))
    degrees = parts[0]
    minutes = parts[1]
    seconds = parts[2] + parts[3] / 100  
    return degrees + minutes / 60 + seconds / 3600

def dms_to_decimal_type_float(dms_str): # 例: 139°44′43.91″ → 139.7454316
    match = re.match(r"(\d+)°(\d+)′([\d.]+)″", dms_str)
    if not match:
        raise ValueError("Invalid DMS format")
    degrees, minutes, seconds = map(float, match.groups())
    return degrees + minutes / 60 + seconds / 3600

def dms_to_decimal_type_split(dms_str): # 例: 139°44′43″55 → 139.7454316
    match = re.match(r"(\d+)°(\d+)′(\d+)″(\d+)", dms_str)
    if not match:
        raise ValueError("Invalid DMS format")
    deg, minute, sec, sec_decimal = match.groups()
    degrees = float(deg)
    minutes = float(minute)
    seconds = float(sec) + float("0.", sec_decimal) 
    return degrees + minutes / 60 + seconds / 3600

def dms_to_decimal_by_jpn(dms_str): # 例: 139度44分43.91秒 → 139.7454316
    match = re.match(r"(\d+(?:\.\d+)?)度(\d+(?:\.\d+)?)分(\d+(?:\.\d+)?)秒", dms_str)
    if not match:
        raise ValueError("Invalid Japanese DMS format")
    degrees, minutes, seconds = map(float, match.groups())
    return degrees + minutes / 60 + seconds / 3600

epsg_dict = {
    "日本測地系2011(JGD2011)地理座標系": "EPSG:6668",
    "日本測地系2000(JGD2000)地理座標系": "EPSG:4612",
    "旧日本測地系(TOKYO Datum)": "EPSG:4301",
    "WGS84地理座標系": "EPSG:4326",
    "WEBメルカトル座標系": "EPSG:3857",
    "日本測地系2011（JGD2011）平面直角座標系第I系": "EPSG:6669",
    "日本測地系2011（JGD2011）平面直角座標系第II系": "EPSG:6670",
    "日本測地系2011（JGD2011）平面直角座標系第III系": "EPSG:6671",
    "日本測地系2011（JGD2011）平面直角座標系第IV系": "EPSG:6672",
    "日本測地系2011（JGD2011）平面直角座標系第V系": "EPSG:6673",
    "日本測地系2011（JGD2011）平面直角座標系第VI系": "EPSG:6674",
    "日本測地系2011（JGD2011）平面直角座標系第VII系": "EPSG:6675",
    "日本測地系2011（JGD2011）平面直角座標系第VIII系": "EPSG:6676",
    "日本測地系2011（JGD2011）平面直角座標系第IX系": "EPSG:6677",
    "日本測地系2011（JGD2011）平面直角座標系第X系": "EPSG:6678",
    "日本測地系2011（JGD2011）平面直角座標系第XI系": "EPSG:6679",
    "日本測地系2011（JGD2011）平面直角座標系第XII系": "EPSG:6680",
    "日本測地系2011（JGD2011）平面直角座標系第XIII系": "EPSG:6681",
    "日本測地系2011（JGD2011）平面直角座標系第XIV系": "EPSG:6682",
    "日本測地系2011（JGD2011）平面直角座標系第XV系": "EPSG:6683",
    "日本測地系2011（JGD2011）平面直角座標系第XVI系": "EPSG:6684",
    "日本測地系2011（JGD2011）平面直角座標系第XVII系": "EPSG:6685",
    "日本測地系2011（JGD2011）平面直角座標系第XVIII系": "EPSG:6686",
    "日本測地系2011（JGD2011）平面直角座標系第XIX系": "EPSG:6687",
    "日本測地系2011UTM座標系51(東経120-126)": "EPSG:6688",
    "日本測地系2011UTM座標系52(東経126-132)": "EPSG:6689",
    "日本測地系2011UTM座標系53(東経132-138)": "EPSG:6690",
    "日本測地系2011UTM座標系54(東経138-144)": "EPSG:6691",
    "日本測地系2011UTM座標系55(東経144-150)": "EPSG:6692",
    "日本測地系2000（JGD2000）平面直角座標系第I系": "EPSG:2443",
    "日本測地系2000（JGD2000）平面直角座標系第II系": "EPSG:2444",
    "日本測地系2000（JGD2000）平面直角座標系第III系": "EPSG:2445",
    "日本測地系2000（JGD2000）平面直角座標系第IV系": "EPSG:2446",
    "日本測地系2000（JGD2000）平面直角座標系第V系": "EPSG:2447",
    "日本測地系2000（JGD2000）平面直角座標系第VI系": "EPSG:2448",
    "日本測地系2000（JGD2000）平面直角座標系第VII系": "EPSG:2449",
    "日本測地系2000（JGD2000）平面直角座標系第VIII系": "EPSG:2450",
    "日本測地系2000（JGD2000）平面直角座標系第IX系": "EPSG:2451",
    "日本測地系2000（JGD2000）平面直角座標系第X系": "EPSG:2452",
    "日本測地系2000（JGD2000）平面直角座標系第XI系": "EPSG:2453",
    "日本測地系2000（JGD2000）平面直角座標系第XII系": "EPSG:2454",
    "日本測地系2000（JGD2000）平面直角座標系第XIII系": "EPSG:2455",
    "日本測地系2000（JGD2000）平面直角座標系第XIV系": "EPSG:2456",
    "日本測地系2000（JGD2000）平面直角座標系第XV系": "EPSG:2457",
    "日本測地系2000（JGD2000）平面直角座標系第XVI系": "EPSG:2458",
    "日本測地系2000（JGD2000）平面直角座標系第XVII系": "EPSG:2459",
    "日本測地系2000（JGD2000）平面直角座標系第XVIII系": "EPSG:2460",
    "日本測地系2000（JGD2000）平面直角座標系第XIX系": "EPSG:2461",
    "日本測地系2000UTM座標系51(東経120-126)": "EPSG:3097",
    "日本測地系2000UTM座標系52(東経126-132)": "EPSG:3098",
    "日本測地系2000UTM座標系53(東経132-138)": "EPSG:3099",
    "日本測地系2000UTM座標系54(東経138-144)": "EPSG:3100",
    "日本測地系2000UTM座標系55(東経144-150)": "EPSG:3101",
}

# Streamlit UI 設定
st.title("測地系の変換")

# CSVファイルのアップロード
st.write("### CSVファイルのアップロード")
uploaded_file = st.file_uploader("CSVファイルを選択してください", type=["csv"])

if uploaded_file is None:
    load_df = pd.DataFrame({
        '駅名': ["新宿", "新宿西口", "都庁前", "新宿三丁目", "新宿御苑前"],
        "緯度": [35.6896, 35.6933, 35.6898, 35.6929, 35.6865],
        "経度": [139.7006, 139.6970, 139.6919, 139.7066, 139.7106]
    })
    cvt_df = load_df.copy()
    lat_col = "緯度"
    lon_col = "経度"
    dms_format = "dd"
    st.write("デフォルトのサンプルデータを使用しています。")
    st.dataframe(load_df)

    # 変化前の緯度経度のEPSGを入力
    epsg_code_before = "日本測地系2000(JGD2000)地理座標系"  # デフォルトでJGD2000を選択
    st.write("変換前の測地系(EPSG)は日本測地系2000(JGD2000)地理座標系です。")
    # 変化後の緯度経度のEPSGを入力
    epsg_code_after = st.selectbox("変換後の測地系(EPSG)を選択してください", epsg_dict.keys(), format_func=lambda x: f"{x} ({epsg_dict[x]})", index=3)

else:
    # CSVファイルを読み込む
    st.session_state["load_df"] = pd.read_csv(uploaded_file)
    load_df = st.session_state["load_df"]

    # CSVファイルの内容を表示
    st.write("アップロードされたCSVファイルの内容:")
    st.dataframe(load_df)

    # 緯度経度のカラム名と表記方法を選択
    list_columns = load_df.columns.tolist()
    st.write("### 緯度経度のカラム名と表記方法を選択")
    lat_col = st.selectbox("緯度のカラム名を選択", list_columns)
    lon_col = st.selectbox("経度のカラム名を選択", list_columns)
    dms_format = st.selectbox("緯度経度の表記方法を選択", ["dd", "dd.mm.ss.sss", "dd mm ss sss", "dd° mm' ss.sss\"", "dd° mm' ss\" sss", "dd度 mm分 ss.sss秒"])
    
    # 緯度経度の表記方法に応じて変換
    if dms_format == "dd.mm.ss.sss":
        load_df[lat_col] = load_df[lat_col].apply(dms_to_decimal_by_point)
        load_df[lon_col] = load_df[lon_col].apply(dms_to_decimal_by_point)
    elif dms_format == "dd mm ss sss":
        load_df[lat_col] = load_df[lat_col].apply(dms_to_decimal_by_space)
        load_df[lon_col] = load_df[lon_col].apply(dms_to_decimal_by_space)
    elif dms_format == "dd° mm' ss.sss\"":
        load_df[lat_col] = load_df[lat_col].apply(dms_to_decimal_type_float)
        load_df[lon_col] = load_df[lon_col].apply(dms_to_decimal_type_float)
    elif dms_format == "dd° mm' ss\" sss":
        load_df[lat_col] = load_df[lat_col].apply(dms_to_decimal_type_split)
        load_df[lon_col] = load_df[lon_col].apply(dms_to_decimal_type_split)
    elif dms_format == "dd度 mm分 ss.sss秒":
        load_df[lat_col] = load_df[lat_col].apply(dms_to_decimal_by_jpn)
        load_df[lon_col] = load_df[lon_col].apply(dms_to_decimal_by_jpn)
    else:
        load_df[lat_col] = load_df[lat_col].astype(float)
        load_df[lon_col] = load_df[lon_col].astype(float)
    
    cvt_df = load_df.copy()
    
    # 緯度経度のカラム名の変換
    st.write("### 緯度経度の測地系(EPSG)を変換")
    # 選択したカラムのデータ型がどちらかにstrであるとき、度分秒表記から度数表記に変換
    # 測地系とEPSGのdict
    
    # 変化前の緯度経度のEPSGを入力
    epsg_code_before = st.selectbox("変換前の測地系(EPSG)を選択してください", epsg_dict.keys(), format_func=lambda x: f"{x} ({epsg_dict[x]})", index=2)
    # 変化後の緯度経度のEPSGを入力
    epsg_code_after = st.selectbox("変換後の測地系(EPSG)を選択してください", epsg_dict.keys(), format_func=lambda x: f"{x} ({epsg_dict[x]})", index=0)


if epsg_code_before and epsg_code_after:
    # 緯度経度のEPSGを変換
    cvt_df[lat_col] = gpd.GeoSeries.from_xy(load_df[lon_col], load_df[lat_col], crs=epsg_dict[epsg_code_before]).to_crs(epsg_dict[epsg_code_after]).y
    cvt_df[lon_col] = gpd.GeoSeries.from_xy(load_df[lon_col], load_df[lat_col], crs=epsg_dict[epsg_code_before]).to_crs(epsg_dict[epsg_code_after]).x
    st.write("緯度経度の測地系(EPSG)を変換しました。")
    st.dataframe(cvt_df)
else:
    st.write("変換前の測地系(EPSG)と変換後の測地系(EPSG)を入力してください。")



# データフレームをマップ上に表示
st.write("### マップ上に可視化")
if epsg_code_after == "WGS84地理座標系":
    st.write("変換後の測地系(EPSG)はWGS84地理座標系です。マップ上に表示します。")
else:
    st.write("変換後の測地系(EPSG)はWGS84地理座標系ではありません。マップ上に表示するために、WGS84地理座標系に変換します。")
    cvt_df[lat_col] = gpd.GeoSeries.from_xy(cvt_df[lon_col], cvt_df[lat_col], crs=epsg_dict[epsg_code_after]).to_crs("EPSG:4326").y
    cvt_df[lon_col] = gpd.GeoSeries.from_xy(cvt_df[lon_col], cvt_df[lat_col], crs=epsg_dict[epsg_code_after]).to_crs("EPSG:4326").x
    
    
# 中心座標を取得
center_lat = cvt_df[lat_col].median()
center_lon = cvt_df[lon_col].median()

layer = pdk.Layer(
    "ScatterplotLayer",
    data =cvt_df,
    get_position=[lon_col, lat_col],
    get_color=[255, 0, 0, 140],  # 赤色
    pickable=True,
    radius_scale=20,
    auto_highlight=True,
)

# Pydeckのマップの作成
deck = pdk.Deck(
    layers=[layer],
    initial_view_state=pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=12, pitch=0),
    map_style='mapbox://styles/mapbox/light-v10'  # ベースマップを白に変更
)

# Streamlitアプリの描画
st.pydeck_chart(deck)


# ホームに戻るボタン
st.markdown("---")  # 区切り線
if st.button("⬅ Back to Home"): st.switch_page("pages/home.py")
