import numpy as np
def calculate_clobe(cth_ft, cot, re_um):
    #cth_ft=cloud top height(ft), cot=cloud optical thickness, re_um=effective radius (micrometer)
    #lwc=liquid water content, rho_w=density (ρ) of water
    lwc = 0.3
    rho_w = 1.0e6
    thickness_m = (cot * (2/3) * (re_um) * (rho_w) / lwc) / 1e6
    thickness_ft = thickness_m * 3.28084
    cbh_ft = cth_ft - thickness_ft
    return max(0, cbh_ft)
if __name__ == "__main__":
    test_cth = 28200
    test_cot = 2.0
    test_re = 20.0
    result = calculate_clobe(test_cth, test_cot, test_re)
    print(f"入力雲頂高度: {test_cth}ft")
    print(f"推定された雲の厚さ: {test_cth - result:.0f}ft")
    print(f"CloBE推定雲底高度: {result:.0f}ft")
    print(f"METAR値: 25000ft")
