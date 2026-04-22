import numpy as np
def get_dynamic_lwc(cltype):
    lwc_map = {
        1: 0.05,
        2: 0.05,
        3: 0.20,
        4: 0.20,
        5: 0.40,
        6: 0.40
    }
    return lwc_map.get(cltype, 0.3)
def calculate_clobe(tbb_k, cth_ft, cot, re_um, lwc):
    #cth_ft=cloud top height(ft), cot=cloud optical thickness, re_um=effective radius (micrometer)
    #lwc=liquid water content, rho_w=density (ρ) of water
    rho_w = 1.0e6
    rho_i = 0.92e6
    t_melt = 273.15
    t_glac = 233.15
    if tbb_k >= t_melt:
        rho = rho_w
    elif tbb_k <= t_glac:
        rho = rho_i
    else:
        ratio = (t_melt - tbb_k) / (t_melt - t_glac)
        rho = rho_w - (rho_w - rho_i) * ratio
    thickness_m = cot * (2/3) * (re_um * 1e-6) * (rho / lwc)
    thickness_ft = thickness_m * 3.28084
    cbh_ft = cth_ft - thickness_ft
    return max(0, cbh_ft)
if __name__ == "__main__":
    cloudtype = 1
    test_tbb_k = 249.46
    test_cth = 23000
    test_cot = 1.67
    test_re =46.97
    current_lwc = get_dynamic_lwc(cloudtype)
    result = calculate_clobe(test_tbb_k, test_cth, test_cot, test_re, current_lwc)
    print(f"入力雲頂高度: {test_cth}ft")
    print(f"推定された雲の厚さ: {test_cth - result:.0f}ft")
    print(f"CloBE推定雲底高度: {result:.0f}ft")
    print(f"METAR値: 15000ft")
