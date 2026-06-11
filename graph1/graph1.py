import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

# 여백 오류 방지를 위해 layout='constrained' 적용
fig, ax = plt.subplots(figsize=(10, 6), layout='constrained')
fig.patch.set_facecolor('white')

years        = [2021, 2022, 2023]
total        = [66.1, 79.5, 88.3]
delivery     = [49.2, 51.3, 48.5]
it           = [8.5,  8.5,  14.4]
care         = [5.3,  5.3,   5.2]
professional = [1.7,  1.7,   4.1]
other        = [1.4,  2.7,  16.1]

x = np.arange(len(years))
w = 0.13

ax.bar(x - 2*w, delivery,     w, label='배달·운전',       color='#E05C3A')
ax.bar(x -   w, it,           w, label='IT·소프트웨어',   color='#2E4B8F')
ax.bar(x,       care,         w, label='가사·돌봄',       color='#4CAF50')
ax.bar(x +   w, professional, w, label='교육·전문서비스', color='#9C27B0')
ax.bar(x + 2*w, other,        w, label='기타',            color='#FF9800')

ax.plot(x, total, 'ko-', linewidth=2.5, markersize=9, label='전체 합계(만명)', zorder=5)
for xi, yi in zip(x, total):
    ax.annotate(f'{yi}만명', (xi, yi),
                textcoords='offset points', xytext=(0, 10),
                ha='center', fontsize=11, fontweight='bold', color='black')

ax.set_xticks(x)
ax.set_xticklabels(['2021년', '2022년', '2023년'], fontsize=12)
ax.set_ylabel('종사자 수 (만명)', fontsize=11)
ax.set_ylim(0, 100)
ax.set_title('플랫폼 종사자 규모 및 업종별 현황\n(고용노동부·한국고용정보원, 플랫폼종사자 실태조사 기준)',
             fontsize=14, fontweight='bold', pad=15)
ax.legend(loc='upper left', fontsize=10, frameon=False)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', linestyle='--', alpha=0.4)

# 2026년 시점에서의 다년도 트렌드 통합 해석 주석
ax.text(0.01, -0.05,
    '※ 조사 기간 내 전체 규모 33.6% 지속 성장 (66.1만명 → 88.3만명)\n'
    '※ IT·전문서비스의 급격한 다변화 양상 속, 배달·운전 업종은 엔데믹 이후 소폭 감소 추세 안정화',
    transform=ax.transAxes, fontsize=9.5, color='#444444', verticalalignment='top')

plt.savefig('graph1_platform_scale.png', dpi=150, bbox_inches='tight', facecolor='white')
print("저장 완료: graph1_platform_scale.png")