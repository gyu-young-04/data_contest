import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

# ❶ 핵심 수정: 1행 2열 구조로 도화지를 분할합니다. (너비 비율을 막대 7 : 원형 3 정도로 조절)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={'width_ratios': [7, 3]})
fig.patch.set_facecolor('white')

# -----------------------------------------------------------------
# ❷ 좌측 격자 (ax1): 연령대별 막대 그래프 그리기
# -----------------------------------------------------------------
ages = ['30대', '40대', '50대', '20대', '60대 이상', '10대']
values = [28.8, 26.8, 20.2, 13.8, 8.9, 1.5] # 이미지 기반 추정치 (30대/40대 확인 필요)
colors = ['#2E4B8F', '#2E4B8F', '#E05C3A', '#4CAF50', '#FF9800', '#9C27B0']

bars = ax1.barh(ages, values, color=colors, height=0.6)

# 막대 끝에 숫자 텍스트 표시
for bar in bars:
    width = bar.get_width()
    ax1.text(width + 0.5, bar.get_y() + bar.get_height()/2, f'{width}%', 
             va='center', ha='left', fontsize=11, fontweight='bold')

ax1.set_xlabel('비율 (%)', fontsize=11)
ax1.set_xlim(0, 35)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.grid(axis='x', linestyle='--', alpha=0.4) # 세로 점선

# -----------------------------------------------------------------
# ❸ 우측 격자 (ax2): 성별 비율 원형 그래프 그리기
# -----------------------------------------------------------------
gender_labels = ['남성 (70.4%)', '여성 (29.6%)']
gender_sizes = [70.4, 29.6]
gender_colors = ['#2E4B8F', '#E05C3A'] # 이미지와 유사한 톤의 색상

ax2.pie(gender_sizes, labels=gender_labels, colors=gender_colors, 
        startangle=90, counterclock=False, 
        wedgeprops={'edgecolor': 'white', 'linewidth': 2})
ax2.set_title('성별 비율', fontsize=12, fontweight='bold')

# -----------------------------------------------------------------
# ❹ 상단 전체 제목 및 하단 주석 설정
# -----------------------------------------------------------------
fig.suptitle('플랫폼 종사자 연령대별 분포 (2023년)\n(고용노동부·한국고용정보원, 플랫폼종사자 실태조사)', 
             fontsize=14, fontweight='bold', y=0.95)

# 하단 안내 문구 (전체 도화지 기준 배치)
fig.text(0.05, 0.02, 
         '※ 30~40대 핵심 경제활동 연령층이 전체의 55.6% 차지\n'
         '※ 여성 비율 22년 25.8% → 23년 29.6%로 증가 추세', 
         fontsize=9, color='#444444', ha='left', va='bottom')

# constrained_layout처럼 깔끔하게 자동 여백 조정 후 저장
plt.savefig('graph2_age_gender.png', dpi=150, bbox_inches='tight', facecolor='white')
print("저장 완료: graph2_age_gender.png")