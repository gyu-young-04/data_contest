import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.font_manager as fm

# =========================================================================
# 0. 매 실행 전 이전 그래프 메모리 완벽히 비우기 (잔상 방지)
# =========================================================================
plt.clf()
plt.close('all')

# [단계 1] 한글 폰트 설정 (우분투/WSL 나눔고딕 경로 직접 지정)
font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
font_name = fm.FontProperties(fname=font_path).get_name()
plt.rc('font', family=font_name)
plt.rcParams['axes.unicode_minus'] = False

# =========================================================================
# [단계 2] CSV 파일 자체를 랜덤 숫자로 '직접 수정'해서 저장하기
# =========================================================================
# 1. 기존에 만들어둔 250개 시군구 CSV 파일을 읽어옵니다.
csv_data = pd.read_csv("map_all_sig.csv", dtype={'sig_code': str})

# 2. 🎲 value 컬럼을 1부터 100 사이의 랜덤 숫자로 '직접 수정'합니다.
csv_data['value'] = np.random.randint(1, 101, size=len(csv_data))

# 3. 💾 수정된 데이터를 'map_all_sig.csv' 파일에 그대로 덮어써서 영구 저장합니다.
# 인코딩은 한글이 안 깨지도록 utf-8-sig 양식을 유지합니다.
csv_data.to_csv("map_all_sig.csv", index=False, encoding='utf-8-sig')
print("🎲 [CSV 수정 완료] map_all_sig.csv 파일에 랜덤 수치(1~100)를 직접 주입하고 저장했습니다.")

# =========================================================================
# [단계 3] 지도 데이터 불러오기 및 병합
# =========================================================================
# 1. 지리 경계 데이터 불러오기
sig_gdf = gpd.read_file("sig.shp")

# 2. 위에서 랜덤으로 직접 수정해 저장한 CSV 데이터를 지도와 병합 (전국 250개 유지)
merged_gdf = sig_gdf.merge(csv_data, left_on="SIG_CD", right_on="sig_code", how="left")

# =========================================================================
# [단계 4] 지도 시각화 설정 (수치형 밀도 지도)
# =========================================================================
fig, ax = plt.subplots(1, 1, figsize=(15, 15))

# 데이터의 수치에 따라 다르게 색칠하기
merged_gdf.plot(
    column="value",           # 방금 랜덤으로 바뀐 CSV의 수치 데이터 사용
    categorical=False,        # 연속형 데이터
    cmap="Blues",             # 파란색 그라데이션 밀도
    legend=True,              
    legend_kwds={
        'label': "테스트 평가 지수 (점수)",  
        'orientation': "vertical",
        'shrink': 0.7             
    },
    edgecolor="grey",         
    linewidth=0.3,            
    ax=ax
)

# 불필요한 위도/경도 축 숨기기
ax.axis('off')
ax.set_title("대한민국 시군구별 데이터 분석 결과 시각화 (랜덤 수치 기입)", fontsize=18, fontweight='bold', pad=20)

# =========================================================================
# [단계 5] 고해상도 이미지 저장
# =========================================================================
plt.savefig("korea_final_value_map.png", dpi=300, bbox_inches='tight')
print("🎨 [지도 저장 완료] 최종 수치가 반영된 지도(korea_final_value_map.png) 작성을 마쳤습니다.")