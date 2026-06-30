import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np
import unicodedata
import re

# ── 0. 한글 폰트 ──────────────────────────────────────────────────────────
font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
font_name = fm.FontProperties(fname=font_path).get_name()
plt.rc('font', family=font_name)
plt.rcParams['axes.unicode_minus'] = False

# ── 1. 정규화 함수 ────────────────────────────────────────────────────────
def clean_name(s):
    s = str(s)
    s = unicodedata.normalize('NFC', s)
    s = re.sub(r'[\r\n\t\xa0\u3000\u200b]', ' ', s)
    s = re.sub(r' +', ' ', s).strip()
    return s

# ── 2. 매핑 테이블 ────────────────────────────────────────────────────────
csv_ref = pd.read_csv("map_all_sig.csv", dtype={'sig_code': str})
csv_ref['sig_code'] = csv_ref['sig_code'].str.zfill(5)
csv_ref['sig_name_clean'] = csv_ref['sig_name'].apply(clean_name)
name_to_code = dict(zip(csv_ref['sig_name_clean'], csv_ref['sig_code']))

bucheon_code = name_to_code.get('부천시')
if bucheon_code:
    for sub in ['부천시 소사구', '부천시 오정구', '부천시 원미구']:
        name_to_code[sub] = bucheon_code

# ── 3. 엑셀 로드 (all_rate.xlsx — 종합 지수) ─────────────────────────────
EXCEL_PATH = "all_rate.xlsx"

# 기존 4개 지수 제외하고, 새로 존재하는 종합 지수만 사용
sheet_info = {
    "종합_취약성":            ("Sheet1", "종합_취약성",            "Purples"),
    "총_플랫폼_노동_취약성_지수": ("Sheet1", "총_플랫폼_노동_취약성_지수", "RdPu"),
}

data_dict = {}
for label, (sheet, col, cmap) in sheet_info.items():
    df = pd.read_excel(EXCEL_PATH, sheet_name=sheet)
    df = df[['기준연도', '시군구명', col]].copy()
    df.columns = ['year', 'sig_name', 'value']
    df['year'] = df['year'].astype(int)
    df['sig_name_clean'] = df['sig_name'].apply(clean_name)
    df['sig_code'] = df['sig_name_clean'].map(name_to_code)

    unmatched = df[df['sig_code'].isna()]['sig_name'].unique()
    if len(unmatched) > 0:
        print(f"[{label}] 매핑 실패: {unmatched}")
    else:
        print(f"[{label}] ✅ 전체 매핑 성공")

    data_dict[label] = (df, cmap)

# ── 4. 지리 데이터 (서울 11xxx + 경기 41xxx만) ───────────────────────────
sig_gdf = gpd.read_file("sig.shp")
sig_gdf['SIG_CD'] = sig_gdf['SIG_CD'].astype(str).str.zfill(5)
sig_gdf = sig_gdf.set_crs(epsg=5179)

target_gdf = sig_gdf[
    sig_gdf['SIG_CD'].str.startswith('11') |
    sig_gdf['SIG_CD'].str.startswith('41')
].copy()

b = target_gdf.total_bounds
pad = 15000
COMMON_XLIM = (b[0] - pad, b[2] + pad)
COMMON_YLIM = (b[1] - pad, b[3] + pad)

YEARS = [2022, 2023, 2024]
SOURCE_TEXT = "본 지수는 상대적 취약성 지표이며, 지역 간 상대적 순위 해석에 활용"

# ── 5. 지수별 개별 저장 ───────────────────────────────────────────────────
for label, (df_all, cmap_name) in data_dict.items():
    plt.clf()
    plt.close('all')

    vmin = np.percentile(df_all['value'].dropna(), 5)
    vmax = np.percentile(df_all['value'].dropna(), 95)
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

    fig = plt.figure(figsize=(18, 10))
    fig.patch.set_facecolor('white')
    fig.suptitle(f"플랫폼 노동 취약성 지수 - {label} (2022–2024)",
                 fontsize=16, fontweight='bold', y=0.97)

    ax_main = [fig.add_axes([0.03 + i * 0.315, 0.15, 0.28, 0.75]) for i in range(3)]

    for col_idx, year in enumerate(YEARS):
        ax = ax_main[col_idx]

        df_year = (df_all[df_all['year'] == year][['sig_code', 'value']]
                   .dropna(subset=['sig_code']))
        matched = set(df_year['sig_code'].values)

        has_data = target_gdf[target_gdf['SIG_CD'].isin(matched)].merge(
            df_year, left_on='SIG_CD', right_on='sig_code', how='left'
        )

        if not has_data.empty:
            has_data.plot(
                ax=ax,
                column='value',
                cmap=cmap_name,
                norm=norm,
                edgecolor='white',
                linewidth=0.5,
                legend=False
            )

        ax.set_xlim(COMMON_XLIM)
        ax.set_ylim(COMMON_YLIM)
        ax.set_facecolor('white')
        ax.set_title(f"{year}년", fontsize=14, fontweight='bold',
                     loc='center', pad=8)
        ax.axis('off')

    sm = plt.cm.ScalarMappable(cmap=cmap_name, norm=norm)
    sm.set_array([])
    cbar_ax = fig.add_axes([0.33, 0.07, 0.34, 0.025])
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation='horizontal')
    cbar.ax.tick_params(labelsize=9)
    cbar_ax.set_title(label, fontsize=11, pad=6)

    fig.text(0.5, 0.02, SOURCE_TEXT,
             ha='center', va='bottom', fontsize=7.5, color='#666666')

    filename = f"heatmap_{label}.png"
    plt.savefig(filename, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✅ 저장: {filename}")

print("\n🎉 전체 완료!")