import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

fig, axes = plt.subplots(1, 2, figsize=(13, 6))
fig.patch.set_facecolor('white')
fig.suptitle('플랫폼 노동 진입 동기 및 향후 전망 (2023년)\n(고용노동부·한국고용정보원, 한국노동사회연구소)',
             fontsize=14, fontweight='bold', y=1.02)

# ── 왼쪽: 진입 동기 수평 막대 ───────────────────
ax1 = axes[0]
motives = ['시간 유연성\n(자발적 선호)', '일 구하기 쉬워서\n(접근성)', '소득 보충\n(부업 목적)',
           '실직·이직 후\n대안', '생계유지\n(주소득 필요)']
values  = [28.2, 23.8, 21.0, 15.5, 11.5]
colors  = ['#2E4B8F', '#4CAF50', '#FF9800', '#E05C3A', '#C0392B']

ax1.axhspan(1.5, 4.6, alpha=0.07, color='#2E4B8F')
ax1.axhspan(-0.5, 1.5, alpha=0.07, color='#C0392B')

y = np.arange(len(motives))
bars = ax1.barh(y, values, height=0.55, color=colors, alpha=0.88)
for bar, val in zip(bars, values):
    ax1.text(val + 0.3, bar.get_y() + bar.get_height() / 2,
             f'{val}%', va='center', fontsize=11.5, fontweight='bold')

ax1.set_yticks(y)
ax1.set_yticklabels(motives, fontsize=10)
ax1.set_xlabel('응답 비율 (%)', fontsize=10)
ax1.set_xlim(0, 36)
ax1.set_title('플랫폼 노동 선택 동기', fontsize=12, fontweight='bold', pad=10)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.grid(axis='x', linestyle='--', alpha=0.4)

ax1.text(30, 3.7, '자발적\n선호\n(52%)', fontsize=8.5, color='#2E4B8F',
         fontweight='bold', ha='center')
ax1.text(30, 0.5, '반강제적\n선택\n(48%)', fontsize=8.5, color='#C0392B',
         fontweight='bold', ha='center')

# ── 오른쪽: 지속 의향 이중 도넛 차트 ──────────────
ax2 = axes[1]

outer_labels = ['지속 의향\n(81.8%)', '이직 의향\n(18.2%)']
outer_sizes  = [81.8, 18.2]
outer_colors = ['#2E4B8F', '#E05C3A']

inner_labels = ['주업 지속', '부업 유지', '타직종 이동', '임금근로 복귀']
inner_sizes  = [45.0, 36.8, 11.2, 7.0]
inner_colors = ['#4472C4', '#70AD47', '#FF7F50', '#FFC000']

ax2.pie(outer_sizes, radius=1.0, colors=outer_colors,
        startangle=90,
        wedgeprops=dict(width=0.38, edgecolor='white', linewidth=2.5))

ax2.pie(inner_sizes, radius=0.60, colors=inner_colors,
        startangle=90,
        wedgeprops=dict(width=0.38, edgecolor='white', linewidth=2),
        autopct='%1.0f%%', pctdistance=0.75,
        textprops={'fontsize': 8.5})

ax2.set_title('향후 지속 의향 및 세부 계획\n(외부: 지속 여부 / 내부: 세부 계획)',
              fontsize=12, fontweight='bold', pad=10)

leg1 = [mpatches.Patch(color=c, label=l) for c, l in zip(outer_colors, outer_labels)]
leg2 = [mpatches.Patch(color=c, label=l) for c, l in zip(inner_colors, inner_labels)]
ax2.legend(handles=leg1 + leg2, loc='lower center', fontsize=8.5, frameon=False,
           ncol=2, bbox_to_anchor=(0.5, -0.22))

fig.text(0.01, -0.06,
    '※ 진입동기의 약 48%는 실직 대안·생계유지 등 "반강제적 선택" 성격 → 단순 선호가 아닌 구조적 문제\n'
    '※ 이직 의향은 18.2%로 낮음 → 대안 부재 또는 진입 장벽으로 인한 잠금 효과(Lock-in) 가능성\n'
    '※ 진입동기 중 실직 대안·생계유지 등 "반강제적 선택(48%)" 비중이 높아 단순 유연성 선호로 단정 곤란\n'
    '※ 이직 의향(18.2%)이 낮고 잔류율이 높은 잠금 효과(Lock-in) 지속 — 최근 종사자의 노동자성 인정 판례 확대와 맞물려 권리 보장 요구 가속화',
    fontsize=9, color='#444444')

plt.tight_layout()
plt.savefig('graph5_motivation_future.png', dpi=150, bbox_inches='tight', facecolor='white')
print("저장 완료: graph5_motivation_future.png")