import streamlit as st
import ftplib
import os
import xarray as xr
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
def get_dynamic_lwc(cltype):
    lwc_map = {1: 0.05, 2: 0.05, 3: 0.2, 4: 0.2, 5: 0.4, 6: 0.4}
    return lwc_map.get(cltype, 0.3)

def calculate_clobe_logic(tbb_k, cth_ft, cot, re_um, cltype):
    lwc = get_dynamic_lwc(cltype)
    rho_w, rho_i = 1.0e6, 0.92e6
    if tbb_k >= 273.15: rho = rho_w
    elif tbb_k <= 233.15: rho = rho_i
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

    now = datetime.utcnow()
    for i in range(2, 7):
        target_time = now - timedelta(minutes=i * 10)
        remote_dir = f"pub/himawari/L2/CLP/010/{target_time.strftime('%Y%m')}/{target_time.strftime('%d')}/{target_time.strftime('%H')}/"  
        try:
            ftp.cwd("/") 
            ftp.cwd(remote_dir)
            files = ftp.nlst()
            target_files = sorted([f for f in files if "JP000.nc.gz" in f])
            if target_files:
                latest_file = target_files[-1]
                if not os.path.exists(latest_file):
                    with open(latest_file, 'wb') as f:
                        ftp.retrbinary(f"RETR {latest_file}", f.write)
                ftp.quit()
                return latest_file
        except:
            continue
    ftp.quit()
    return None

st.title("CloBE - Cloud Base Estimation")
st.markdown("This tool estimates cloud base heights using the information from Himawari")
with st.sidebar:
    st.header("user information")
    user_id = st.text_input("P-Tree User ID", value="yama1028waki_gmail.com")
    password = st.text_input("Password", type="password")
    st.header("coordinates")
    target_lat = st.number_input("lat", value=38.1397, format="%.4f")
    target_lon = st.number_input("lon", value=140.9172, format="%.4f")
    buf = 0.02 
if st.button("run"):
    if not user_id or not password:
        st.warning("enter your user information")
    else:
        with st.spinner("bringing the data from JAXA"):
            filename = get_latest_file_from_ptree(user_id, password)
            if filename:
                try:
                    ds = xr.open_dataset(filename, mask_and_scale=True)
                    area = ds.sel(
                        latitude=slice(target_lat + buf, target_lat - buf), 
                        longitude=slice(target_lon - buf, target_lon + buf)
                    )
                    cltype_vals = area['CLTYPE'].values.flatten()
                    if len(cltype_vals) == 0 or np.isnan(cltype_vals).all():
                        st.error("There is NO cloud data (may be night)")
                    else:
                        res = {
                            'ctt': area['CLTT'].mean().item(),
                            'cth': area['CLTH'].mean().item() * 3.28084,
                            'cot': area['CLOT'].mean().item(),
                            'cer': area['CLER_23'].mean().item(),
                            'type': int(stats.mode(cltype_vals, keepdims=True).mode[0])
                        }
                        est_cbh = calculate_clobe_logic(res['ctt'], res['cth'], res['cot'], res['cer'], res['type'])
                        
                        st.success(f"succeeded: {filename}")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("estimated cloud base height", f"{est_cbh:,.0f} ft")
                            st.metric("cloud top height", f"{res['cth']:,.0f} ft")
                        with col2:
                            st.write(f"**cloud type number:** {res['type']}")
                            st.write(f"**cloud top tempereture:** {res['ctt']:.1f} K")
                            st.write(f"**cloud optical thickness:** {res['cot']:.2f}")
                            
                        st.info(f"used lwc: {get_dynamic_lwc(res['type'])} g/m³")
                    
                    ds.close()
                except Exception as e:
                    st.error(f"error: {e}")
            else:
                st.error("couldn't find the latest daytime data")
