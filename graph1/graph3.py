import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

fig, axes = plt.subplots(1, 2, figsize=(13, 6))
fig.patch.set_facecolor('white')
fig.suptitle('플랫폼 노동자 애로사항 및 보험 가입 현황 (2023년)\n(고용노동부·한국고용정보원, 플랫폼종사자 실태조사)',
             fontsize=14, fontweight='bold', y=1.02)

ax1 = axes[0]
items  = ['계약에 없는 업무 요구', '건강·안전 위험·불안감', '일방적 계약 변경',
          '경력 인정 곤란', '보수지급 지연']
values = [12.2, 11.9, 10.5, 9.7, 9.5]
colors = ['#C0392B', '#E05C3A', '#E67E22', '#F39C12', '#F1C40F']

y = np.arange(len(items))
bars = ax1.barh(y, values, height=0.55, color=colors, alpha=0.9)
for bar, val in zip(bars, values):
    ax1.text(val + 0.1, bar.get_y() + bar.get_height() / 2,
             f'{val}%', va='center', fontsize=11, fontweight='bold')

ax1.set_yticks(y)
ax1.set_yticklabels(items, fontsize=11)
ax1.set_xlabel('응답 비율 (%)', fontsize=10)
ax1.set_xlim(0, 16)
ax1.set_title('주요 애로사항 Top 5', fontsize=12, fontweight='bold', pad=10)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.grid(axis='x', linestyle='--', alpha=0.4)

ax2 = axes[1]
insurance_items = ['산재보험\n가입률', '고용보험\n가입률', '국민연금\n가입률', '건강보험\n가입률']
platform_vals   = [36.5, 18.3, 52.1, 61.4]
general_vals    = [100.0, 100.0, 98.5, 99.2]

x = np.arange(len(insurance_items))
w = 0.32

b1 = ax2.bar(x - w / 2, platform_vals, w, label='플랫폼 노동자',   color='#E05C3A', alpha=0.88)
b2 = ax2.bar(x + w / 2, general_vals,  w, label='일반 임금근로자', color='#2E4B8F', alpha=0.88)

for bar in b1:
    h = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width() / 2, h + 1,
             f'{h}%', ha='center', fontsize=9.5, fontweight='bold', color='#C0392B')
for bar in b2:
    h = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width() / 2, h + 1,
             f'{h}%', ha='center', fontsize=9.5, fontweight='bold', color='#1B4FBE')

ax2.axhline(y=100, color='gray', linestyle=':', alpha=0.6)
ax2.set_xticks(x)
ax2.set_xticklabels(insurance_items, fontsize=11)
ax2.set_ylabel('가입률 (%)', fontsize=10)
ax2.set_ylim(0, 118)
ax2.set_title('사회보험 가입률 비교\n(플랫폼 vs 일반 임금근로자)', fontsize=12, fontweight='bold', pad=10)
ax2.legend(fontsize=10, frameon=False)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.grid(axis='y', linestyle='--', alpha=0.4)

fig.text(0.01, -0.04,
    '일방적 계약 변경 및 부당 요구(애로 1·3위) 대응을 위한 플랫폼 공정거래 규제 법제화 요구 지속 직면\n'
    '※ 고용·산재보험 고유의 "전속성 요건 폐지" 정착기임에도 불확실한 소득 신고 체계로 인해 실가입률은 여전히 취약',
    fontsize=9, color='#444444')

plt.tight_layout()
plt.savefig('graph3_issues_insurance.png', dpi=150, bbox_inches='tight', facecolor='white')
print("저장 완료: graph3_issues_insurance.png")