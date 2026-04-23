import streamlit as st
import ftplib
import os
import xarray as xr
import numpy as np
from datetime import datetime, timedelta, timezone
from scipy import stats
import warnings
warnings.filterwarnings('ignore')
def get_dynamic_lwc(cltype):
    lwc_map = {1: 0.05, 2: 0.05, 3: 0.2, 4: 0.2, 5: 0.4, 6: 0.4}
    return lwc_map.get(cltype, 0.3)
def calculate_clobe_logic(tbb_k, cth_ft, cot, re_um, cltype):
    lwc = get_dynamic_lwc(cltype)
    rho_w, rho_i = 1.0e6, 0.92e6
    if tbb_k >= 273.15: 
        rho = rho_w
    elif tbb_k <= 233.15: 
        rho = rho_i
    else:
        ratio = (273.15 - tbb_k) / 40.0
        rho = rho_w - (rho_w - rho_i) * ratio
    thickness_ft = (cot * (2/3) * (re_um * 1e-6) * (rho / lwc)) * 3.28084
    return max(0, cth_ft - thickness_ft)
def get_latest_file_from_ptree(user, pw):
    ftp_host = "ftp.ptree.jaxa.jp"
    try:
        ftp = ftplib.FTP(ftp_host)
        ftp.login(user, pw)
    except Exception as e:
        st.error(f"FTP login error: {e}")
        return None
    now = datetime.now(timezone.utc)
    status_ui = st.empty()
    for i in range(0, 18):
        target_time = now - timedelta(minutes=i * 10)
        yyyymm = target_time.strftime('%Y%m')
        dd = target_time.strftime('%d')
        hh = target_time.strftime('%H')
        remote_dir = f"pub/himawari/L2/CLP/010/{yyyymm}/{dd}/{hh}/"
        status_ui.text(f"探索中... {hh}時台のフォルダを確認中")
        try:
            ftp.cwd("/")
            ftp.cwd(remote_dir)
            files = ftp.nlst()
            target_files = sorted([f for f in files if "FLDK" in f and f.endswith(".nc")], reverse=True)
            if target_files:
                latest_file = target_files[0]
                status_ui.text(f"found the latest file: {latest_file}")
                if not os.path.exists(latest_file):
                    with open(latest_file, 'wb') as f:
                        ftp.retrbinary(f"RETR {latest_file}", f.write)
                ftp.quit()
                return latest_file
        except:
            continue
    ftp.quit()
    return None
st.set_page_config(page_title="CloBE Estimator", layout="wide")
st.title("☁️ CloBE - Cloud Base Estimation System")
with st.sidebar:
    st.header("🔑 認証情報")
    u_id = st.text_input("P-Tree User ID", value="yama1028waki_gmail.com")
    u_pw = st.text_input("Password", type="password")
    st.header("📍 解析座標")
    t_lat = st.number_input("ターゲット緯度", value=38.1397, format="%.4f")
    t_lon = st.number_input("ターゲット経度", value=140.9172, format="%.4f")
    buf = st.slider("平均化範囲(度)", 0.01, 0.10, 0.02)
if st.button("analyze the latest data"):
    if not u_id or not u_pw:
        st.warning("enter your UID and PW")
    else:
        with st.spinner("loading"):
            filename = get_latest_file_from_ptree(u_id, u_pw)
            if filename:
                try:
                    ds = xr.open_dataset(filename, mask_and_scale=True)
                    area = ds.sel(
                        latitude=slice(t_lat + buf, t_lat - buf), 
                        longitude=slice(t_lon - buf, t_lon + buf)
                    )
                    cltype_raw = area['CLTYPE'].values.flatten()
                    valid_idx = ~np.isnan(cltype_raw)
                    if not np.any(valid_idx):
                        st.error(f"ファイルは取得できましたが、指定座標({t_lat}, {t_lon})に雲データがありません。快晴の可能性があります。")
                    else:
                        res = {
                            'ctt': float(np.nanmean(area['CLTT'].values)),
                            'cth_ft': float(np.nanmean(area['CLTH'].values)) * 3.28084 * 1000,
                            'cot': float(np.nanmean(area['CLOT'].values)),
                            'cer': float(np.nanmean(area['CLER_23'].values)),
                            'type': int(stats.mode(cltype_raw[valid_idx], keepdims=True).mode[0])
                        }
                        est_cbh = calculate_clobe_logic(res['ctt'], res['cth_ft'], res['cot'], res['cer'], res['type'])
                        st.success(f"succeeded: {filename}")
                        m1, m2, m3 = st.columns(3)
                        m1.metric("推定雲底高度 (CBH)", f"{est_cbh:,.0f} ft")
                        m2.metric("雲頂高度 (CTH)", f"{res['cth_ft']:,.0f} ft")
                        m3.metric("雲頂温度", f"{res['ctt']:.1f} K")
                        with st.expander("詳細な観測値"):
                            st.write(f"**判定雲形:** {res['type']}")
                            st.write(f"**光学的厚さ (COT):** {res['cot']:.2f}")
                            st.write(f"**実効粒子半径 (Re):** {res['cer']:.2f} μm")
                    ds.close()
                except Exception as e:
                    st.error(f"analyze error: {e}")
            else:
                st.error("JAXAサーバーから最新の有効データを見つけられませんでした。")
                st.info("【ヒント】JAXAのデータ生成は10分〜20分遅れます。また、夜間はデータが空になるため取得できません。")
