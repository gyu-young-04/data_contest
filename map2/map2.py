import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

plt.clf()
plt.close('all')

# ── 폰트 ──────────────────────────────────────────────────
fm.fontManager.addfont('/usr/share/fonts/truetype/nanum/NanumGothic.ttf')
fp = fm.FontProperties(fname='/usr/share/fonts/truetype/nanum/NanumGothic.ttf')
plt.rcParams['font.family'] = fp.get_name()
plt.rcParams['axes.unicode_minus'] = False


# =========================================================
# [1단계] CSV 불러오기
# =========================================================
# (이전 에러 해결을 위해 인코딩을 utf-8-sig 혹은 cp949로 맞춰서 읽어오도록 지정하는 것이 안전합니다)
csv_new = pd.read_csv('map_all_sig_exposure.csv', dtype={'sig_code': str})

# =========================================================
# [1.5단계] 정규화 + 가중치 계산 → exposure_index 생성
# =========================================================
def normalize(series):
    return (series - series.min()) / (series.max() - series.min()) * 100

csv_new['delivery_demand_norm']  = normalize(csv_new['delivery_demand'])
csv_new['card_consumption_norm'] = normalize(csv_new['card_consumption'])
csv_new['floating_pop_norm']     = normalize(csv_new['floating_pop'])
csv_new['single_household_norm'] = normalize(csv_new['single_household'])

csv_new['exposure_index'] = (
    csv_new['delivery_demand_norm']  * 0.35 +
    csv_new['card_consumption_norm'] * 0.25 +
    csv_new['floating_pop_norm']     * 0.25 +
    csv_new['single_household_norm'] * 0.15
).round(1)

csv_new.to_csv('map_all_sig_exposure.csv', index=False, encoding='utf-8-sig')
print(csv_new[['sig_code', 'sig_name', 'delivery_demand', 'card_consumption',
               'floating_pop', 'single_household', 'exposure_index']].head())


# =========================================================
# [2단계] SHP + CSV 병합
# =========================================================
sig_gdf = gpd.read_file("sig.shp")


# ── 대구만 필터링 (SIG_CD 앞 2자리 = 22) ──
sig_gdf = sig_gdf[sig_gdf['SIG_CD'].str.startswith('27')]


merged = sig_gdf.merge(csv_new, left_on='SIG_CD', right_on='sig_code', how='left')
merged = gpd.GeoDataFrame(merged, geometry='geometry')
print(f"\n매핑 완료: {merged['exposure_index'].notna().sum()} / {len(merged)}")

# =========================================================
# [3단계] 5분위 등급 색상
# =========================================================
q = merged['exposure_index'].quantile([0, 0.2, 0.4, 0.6, 0.8, 1.0]).values
COLORS = ['#FFF5F0', '#FCBBA1', '#FC7050', '#DE2D26', '#A50F15']
LABELS = ['1분위(최저)', '2분위', '3분위', '4분위', '5분위(최고)']

def get_color(val):
    if pd.isna(val): return '#CCCCCC'
    for i in range(4, -1, -1):
        if val >= q[i]: return COLORS[i]
    return COLORS[0]

merged['clr'] = merged['exposure_index'].apply(get_color)

# =========================================================
# [4단계] 시각화 (범례 지도 내장 및 지표 하단 가로 배치 버전)
# =========================================================
# 하단에 지표가 들어가므로 세로 비율을 조금 줄여 16:16 비율로 조정
fig = plt.figure(figsize=(16, 16), facecolor='#0D1117')

# [지도 패널]: 지도가 화면 대부분을 차지하도록 좌우 여백을 넓힘
ax = fig.add_axes([0.05, 0.16, 0.90, 0.78])
ax.set_facecolor('#0D1117')

# 배경 (전체 경계)
merged.plot(color='#1C2333', edgecolor='#2A3A55', linewidth=0.4, ax=ax)

# 노출도 색칠
for clr, grp in merged.groupby('clr'):
    gpd.GeoDataFrame(grp, geometry='geometry').plot(
        color=clr, edgecolor='#2A3A55', linewidth=0.3, ax=ax)

# ── Top 15 라벨 ──────────────────────────────────────────
top15 = merged.nlargest(15, 'exposure_index').dropna(subset=['exposure_index'])
for _, row in top15.iterrows():
    try:
        cx = row.geometry.centroid.x
        cy = row.geometry.centroid.y
        nm = row.get('sig_name', row['SIG_CD'])
        ax.annotate(
            f"{nm}\n{row['exposure_index']:.0f}",
            xy=(cx, cy), fontproperties=fp, fontsize=5.5,
            color='white', ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.2', fc='#DE2D26',
                      alpha=0.85, ec='none'))
    except:
        pass

ax.axis('off')
ax.set_title(
    '노출도 지수 (Exposure Index)  ·  시군구별',
    fontproperties=fm.FontProperties(fname='/usr/share/fonts/truetype/nanum/NanumGothic.ttf', size=24, weight='bold'),
    color='white', pad=18, loc='center')


# ── 1. 노출도 등급 범례 (지도 오른쪽 빈 바다 영역에 배경 없이 배치) ──
# 독립된 패널이 아니라 지도 내부(ax)의 오른쪽 상단(동해 바다 부근 빈 공간)에 텍스트와 도형을 직접 그립니다.
ax.text(0.82, 0.72, '노출도 등급', fontproperties=fp, color='#AABBCC',
        fontsize=11, weight='bold', transform=ax.transAxes)

for i, (lbl, clr) in enumerate(zip(LABELS, COLORS)):
    y_pos = 0.66 - i * 0.05  # 위에서 아래로 세로로 정렬
    # 배경 없이 투명하게 사각형 점만 찍음 (ec='none'으로 테두리도 제거 가능)
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.82, y_pos), 0.02, 0.03, boxstyle='round,pad=0.005',
        fc=clr, ec='#2A3A55', linewidth=0.5, transform=ax.transAxes))
    # 등급 텍스트 배치
    ax.text(0.85, y_pos + 0.015, lbl.replace('\n', ' '), fontproperties=fp, color='white',
            fontsize=9, va='center', transform=ax.transAxes)


# ── 2. 구성 지표 패널 (하단에 가로로 길게 배치) ─────────────────────
# 세로 높이(height)를 0.08로 슬림하게 만들고 가로로 길게 늘림
ax_info = fig.add_axes([0.05, 0.07, 0.90, 0.08])
ax_info.set_facecolor('#131B2E'); ax_info.axis('off')

# 하단 바(Bar) 형태의 깔끔한 테두리 카드 디자인
ax_info.add_patch(mpatches.FancyBboxPatch(
    (0, 0), 1, 1, boxstyle='round,pad=0.01',
    fc='#131B2E', ec='#1C2D4A', linewidth=0.6, transform=ax_info.transAxes, zorder=0))

# '구성 지표' 타이틀을 맨 왼쪽에 세로 중앙 정렬로 배치
ax_info.text(0.02, 0.5, '구성 지표', fontproperties=fp, color='#AABBCC',
             fontsize=10, transform=ax_info.transAxes, va='center', weight='bold')

items = [
    ('#FC7050', '배달앱 수요 밀도',   '가중치 35%  |  배달앱 카드사용금액 기준'),
    ('#FDB97C', '카드소비 집중도',    '가중치 25%  |  외식·생활서비스 업종'),
    ('#74C8F5', '유동인구 밀도',      '가중치 25%  |  야간·주말 유동인구 비중'),
    ('#B5EAD7', '1인가구 비율',       '가중치 15%  |  가구통계등록부 기준'),
]

# 4개의 지표를 가로로 배치하기 위해 x 좌표를 등간격(0.23씩 증가)으로 계산
for i, (clr, name, desc) in enumerate(items):
    x_pos = 0.11 + i * 0.225
    
    # 지표 색상 점 (●)
    ax_info.text(x_pos, 0.65, '●', color=clr, fontsize=10,
                 transform=ax_info.transAxes, va='center')
    # 지표 이름
    ax_info.text(x_pos + 0.015, 0.65, name, fontproperties=fp, color='white',
                 fontsize=9.5, transform=ax_info.transAxes, va='center', weight='bold')
    # 지표 세부 설명 (이름 아래에 배치)
    ax_info.text(x_pos + 0.015, 0.30, desc, fontproperties=fp, color='#6B7E99',
                 fontsize=7.5, transform=ax_info.transAxes, va='center')


# ── 3. 하단 통계 ─────────────────────────────────────────────
v = merged['exposure_index'].dropna()
ax_stat = fig.add_axes([0.05, 0.02, 0.90, 0.03])
ax_stat.set_facecolor('#0D1117'); ax_stat.axis('off')
ax_stat.text(0.5, 0.5,
    f"전국 시군구 {len(v)}개  |  평균 {v.mean():.1f}  |  "
    f"최고 {v.max():.0f}  |  최저 {v.min():.0f}  |  "
    f"상위 20% 기준값 {v.quantile(0.8):.1f}  |  "
    f"※ 현재 수치는 랜덤 시뮬레이션 (실제 데이터 교체 예정)",
    fontproperties=fp, color='#5A6A7E', fontsize=8.5,
    ha='center', va='center', transform=ax_stat.transAxes)

# 파일 저장
plt.savefig('exposure_index_map_daegu_shp.png',
            dpi=200, bbox_inches='tight', facecolor='#0D1117')
print("\n✅ 지도 저장 완료: exposure_index_map_daegu_shp.png")