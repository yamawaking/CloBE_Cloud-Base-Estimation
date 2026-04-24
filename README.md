# CloBE
https://clobeontheweb.streamlit.app

CloBE- Cloud Base Estimation

CloBE (クローブ)- 雲底高度推定ツール

## Overview
　**CloBE**は、宇宙航空研究開発機構（JAXA）が提供する分野横断型プロダクト提供システム（P-Tree）を用いて、気象衛星ひまわりから得られた日本周辺の雲についての雲特性データ（輝度温度、雲頂高度、雲粒有効半径、光学的厚さ、雲形等）を元に、指定された座標周辺の上空にある雲の雲底高度を、計算により推定することを目指すpythonツールである。

## Logic
　CloBEが用いる雲底高度推定のロジックは以下の通りである。

　指定された座標周辺の雲について、その物理的厚さを、雲粒有効半径と光学的厚さ、雲形から推測した雲水混合比から推定し、雲頂高度からこれを差し引くことで、当該雲の雲底高度を近似する。

　気象衛星ひまわりの雲特性データから得られる雲の光学的厚さ（COT）と、CloBEが推定する雲の物理的厚さ（CPT）の関係は、以下のとおりである。なおzは鉛直方向の軸であり、βextは消散係数を示す。

### _COT = ∫[zbase→ztop] * βext dz ≒ βext * CPT_

　このとき、消散係数βextは、雲を構成する粒子の断面積とその分布から以下の左辺のように示すことができる。なお、rは粒子の半径を、Qextは消散効率をそれぞれ示す。Qextは2と近似することができるため、右辺のように表すことができる。

### _βext = ∫n(r) * Qext * πr^2 dr ≒ ∫n(r) * 2π_

　しかしながら、粒子の分布は気象衛星からの情報からは知りえない。そこで、CloBEは雲水混合比（LWC）を計算に用いる。LWCは、雲を構成する粒子の体積とその分布および粒子の密度（ρ）から、以下のように示すことができる。

### _LWC = ρ * ∫n(r) * 4/3πr^3 dr_

　βextを求めるにあたり、未知数であるnを計算式から取り除くため、これをLWCで除する。

### _βext / LWC = n * 2πr^2 / n * 4/3πr^3 * ρ_

### _= 2 / 4/3 * r *ρ = 3 / 2 * r * ρ_

　以上により、βwxtは以下のように求めることができる。

### _βext = 3/2 * LWC / ρ * r_

　これをCOTを求める式に代入すると、以下のようにしてCPTを求める式を作ることができる。なお、CloBEは、rとして雲粒有効半径を用い、ρを雲頂の輝度温度に基づいて、またLWCを雲形に基づいて、それぞれ推定することで、雲底高度を近似する。雲粒有効半径、輝度温度、および雲形は、気象衛星ひまわりから得られる雲特性データに含まれる。

### _COT = 3/2 * LWC / ρ * r * CPT_

### _CPT = COT * 2/3 * ρ * r / LWC_

## Verification
　雲底高度推定の妥当性向上のため、日本国内の飛行場における気象観測員である開発者（Kosei Yamawaki）は、その業務の傍ら、本プログラムについて精度の検証をおこなっている。職場には直上の雲のほぼ正確な雲底高度を計測するシーロメータがあるため、検証にはこれを用いている。検証により系統的誤差が認められた場合、それに応じて随時、プログラムの改善をおこなう。

## Notes
　使用にあたり以下の点に留意されたい。

1. CloBEが算出するのは、あくまで衛星データを用いた雲底高度の推定値、参考値であるに過ぎない。必ずしも正確、あるいはその近似値が導出されるとは限らない。

2. CloBEは、気象衛星が観測しうる特定の雲について、その雲の特性から厚さを求めることで雲底高度を推定する。*したがって、現状、雲層が複数ある場合は著しく機能が低下する*。

3. CloBEが雲底高度の推定のため用いる衛星データのうちほとんど全ては、現時点では日中時間帯のみ入手が可能である。したがって、CloBEも同様に*夜間帯に利用することはできない*。

4. なんらかの理由によってP-Treeから衛星データを取得することができない場合、CloBEは雲底高度の推定値を出すことはできない。

## References

Cloud property data that is used in the development of this tool is supplied by the P-Tree System, Japan Aerospace Exploration Agency (JAXA). The references of this service are below.

本ツールの開発にて使用する雲特性データは、宇宙航空研究開発機構（JAXA）の分野横断型プロダクト提供サービス（P-Tree）より提供を受けるものである。このサービスについての参考文献を以下に挙げる。

(Cloud Flag Algorithm)

Ishida, H., and T. Y. Nakajima, 2009: Development of an unbiased cloud detection algorithm for a spaceborne multispectral imager, J. Geophys. Res., 114, D07206, doi:10.1029/2008JD010710.

Ishida, H., T. Y. Nakajima, T. Yokota, N. Kikuchi, and H. Watanabe, 2011: Investigation of GOSAT TANSO-CAI cloud screening ability through an inter-satellite comparison, J. Appl. Meteor. Climatol., 50, 1571?1586. doi: http://dx.doi.org/10.1175/2011JAMC2672.1.

Letu, H., T. M. Nagao, T. Y. Nakajima, and Y. Matsumae, 2014: Method for validating cloud mask obtained from satellite measurements using ground-based sky camera. Applied optics, 53(31), 7523-7533.

Nakajima, T. Y., T. Tsuchiya, H. Ishida, and H. Shimoda, 2011: Cloud detection performance of spaceborne visible-to-infrared multispectral imagers. Applied Optics, 50, 2601-2616.

(Cloud Retrieval Algorithm)

Kawamoto, K., T. Nakajima, and T. Y. Nakajima, 2001: A Global Determination of Cloud Microphysics with AVHRR Remote Sensing, J. Clim., 14(9), 2054?2068, doi:10.1175/1520-0442(2001)014<2054:AGDOCM>2.0.CO;2.

Nakajima, T. Y., and T. Nakajima, 1995: Wide-Area Determination of Cloud Microphysical Properties from NOAA AVHRR Measurements for FIRE and ASTEX Regions, J. Atmos. Sci., 52(23), 4043?4059, doi:10.1175/1520-0469(1995)052<4043:WADOCM>2.0.CO;2.

(Scattering property database for nonspherical ice particles)

Ishimoto, H., K. Masuda., Y. Mano, N. Orikasa, and A. Uchiyama, 2012a, Optical modeling of irregularly shaped ice particles in convective cirrus. In radiation processed in the atmosphere and ocean (IRS2012): Proceedings of the International Radiation Symposium (IRC/IAMAS) 1531, 184-187.

Ishimoto, H., K. Masuda, Y. Mano, N. Orikasa, and A. Uchiyama, 2012b: Irregularly shaped ice aggregates in optical modeling of convectively generated ice clouds, J. Quant. Spectrosc. Radiat. Transfer, 113, 632?643.

Masuda, K., H. Ishimoto, and Y. Mano, 2012: Efficient method of computing a geometric optics integral for light scattering, Meteorology and Geophysics ., 63, 15?19.

Letu, H., T. Y. Nakajima, and T. N. Matsui, 2012: Development of an ice crystal scattering database for the global change observation mission/second generation global imager satellite mission: Investigating the refractive index grid system and potential retrieval error. Appl. Opt., 51, 6172-6178.

Letu, H. H. Ishimoto, J. Riedi, T. Y. Nakajima, L. C.-Labonnote, A. J. Baran, T. M. Nagao, and M. Sekiguchi, 2016: Investigation of ice particle habits to be used for ice cloud remote sensing for the GCOM-C satellite mission. Atmos. Chem. Phys, 16(18), 12287-12303.

Letu, H., T. M. Nagao, T. Y. Nakajima J. Riedi, H. Ishimoto, A. J. Baran, H. Shang, M. Sekiguchi, and M. Kikuchi: Ice cloud properties from Himawari-8/AHI next-generation geostationary satellite: Capability of the AHI to monitor the DC cloud generation process. IEEE Transactions on Geoscience and Remote Sensing, in revision.
