"""
플랫폼 노동 취약성 분석 - 노출도(Exposure) 지수화 및 지도 시각화
=================================================================
데이터센터 반출: 결과 CSV + 지도 PNG 저장

데이터 구조 (배달앱 매출 통합카드):
  CRTR_YM               : 기준연월 (YYYYMM)
  FRCS_ADCLSF_CTPV_CD   : 시도코드
  FRCS_ADCLSF_SGG_CD    : 시군구코드
  FRCS_ADCLSF_CTPV_NM   : 시도명
  FRCS_ADCLSF_SGG_NM    : 시군구명
  DLVR_TPBIZ_CD         : 배달업종코드
  CARD_USE_NOCS         : 카드사용건수
  CARD_USE_AMT          : 카드사용금액
  PP1_AVG_CARD_USE_AMT  : 1인당 평균 카드사용금액
"""

# 피쳐 1 — 총주문건수 (배달 수요 절대량)
# 그 지역에서 배달앱으로 결제된 총 횟수
# 숫자가 클수록 라이더가 많이 필요한 지역 = 플랫폼 노동 수요가 큰 지역

# 피쳐 2 - 총주문금액 (시장 규모) (단가가 높은지역 잡기)
# 건수는 비슷해도 금액이 크면 → 고가 배달 시장 → 라이더 단가 수입은 높지만 진입 경쟁도 셈

# 피쳐 3 — 1인당 평균 주문금액 (서비스 단가)
#건당 평균 결제금액. 
# 취약성 분석에서는 이 값이 낮을수록 라이더 한 건당 수입이 적다는 뜻이라 노출 취약성과 연결됨.
# 예) 평균 1만원짜리 배달 vs 3만원짜리 배달 → 같은 건수여도 수입 3배 차이

# 피쳐 4 - 업종 다양성 (Shannon 엔트로피)
#배달 업종이 얼마나 다양하게 분포하는지. 공식은 정보이론의 Shannon 엔트로피.
#예를 들어 업종이 3개(치킨/피자/중식)일 때 비율이 균등하다면 다양성이 높다고 할수있음
#취약성 관점에서는 다양성이 높을수록 라이더가 여러 업종으로 분산되어 
# 특정 업종 침체 시 타격이 크고, 경쟁도 치열해서 노출 취약성이 높다고 해석해요.

import os   #파일 경로 탐색
import glob #파일 경로 탐색
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib import font_manager
import geopandas as gpd #SHP 파일 읽어서 지도 그리기
from sklearn.preprocessing import StandardScaler # 표준화
from sklearn.cluster import KMeans #클러스터링
from sklearn.decomposition import PCA #주성분 분석
from scipy.stats import mstats #극단치 처리

warnings.filterwarnings("ignore")


#  경로 설정 (센터 환경에 맞게 수정해야함)
DATA_DIR    = "./csv"       # 배달앱 매출 xlsx 파일들이 있는 폴더
SHAPEFILE   = "./sig.shp"         # 시군구 경계 shp (SGIS 다운로드)
OUTPUT_DIR  = "./result"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 한글 폰트 (센터 환경에 맞게 경로 수정, 없으면 자동 탐색)
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "C:/Windows/Fonts/malgun.ttf",
    "/Library/Fonts/AppleGothic.ttf",
]
for fp in FONT_CANDIDATES:
    if os.path.exists(fp):
        font_manager.fontManager.addfont(fp)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=fp).get_name()
        break
plt.rcParams["axes.unicode_minus"] = False


N_CLUSTERS  = 4     # K-Means 클러스터 수
YEAR_TARGET = None  # None이면 전체 연도 사용, ex) 2024면 2024년만


# ─────────────────────────────────────────────────────────────────────────────
# 1. 데이터 로드
# ─────────────────────────────────────────────────────────────────────────────

def load_delivery_data(data_dir: str) -> pd.DataFrame:
    """
    폴더 내 모든 xlsx 파일을 읽어 하나의 DataFrame으로 합침.
    헤더가 5번째 행(0-indexed=4)에 있는 구조 기준.
    """
    files = glob.glob(os.path.join(data_dir, "**/*.xlsx"), recursive=True)
    if not files:
        files = glob.glob(os.path.join(data_dir, "*.xlsx"))
    print(f"[로드] {len(files)}개 파일 발견")


    dfs = []
    for f in files:
        try:
            df = pd.read_excel(f, header=5) #파일 구조상 앞 설명행이 있기에
            df = df.drop(columns=[c for c in df.columns if "Unnamed" in str(c)], errors="ignore")
            # 엑셀의 빈 열이 자동으로 읽히는것을 제거
            dfs.append(df)
        except Exception as e:
            print(f"  ⚠ 로드 실패: {f} → {e}")

    if not dfs:
        raise FileNotFoundError(f"{data_dir} 에서 xlsx 파일을 찾을 수 없습니다.")
    return pd.concat(dfs, ignore_index=True)    #여러 파일을 하나로


# ─────────────────────────────────────────────────────────────────────────────
# 2. 전처리
# ─────────────────────────────────────────────────────────────────────────────

def preprocess(df: pd.DataFrame, year: int = None) -> pd.DataFrame:
    col_map = {
        "CRTR_YM":                "기준연월",
        "FRCS_ADCLSF_CTPV_CD":   "시도코드",
        "FRCS_ADCLSF_SGG_CD":    "시군구코드",
        "FRCS_ADCLSF_CTPV_NM":   "시도명",
        "FRCS_ADCLSF_SGG_NM":    "시군구명",
        "DLVR_TPBIZ_CD":         "배달업종코드",
        "CARD_USE_NOCS":         "카드사용건수",
        "CARD_USE_AMT":          "카드사용금액",
        "PP1_AVG_CARD_USE_AMT":  "1인당평균금액",
    }
    df = df.rename(columns=col_map)

    # 타입 변환 (숫자로 바꾸지 못하면 NaN 처리해서 에러가 없어지게함)
    df["기준연월"]   = pd.to_numeric(df["기준연월"],   errors="coerce") 
    df["시군구코드"]  = pd.to_numeric(df["시군구코드"],  errors="coerce").astype("Int64")
    df["카드사용건수"] = pd.to_numeric(df["카드사용건수"], errors="coerce")
    df["카드사용금액"] = pd.to_numeric(df["카드사용금액"], errors="coerce")
    df["1인당평균금액"] = pd.to_numeric(df["1인당평균금액"], errors="coerce")
    df = df.dropna(subset=["기준연월", "시군구코드", "카드사용건수"])

    df["연도"] = (df["기준연월"] // 100).astype(int)

    if year is not None:
        df = df[df["연도"] == year]
        print(f"[전처리] {year}년 데이터만 사용: {len(df)}행")
    else:
        print(f"[전처리] 전체 데이터 사용: {len(df)}행")

    return df


# ─────────────────────────────────────────────────────────────────────────────
# 3. 노출도 지표 계산
# ─────────────────────────────────────────────────────────────────────────────

def calc_exposure_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    시군구별 노출도 구성 지표 4가지:
      E1. 배달 주문 총건수           → 플랫폼 노동 수요 절대량
      E2. 배달 주문 총금액           → 시장 규모
      E3. 1인당 평균 주문금액        → 서비스 단가 (낮을수록 건당 수입 적음)
      E4. 업종 다양성 (Shannon 지수) → 다양한 업종 = 노동 수요 분산
    """
    grp = df.groupby(["시군구코드", "시도명", "시군구명"])

    # E1, E2
    agg = grp.agg(
        E1_총주문건수=("카드사용건수", "sum"),
        E2_총주문금액=("카드사용금액", "sum"),
        E3_1인당평균금액=("1인당평균금액", "mean"),
    ).reset_index()

    # E4: Shannon 다양성 (업종)
    def shannon(sub):
        counts = sub.groupby("배달업종코드")["카드사용건수"].sum()
        p = counts / counts.sum()
        return -(p * np.log(p + 1e-9)).sum()

    diversity = df.groupby("시군구코드").apply(shannon).reset_index()
    diversity.columns = ["시군구코드", "E4_업종다양성"]

    feat = agg.merge(diversity, on="시군구코드", how="left")
    print(f"[지표] 시군구 수: {len(feat)}")
    return feat


# ─────────────────────────────────────────────────────────────────────────────
# 4. 노출도 지수화 (표준화 → PCA → 종합 지수)
# ─────────────────────────────────────────────────────────────────────────────

def calc_exposure_index(feat: pd.DataFrame) -> pd.DataFrame:
    feature_cols = ["E1_총주문건수", "E2_총주문금액", "E3_1인당평균금액", "E4_업종다양성"]


    # 윈저라이징: 상위/하위 5% 극단값을 경계값으로 대체
    # 서울이 다른 지역의 100배면 지수가 서울 하나에 쏠리는걸 방지
    for col in feature_cols:
        feat[col] = mstats.winsorize(feat[col].fillna(0), limits=[0.05, 0.05])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(feat[feature_cols])

    # ★ n_components를 샘플 수와 피처 수 중 작은 값으로 제한
    n_components = min(len(feat), len(feature_cols))
    pca = PCA(n_components=n_components)
    pca.fit(X_scaled)
    weights = pca.explained_variance_ratio_
    pc_scores = pca.transform(X_scaled)
    exposure_raw = np.dot(pc_scores, weights)

    mn, mx = exposure_raw.min(), exposure_raw.max()
    # ★ 분모가 0이면 (샘플 1개 등) 그냥 50으로

    #정규화
    if mx == mn:
        feat["노출도지수"] = 50.0
    else:
        feat["노출도지수"] = (exposure_raw - mn) / (mx - mn) * 100

    print("\n[PCA] 각 주성분 설명력:")
    for i, ev in enumerate(pca.explained_variance_ratio_):
        print(f"  PC{i+1}: {ev:.3f} ({ev*100:.1f}%)")

    # ★ 실제 n_components 기준으로 DataFrame 생성
    loading_df = pd.DataFrame(
        pca.components_.T,
        index=feature_cols,
        columns=[f"PC{i+1}" for i in range(n_components)]  # ← 여기가 핵심
    )
    print("\n[PCA 로딩 행렬]")
    print(loading_df.round(3).to_string())

    return feat, loading_df


# ─────────────────────────────────────────────────────────────────────────────
# 5. K-Means 클러스터링 (지역 유형화)
# ─────────────────────────────────────────────────────────────────────────────

def cluster_regions(feat: pd.DataFrame, n_clusters: int = 4) -> pd.DataFrame:
    feature_cols = ["E1_총주문건수", "E2_총주문금액", "E3_1인당평균금액", "E4_업종다양성"]
    X = StandardScaler().fit_transform(feat[feature_cols].fillna(0))
    n_clusters = min(n_clusters, len(feat))
    #실행할때마다 같은결과가 나오게
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10) 
    feat["클러스터"] = km.fit_predict(X)

    # 클러스터별 노출도 평균으로 라벨링
    cluster_mean = feat.groupby("클러스터")["노출도지수"].mean().sort_values(ascending=False)
    rank_map = {c: i for i, c in enumerate(cluster_mean.index)}
    feat["노출유형"] = feat["클러스터"].map(rank_map)

    type_labels = {0: "🔴 초고노출", 1: "🟠 고노출", 2: "🟡 중노출", 3: "🟢 저노출"}
    feat["노출유형명"] = feat["노출유형"].map(type_labels)

    print("\n[클러스터] 유형별 통계:")
    print(feat.groupby("노출유형명")["노출도지수"].describe().round(2).to_string())
    return feat


# ─────────────────────────────────────────────────────────────────────────────
# 6. 시각화: 노출도 Choropleth + 클러스터 지도
# ─────────────────────────────────────────────────────────────────────────────

def plot_maps(feat: pd.DataFrame, shp_path: str, output_dir: str):
    gdf = gpd.read_file(shp_path, encoding="cp949")
    gdf["시군구코드"] = pd.to_numeric(gdf["SIG_CD"], errors="coerce").astype("Int64")
    merged = gdf.merge(feat, on="시군구코드", how="left")

    # ── 왼쪽: 노출도 지수 Choropleth ──────────────────────────────────
    fig1, ax1 = plt.subplots(1, 1, figsize=(12, 12))  # ← 분리
    merged.plot(
        column="노출도지수",
        ax=ax1,
        cmap="YlOrRd",
        legend=True,
        legend_kwds={"label": "노출도 지수 (0~100)", "orientation": "vertical", "shrink": 0.6},
        missing_kwds={"color": "#eeeeee", "label": "데이터 없음"},
        linewidth=0.3,
        edgecolor="gray",
    )
    ax1.set_title("플랫폼 노동 노출도 지수\n(배달앱 매출 기반)", fontsize=16, fontweight="bold", pad=15)
    ax1.axis("off")

    top5 = merged.nlargest(5, "노출도지수").dropna(subset=["geometry"])
    for _, row in top5.iterrows():
        cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
        ax1.annotate(
            f"{row['시군구명']}\n{row['노출도지수']:.1f}",
            xy=(cx, cy), fontsize=7, ha="center", color="black",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.7),
        )

    out1 = os.path.join(output_dir, "exposure_choropleth.png")  # ← 파일명 분리
    plt.savefig(out1, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"[저장] 노출도 지도 → {out1}")

    # ── 오른쪽: K-Means 클러스터 지도 ────────────────────────────────
    fig2, ax2 = plt.subplots(1, 1, figsize=(12, 12))  # ← 분리
    cluster_colors = {0: "#d32f2f", 1: "#f57c00", 2: "#fbc02d", 3: "#388e3c"}
    merged["cluster_color"] = merged["노출유형"].map(cluster_colors).fillna("#cccccc")

    merged.plot(ax=ax2, color=merged["cluster_color"], linewidth=0.3, edgecolor="gray")
    ax2.set_title("지역 유형화 (K-Means 클러스터링)\n노출도 기반", fontsize=16, fontweight="bold", pad=15)
    ax2.axis("off")

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#d32f2f", label="🔴 초고노출"),
        Patch(facecolor="#f57c00", label="🟠 고노출"),
        Patch(facecolor="#fbc02d", label="🟡 중노출"),
        Patch(facecolor="#388e3c", label="🟢 저노출"),
        Patch(facecolor="#cccccc", label="데이터 없음"),
    ]
    ax2.legend(handles=legend_elements, loc="lower left", fontsize=10, framealpha=0.9)

    out2 = os.path.join(output_dir, "exposure_cluster.png")  # ← 파일명 분리
    plt.savefig(out2, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"[저장] 클러스터 지도 → {out2}")


# ─────────────────────────────────────────────────────────────────────────────
# 7. 결과 저장
# ─────────────────────────────────────────────────────────────────────────────

def save_results(feat: pd.DataFrame, loading_df: pd.DataFrame, output_dir: str):
    # 주요 컬럼만 정리
    out = feat[[
        "시도명", "시군구명", "시군구코드",
        "E1_총주문건수", "E2_총주문금액", "E3_1인당평균금액", "E4_업종다양성",
        "노출도지수", "노출유형명"
    ]].sort_values("노출도지수", ascending=False)

    csv_path = os.path.join(output_dir, "exposure_index.csv")
    out.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"[저장] 지수 CSV → {csv_path}")

    loading_path = os.path.join(output_dir, "pca_loading.csv")
    loading_df.to_csv(loading_path, encoding="utf-8-sig")
    print(f"[저장] PCA 로딩 → {loading_path}")

    print("\n[상위 10개 고노출 지역]")
    print(out.head(10).to_string(index=False))


# ─────────────────────────────────────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("플랫폼 노동 노출도 지수 분석")
    print("=" * 60)

    df_raw = load_delivery_data(DATA_DIR)
    df = preprocess(df_raw, year=YEAR_TARGET)

    feat = calc_exposure_features(df)
    feat, loading_df = calc_exposure_index(feat)
    feat = cluster_regions(feat, n_clusters=N_CLUSTERS)

    # Shapefile 있을 때만 지도 그리기
    if os.path.exists(SHAPEFILE):
        plot_maps(feat, SHAPEFILE, OUTPUT_DIR)
    else:
        print(f"\n⚠ Shapefile 없음: {SHAPEFILE} → 지도 생략")

    save_results(feat, loading_df, OUTPUT_DIR)
    print("\n✅ 완료")


if __name__ == "__main__":
    main()