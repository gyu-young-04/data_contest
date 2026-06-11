import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

fig, axes = plt.subplots(1, 2, figsize=(13, 6))
fig.patch.set_facecolor('white')
fig.suptitle('플랫폼 노동자 소득 및 노동시간 비교 (2023년)\n(고용노동부·한국고용정보원, 한국노동사회연구소)',
             fontsize=14, fontweight='bold', y=1.02)

ax1 = axes[0]
groups  = ['플랫폼 노동자\n(주업)', '플랫폼 노동자\n(부업)', '일반 임금근로자\n(평균)']
incomes = [266, 146, 353]
colors  = ['#E05C3A', '#FF9800', '#2E4B8F']

x = np.arange(len(groups))
bars = ax1.bar(x, incomes, width=0.5, color=colors, alpha=0.88)
for bar, val in zip(bars, incomes):
    ax1.text(bar.get_x() + bar.get_width() / 2, val + 5,
             f'{val}만원', ha='center', fontsize=12, fontweight='bold')

ax1.annotate('', xy=(2, 353), xytext=(0, 266),
             arrowprops=dict(arrowstyle='<->', color='#555', lw=1.5,
                             connectionstyle='arc3,rad=0'))
ax1.text(1.0, 310, '-87만원\n차이', ha='center', fontsize=9.5,
         color='#C0392B', fontweight='bold')

ax1.set_xticks(x)
ax1.set_xticklabels(groups, fontsize=10.5)
ax1.set_ylabel('월평균 소득 (만원)', fontsize=11)
ax1.set_ylim(0, 420)
ax1.set_title('월평균 소득 비교', fontsize=12, fontweight='bold', pad=10)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.grid(axis='y', linestyle='--', alpha=0.4)

ax2 = axes[1]
time_groups = ['플랫폼\n(주업)', '플랫폼\n(부업)', '일반임금\n근로자']
hours       = [43.2, 15.6, 40.5]
colors2     = ['#E05C3A', '#FF9800', '#2E4B8F']

bars2 = ax2.bar(np.arange(3), hours, width=0.5, color=colors2, alpha=0.88)
for bar, val in zip(bars2, hours):
    ax2.text(bar.get_x() + bar.get_width() / 2, val + 0.5,
             f'{val}시간', ha='center', fontsize=12, fontweight='bold')

ax2.axhline(y=40, color='red', linestyle='--', alpha=0.7, linewidth=1.5)
ax2.text(2.55, 40.5, '법정 주 40시간', fontsize=9, color='red')

ax2.set_xticks([0, 1, 2])
ax2.set_xticklabels(time_groups, fontsize=11)
ax2.set_ylabel('주당 노동시간 (시간)', fontsize=11)
ax2.set_ylim(0, 55)
ax2.set_title('주당 평균 노동시간 비교', fontsize=12, fontweight='bold', pad=10)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.grid(axis='y', linestyle='--', alpha=0.4)

fig.text(0.01, -0.04,
    '※ 플랫폼 주업 노동자 소득(266만원)은 일반 임금근로자(353만원)의 75.4% 수준'
    '※ 플랫폼 주업 노동시간은 법정기준 초과에도 산재·고용보험 사각지대 노출\n'
    '※ 비용지출(유류비·장비비 등) 평균 32만원 공제 시 실수령액 약 234만원'
    '※ 플랫폼 주업 소득(266만원)은 임금근로자 평균의 75.4% 수준이나, 필수 경비(32만원) 공제 시 실소득은 약 234만원에 불과\n'
    '※ 주 43.2시간의 장시간 노동 형태를 띠고 있어, 실제 노동 투입 대비 소득은 2026년 최저임금 수준을 겨우 상회하는 구조'
    '※ 소득 한계 극복을 위한 과로 위험성이 상존함에 따라, 플랫폼 취약 계층 보장 단가 논의 확산',
    fontsize=9, color='#444444')

plt.tight_layout()
plt.savefig('graph4_income_hours.png', dpi=150, bbox_inches='tight', facecolor='white')
print("저장 완료: graph4_income_hours.png")