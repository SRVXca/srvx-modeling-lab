"""Research figure: source points, executed model defaults and separately anchored coefficient maps."""
import json
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parent;LAB=ROOT.parents[2];BUNDLE=LAB/'evidence-core/heat-pump/issue-19-v0.1'
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'work/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

model=json.loads((BUNDLE/'validation/executed-consumer-workflows.json').read_text())['profiles']
comparison=json.loads((BUNDLE/'comparison/capacity-profile-comparison.json').read_text())
fig,axes=plt.subplots(1,2,figsize=(12,5.5))
for name,color,label in [('legacy-H2K','#85717a','Legacy 17F input → current consumer'),
                         ('current-OpenStudio-fallback','#e2a341','Current consumer fallback'),
                         ('matched-equipment-17F-shape-plus-defaults','#3b7a9f','17F source ratio + consumer defaults')]:
    p=sorted([r for r in model[name]['points'] if r['level']=='nominal'],key=lambda r:r['temperatureF'])
    axes[0].plot([r['temperatureF'] for r in p],[r['fractionOfModelNominal'] for r in p],'-o',color=color,label=label)
    axes[1].plot([r['temperatureF'] for r in p],[r['cop'] for r in p],'-o',color=color,label=label)
axes[0].scatter([47,17,5],[1,11/12,.825],marker='D',s=65,color='#b13849',label='ENERGY STAR points (5F speed unspecified)',zorder=5)
axes[1].scatter([5],[2],marker='D',s=65,color='#b13849',label='Only available source COP (5F)',zorder=5)
for key,label,color in [('publishedDerived','Published A82 · common anchor','#50996b'),('reconstructionDerived','Experimental reconstruction · common anchor','#7c6da6')]:
    data=comparison[key]
    axes[0].plot([5,17,47],[data[f'{t}F']['nominal'] for t in [5,17,47]],'--',color=color,label=label)
for ax in axes:
    ax.set_xticks([5,17,47]);ax.set_xlabel('Outdoor temperature [°F]');ax.grid(alpha=.25);ax.legend(fontsize=8)
axes[0].set_ylabel('Capacity / nominal 47F capacity');axes[1].set_ylabel('COP [W/W]')
axes[0].set_title('Nominal capacity profiles; missing speed semantics retained')
axes[1].set_title('Consumer-calculated COP versus one reported point')
fig.suptitle('Heat-pump evidence comparison · no installed-system accuracy claim',fontsize=14)
fig.text(.5,.025,'A82/reconstruction curves share an illustrative Q17/Q47 anchor of 11/12; coefficients are not equipment observations.',ha='center',fontsize=8)
fig.tight_layout(rect=[0,.05,1,.94]);fig.savefig(BUNDLE/'comparison/performance-profiles.png',dpi=170)
print(BUNDLE/'comparison/performance-profiles.png')
