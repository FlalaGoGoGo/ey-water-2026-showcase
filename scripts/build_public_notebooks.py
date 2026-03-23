from __future__ import annotations

import json
import shutil
from pathlib import Path

import nbformat as nbf

SHOWCASE = Path('/Users/zhangziling/Documents/New project/ey-water-2026-showcase')
NOTEBOOKS = SHOWCASE / 'notebooks'
ASSETS = NOTEBOOKS / 'assets'
ANCHORS = ASSETS / 'anchors'
CACHE = ASSETS / 'cache'
TARGETS = ASSETS / 'targets'
SOURCE_ROOT = Path('/Users/zhangziling/Documents/New project')

PUBLIC_RAW = 'https://raw.githubusercontent.com/FlalaGoGoGo/ey-water-2026-showcase/main'
OFFICIAL_RAW = 'https://raw.githubusercontent.com/Snowflake-Labs/EY-AI-and-Data-Challenge/refs/heads/main'


def step_md(step: int, title: str, purpose: str, why: str, out: str) -> str:
    return (
        f"## Step {step}. {title}\n\n"
        f"**这个步骤做什么**\n{purpose}\n\n"
        f"**为什么要做这个步骤**\n{why}\n\n"
        f"**预期产出**\n{out}"
    )


def code_cell(source: str):
    return nbf.v4.new_code_cell(source.strip() + "\n")


def md_cell(source: str):
    return nbf.v4.new_markdown_cell(source.strip() + "\n")


def copy_fullflow_notebooks() -> None:
    copies = {
        SOURCE_ROOT / 'round11_notebooks/v11_4_guard_ec.ipynb': NOTEBOOKS / 'v11_4_guard_ec.ipynb',
        SOURCE_ROOT / 'round15/notebooks/v15_3_ta_refine_push.ipynb': NOTEBOOKS / 'v15_3_ta_refine_push.ipynb',
        SOURCE_ROOT / 'round20/notebooks/v20_4_ta_ec_struct_farcal_alt.ipynb': NOTEBOOKS / 'v20_4_ta_ec_struct_farcal_alt.ipynb',
    }
    for src, dst in copies.items():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def copy_public_assets() -> None:
    mapping = {
        SOURCE_ROOT / 'round29/v29_5_static_hydro_ood_guard.csv': ANCHORS / 'round29/v29_5_static_hydro_ood_guard.csv',
        SOURCE_ROOT / 'round36/v36_1_control_v35_1.csv': ANCHORS / 'round36/v36_1_control_v35_1.csv',
        SOURCE_ROOT / 'round37/v37_1_control_v36_1.csv': ANCHORS / 'round37/v37_1_control_v36_1.csv',
        SOURCE_ROOT / 'round37/v37_4_ta40_ec35_push.csv': ANCHORS / 'round37/v37_4_ta40_ec35_push.csv',
        SOURCE_ROOT / 'round37/v37_5_ta40_ec40_push.csv': TARGETS / 'v37_5_ta40_ec40_push.csv',
        SOURCE_ROOT / 'round38/v38_5_chirps_delta_safe.csv': TARGETS / 'v38_5_chirps_delta_safe.csv',
        SOURCE_ROOT / 'round42/v42_5_ta60_ec60_challenger_push.csv': TARGETS / 'v42_5_ta60_ec60_challenger_push.csv',
        SOURCE_ROOT / 'ey-water-2026/experiments/cache/chirps_monthly_lookup.csv': CACHE / 'chirps_monthly_lookup.csv',
    }
    for src, dst in mapping.items():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def common_env_code() -> str:
    return f'''
# =========================
# Step: Environment Setup
# 作用：导入依赖，定义官方数据源与公开 repo 资产地址
# =========================

from pathlib import Path
from io import StringIO
import subprocess

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

pd.set_option('display.max_columns', 220)
pd.set_option('display.width', 220)

OFFICIAL_RAW = '{OFFICIAL_RAW}'
SHOWCASE_RAW = '{PUBLIC_RAW}'
OUTPUT_DIR = Path('generated_outputs')
OUTPUT_DIR.mkdir(exist_ok=True)


def read_csv_remote(url: str) -> pd.DataFrame:
    """优先 pandas 直读，失败时回退到 curl，保证 notebook 更稳。"""
    try:
        return pd.read_csv(url)
    except Exception as exc:
        print(f'[warn] pandas direct read failed: {{url}}')
        print(f'       reason: {{exc}}')
        res = subprocess.run(['curl', '-L', url], check=True, capture_output=True, text=True)
        return pd.read_csv(StringIO(res.stdout))
'''


def v37_notebook() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    cells = [
        md_cell(
            "# Round37 Full Workflow Notebook: `v37_5_ta40_ec40_push.csv`\n\n"
            "这个 notebook 展示了后期突破阶段的完整流程：从官方 GitHub 原始数据读取，到 Hydro corridor 共识增量构造、导出提交文件、再到与公开参考文件逐列核对。\n\n"
            "**为什么这本 notebook 重要**\n"
            "- 这是项目第一次把官方分数推到 `0.376` 的关键阶段。\n"
            "- 策略核心是把 `TA` 和 `EC` 的正向安全增量同时推到 `0.40 / 0.40`。\n"
            "- DRP 在这个阶段保持锚定，避免破坏整体稳定性。"
        ),
        md_cell(step_md(1, 'Experiment Objective', '说明 round37 突破分支的策略目标和设计原则。', '后期 notebook 不能只给结果，还要讲清楚为什么这一步值得测试。', '得到本分支的实验角色定义。')),
        md_cell(
            "**本分支摘要**\n"
            "- Output file: `v37_5_ta40_ec40_push.csv`\n"
            "- Strategy family: `Hydro micro corridor`\n"
            "- TA alpha: `0.40`\n"
            "- EC alpha: `0.40`\n"
            "- DRP source: `legacy control`"
        ),
        md_cell(step_md(2, 'Environment Setup', '导入依赖并定义官方数据与公开资产地址。', '保证 notebook 从第一行开始就能看懂输入数据来自哪里。', '得到统一运行环境和 URL 常量。')),
        code_cell(common_env_code()),
        md_cell(step_md(3, 'Load Official Data And Public Anchors', '读取官方验证模板、训练数据，以及公开 repo 中保存的关键锚点提交文件。', '这个阶段的策略不是黑盒模型，而是围绕已验证安全锚点做结构化增量。', '得到构造 round37 提交所需的全部输入表。')),
        code_cell(
            "# 官方原始数据\n"
            "train_wq = read_csv_remote(f'{OFFICIAL_RAW}/water_quality_training_dataset.csv')\n"
            "val_tpl = read_csv_remote(f'{OFFICIAL_RAW}/submission_template.csv')\n\n"
            "# 公开 repo 中保存的策略锚点\n"
            "legacy_control = read_csv_remote(f'{SHOWCASE_RAW}/notebooks/assets/anchors/round29/v29_5_static_hydro_ood_guard.csv')\n"
            "control_30 = read_csv_remote(f'{SHOWCASE_RAW}/notebooks/assets/anchors/round36/v36_1_control_v35_1.csv')\n"
            "reference_target = read_csv_remote(f'{SHOWCASE_RAW}/notebooks/assets/targets/v37_5_ta40_ec40_push.csv')\n\n"
            "print('train_wq:', train_wq.shape)\n"
            "print('val_tpl:', val_tpl.shape)\n"
            "print('legacy_control:', legacy_control.shape)\n"
            "print('control_30:', control_30.shape)\n"
            "print('reference_target:', reference_target.shape)"
        ),
        md_cell(step_md(4, 'Quick QA And Context', '检查日期范围、站点数量、以及控制锚点与官方模板是否对齐。', '先确认输入表结构正确，后面的差分和渲染才有意义。', '得到一个可审计的 round37 输入上下文。')),
        code_cell(
            "train_wq['Sample Date'] = pd.to_datetime(train_wq['Sample Date'], dayfirst=True, errors='coerce')\n"
            "val_dates = pd.to_datetime(val_tpl['Sample Date'], dayfirst=True, errors='coerce')\n\n"
            "print('training date range:', train_wq['Sample Date'].min(), '->', train_wq['Sample Date'].max())\n"
            "print('validation date range:', val_dates.min(), '->', val_dates.max())\n"
            "print('unique training sites:', train_wq[['Latitude', 'Longitude']].drop_duplicates().shape[0])\n"
            "print('template rows:', len(val_tpl))\n\n"
            "display(train_wq.head(3))\n"
            "display(legacy_control.head(3))"
        ),
        md_cell(step_md(5, 'Build Consensus Deltas', '把 legacy control 和 round36 control 的差值转换成可控的 TA/EC 共识增量。', 'round37 的核心不是重新训练，而是沿着已经在线验证过的正向方向继续推。', '得到可用于 outer-boundary push 的 TA/EC 增量数组。')),
        code_cell(
            "base_ta = legacy_control['Total Alkalinity'].to_numpy(dtype=float)\n"
            "base_ec = legacy_control['Electrical Conductance'].to_numpy(dtype=float)\n"
            "base_drp = legacy_control['Dissolved Reactive Phosphorus'].to_numpy(dtype=float)\n\n"
            "control_ta = control_30['Total Alkalinity'].to_numpy(dtype=float)\n"
            "control_ec = control_30['Electrical Conductance'].to_numpy(dtype=float)\n\n"
            "# 0.30 是上一阶段 control 的安全推进强度，这里把它还原成单位共识增量。\n"
            "ta_consensus_delta = np.maximum(control_ta - base_ta, 0.0) / 0.30\n"
            "ec_consensus_delta = np.maximum(control_ec - base_ec, 0.0) / 0.30\n\n"
            "print('mean ta consensus delta:', round(float(np.mean(ta_consensus_delta)), 6))\n"
            "print('mean ec consensus delta:', round(float(np.mean(ec_consensus_delta)), 6))"
        ),
        md_cell(step_md(6, 'Render The 40/40 Push', '按 round37 的配置把 TA 和 EC 同时推到 0.40，DRP 保持 legacy 锚点。', '这个版本的目标是验证联合边界 40/40 是否还能在线保持安全。', '得到最终预测数组。')),
        code_cell(
            "ta = np.clip(base_ta + 0.40 * ta_consensus_delta, 0, None)\n"
            "ec = np.clip(base_ec + 0.40 * ec_consensus_delta, 0, None)\n"
            "drp = np.clip(base_drp, 0, None)\n\n"
            "submission = val_tpl[['Latitude', 'Longitude', 'Sample Date']].copy()\n"
            "submission['Sample Date'] = pd.to_datetime(submission['Sample Date'], dayfirst=True, errors='coerce').dt.strftime('%d/%m/%Y')\n"
            "submission['Total Alkalinity'] = ta\n"
            "submission['Electrical Conductance'] = ec\n"
            "submission['Dissolved Reactive Phosphorus'] = drp\n"
            "submission = submission[['Latitude', 'Longitude', 'Sample Date', 'Total Alkalinity', 'Electrical Conductance', 'Dissolved Reactive Phosphorus']]\n"
            "display(submission.head(3))"
        ),
        md_cell(step_md(7, 'Export And Verify', '导出 round37 文件，并和公开参考结果逐列比较。', '公开 notebook 最好不仅能生成文件，还能证明自己复现的是正确版本。', '得到导出 csv 与 exact-match 诊断。')),
        code_cell(
            "out_path = OUTPUT_DIR / 'v37_5_ta40_ec40_push.csv'\n"
            "submission.to_csv(out_path, index=False)\n"
            "print('saved to:', out_path.resolve())\n\n"
            "metric_cols = ['Total Alkalinity', 'Electrical Conductance', 'Dissolved Reactive Phosphorus']\n"
            "diff = (submission[metric_cols] - reference_target[metric_cols]).abs()\n"
            "print('max abs diff by target:')\n"
            "print(diff.max())\n"
            "print('exact match:', bool((diff.max() < 1e-12).all()))"
        ),
        md_cell(step_md(8, 'Diagnostic Review', '用简单图表查看 round37 相对 legacy control 的整体位移。', '这一步帮助外部读者理解为什么这个版本属于“结构化边界推进”而不是随机改数。', '得到 TA/EC/DRP 三个目标的整体位移解释。')),
        code_cell(
            "shift_summary = pd.DataFrame({\n"
            "    'target': ['TA', 'EC', 'DRP'],\n"
            "    'mean_abs_shift': [\n"
            "        float(np.mean(np.abs(submission['Total Alkalinity'] - legacy_control['Total Alkalinity']))),\n"
            "        float(np.mean(np.abs(submission['Electrical Conductance'] - legacy_control['Electrical Conductance']))),\n"
            "        float(np.mean(np.abs(submission['Dissolved Reactive Phosphorus'] - legacy_control['Dissolved Reactive Phosphorus']))),\n"
            "    ]\n"
            "})\n"
            "display(shift_summary)\n\n"
            "plt.figure(figsize=(7, 4))\n"
            "plt.bar(shift_summary['target'], shift_summary['mean_abs_shift'], color=['#ffe600', '#ffd166', '#9cd18b'])\n"
            "plt.title('Round37 mean absolute shift vs legacy control')\n"
            "plt.ylabel('Mean absolute shift')\n"
            "plt.show()"
        ),
        md_cell(
            "## Step 9. Interpretation\n\n"
            "**这个步骤做什么**\n"
            "把 round37 的结果放回到比赛节奏里解释。\n\n"
            "**为什么要做这个步骤**\n"
            "公开 notebook 不应该只有代码，还要告诉外部读者这一版为什么重要。\n\n"
            "**本分支结论**\n"
            "- TA 和 EC 同时推进到 `0.40 / 0.40` 后，round37 首次到达 `0.376`。\n"
            "- DRP 在这一阶段继续保持锚定，说明主收益来自 TA/EC corridor。\n"
            "- 这本 notebook 是后期平台段所有 tied frontier 分支的起点。"
        ),
    ]
    nb['cells'] = cells
    return nb


def v38_notebook() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    cells = [
        md_cell(
            "# Round38 Full Workflow Notebook: `v38_5_chirps_delta_safe.csv`\n\n"
            "这个 notebook 展示了 tied-best 阶段最重要的一个外部信号试探：在 `v37_5` 的 40/40 winner 上，使用 CHIRPS 月尺度降水异常只对湿月样本做 `EC` 轻量回退。\n\n"
            "**为什么这本 notebook 重要**\n"
            "- 它代表项目第一次把外部气候信号稳妥地嵌入后期 frontier。\n"
            "- 变化范围很小，但验证了 `wet-month guard` 这条线在线上不会伤分。\n"
            "- 这类 notebook 对公开读者最有价值，因为它清楚展示了 external data 怎么进入后处理。"
        ),
        md_cell(step_md(1, 'Experiment Objective', '说明 round38 CHIRPS safe probe 的目标。', '外部数据试探的关键不是幅度大，而是让读者看清楚门控逻辑。', '得到该分支的策略角色说明。')),
        md_cell(
            "**本分支摘要**\n"
            "- Output file: `v38_5_chirps_delta_safe.csv`\n"
            "- Base winner: `v37_5_ta40_ec40_push.csv`\n"
            "- Relax source: `v37_4_ta40_ec35_push.csv`\n"
            "- Gate: `if chirps_z >= wet_threshold then EC uses relaxed branch`\n"
            "- TA / DRP: keep winner anchor"
        ),
        md_cell(step_md(2, 'Environment Setup', '导入依赖并定义官方数据和公开 repo 资产地址。', '外部读者需要清楚看到 CHIRPS lookup 和锚点文件从哪里来。', '得到统一环境和远程数据读取函数。')),
        code_cell(common_env_code()),
        md_cell(step_md(3, 'Load Official Data, CHIRPS Lookup, And Anchors', '读取官方训练/验证数据、CHIRPS 月尺度缓存，以及两个 round37 提交锚点。', '这是把外部信号带入 notebook 的关键准备步骤。', '得到 round38 safe probe 所需的全部输入。')),
        code_cell(
            "train_wq = read_csv_remote(f'{OFFICIAL_RAW}/water_quality_training_dataset.csv')\n"
            "val_tpl = read_csv_remote(f'{OFFICIAL_RAW}/submission_template.csv')\n"
            "chirps = read_csv_remote(f'{SHOWCASE_RAW}/notebooks/assets/cache/chirps_monthly_lookup.csv')\n"
            "winner_40_40 = read_csv_remote(f'{SHOWCASE_RAW}/notebooks/assets/targets/v37_5_ta40_ec40_push.csv')\n"
            "relax_40_35 = read_csv_remote(f'{SHOWCASE_RAW}/notebooks/assets/anchors/round37/v37_4_ta40_ec35_push.csv')\n"
            "reference_target = read_csv_remote(f'{SHOWCASE_RAW}/notebooks/assets/targets/v38_5_chirps_delta_safe.csv')\n\n"
            "print('train_wq:', train_wq.shape)\n"
            "print('val_tpl:', val_tpl.shape)\n"
            "print('chirps:', chirps.shape)\n"
            "print('winner_40_40:', winner_40_40.shape)\n"
            "print('relax_40_35:', relax_40_35.shape)"
        ),
        md_cell(step_md(4, 'Build CHIRPS Wet-Month Gate', '基于训练集与验证模板共同构造 `chirps_z`，再得到湿月 mask。', 'round38 的关键不在模型，而在门控规则是否足够稳定。', '得到可以直接控制 EC 回退位置的 wet mask。')),
        code_cell(
            "def add_year_month(df: pd.DataFrame) -> pd.DataFrame:\n"
            "    out = df.copy()\n"
            "    out['Sample Date'] = pd.to_datetime(out['Sample Date'], dayfirst=True, errors='coerce')\n"
            "    out['year'] = out['Sample Date'].dt.year.astype(int)\n"
            "    out['month'] = out['Sample Date'].dt.month.astype(int)\n"
            "    return out\n\n"
            "site_month_stats = (\n"
            "    chirps.groupby(['Latitude', 'Longitude', 'month'])['chirps_monthly_precip']\n"
            "    .agg(['mean', 'std'])\n"
            "    .reset_index()\n"
            "    .rename(columns={'mean': 'chirps_site_month_mean', 'std': 'chirps_site_month_std'})\n"
            ")\n\n"
            "train = add_year_month(train_wq).merge(chirps, on=['Latitude', 'Longitude', 'year', 'month'], how='left')\n"
            "train = train.merge(site_month_stats, on=['Latitude', 'Longitude', 'month'], how='left')\n"
            "train['chirps_site_month_std'] = train['chirps_site_month_std'].replace(0.0, np.nan)\n"
            "train['chirps_anom'] = train['chirps_monthly_precip'] - train['chirps_site_month_mean']\n"
            "train['chirps_z'] = train['chirps_anom'] / train['chirps_site_month_std']\n"
            "wet_threshold = float(train['chirps_z'].dropna().quantile(0.80))\n\n"
            "sub = add_year_month(val_tpl).merge(chirps, on=['Latitude', 'Longitude', 'year', 'month'], how='left')\n"
            "sub = sub.merge(site_month_stats, on=['Latitude', 'Longitude', 'month'], how='left')\n"
            "sub['chirps_site_month_std'] = sub['chirps_site_month_std'].replace(0.0, np.nan)\n"
            "sub['chirps_anom'] = sub['chirps_monthly_precip'] - sub['chirps_site_month_mean']\n"
            "sub['chirps_z'] = sub['chirps_anom'] / sub['chirps_site_month_std']\n"
            "wet_mask = (sub['chirps_z'] >= wet_threshold).fillna(False).to_numpy()\n\n"
            "print('wet_threshold_train_q80:', round(wet_threshold, 4))\n"
            "print('wet_row_count:', int(wet_mask.sum()))\n"
            "display(sub[['Latitude', 'Longitude', 'Sample Date', 'chirps_z']].head(5))"
        ),
        md_cell(step_md(5, 'Render The CHIRPS Safe Branch', '在 40/40 winner 的基础上，仅对湿月行把 EC 回退到 40/35 版本。', '这样既保留了主 winner 的结构，又让外部降水信号只在小范围起作用。', '得到 round38 safe probe 的最终预测。')),
        code_cell(
            "ta = winner_40_40['Total Alkalinity'].to_numpy(dtype=float).copy()\n"
            "ec = winner_40_40['Electrical Conductance'].to_numpy(dtype=float).copy()\n"
            "drp = winner_40_40['Dissolved Reactive Phosphorus'].to_numpy(dtype=float).copy()\n\n"
            "relax_ec = relax_40_35['Electrical Conductance'].to_numpy(dtype=float)\n"
            "ec[wet_mask] = relax_ec[wet_mask]\n\n"
            "submission = val_tpl[['Latitude', 'Longitude', 'Sample Date']].copy()\n"
            "submission['Sample Date'] = pd.to_datetime(submission['Sample Date'], dayfirst=True, errors='coerce').dt.strftime('%d/%m/%Y')\n"
            "submission['Total Alkalinity'] = np.clip(ta, 0, None)\n"
            "submission['Electrical Conductance'] = np.clip(ec, 0, None)\n"
            "submission['Dissolved Reactive Phosphorus'] = np.clip(drp, 0, None)\n"
            "submission = submission[['Latitude', 'Longitude', 'Sample Date', 'Total Alkalinity', 'Electrical Conductance', 'Dissolved Reactive Phosphorus']]\n"
            "display(submission.head(3))"
        ),
        md_cell(step_md(6, 'Export And Verify', '导出文件并和公开参考文件做 exact-match 检查。', '这样外部读者可以确认 notebook 不是“近似思路”，而是精确复现。', '得到 round38 safe probe 的复现校验结果。')),
        code_cell(
            "out_path = OUTPUT_DIR / 'v38_5_chirps_delta_safe.csv'\n"
            "submission.to_csv(out_path, index=False)\n"
            "print('saved to:', out_path.resolve())\n\n"
            "metric_cols = ['Total Alkalinity', 'Electrical Conductance', 'Dissolved Reactive Phosphorus']\n"
            "diff = (submission[metric_cols] - reference_target[metric_cols]).abs()\n"
            "print('max abs diff by target:')\n"
            "print(diff.max())\n"
            "print('exact match:', bool((diff.max() < 1e-12).all()))"
        ),
        md_cell(step_md(7, 'Diagnostics And Interpretation', '量化这次改动到底改了多少行，以及每行的平均 EC 变化。', '后期 tied-best 版本的特点就是“改动很少，但每个改动都有假设”。', '得到 round38 的可解释门控摘要。')),
        code_cell(
            "changed_mask = np.abs(winner_40_40['Electrical Conductance'] - submission['Electrical Conductance']) > 1e-12\n"
            "summary = {\n"
            "    'wet_row_count': int(wet_mask.sum()),\n"
            "    'changed_row_count': int(changed_mask.sum()),\n"
            "    'mean_ec_shift_on_changed_rows': float(np.mean(np.abs(winner_40_40.loc[changed_mask, 'Electrical Conductance'] - submission.loc[changed_mask, 'Electrical Conductance']))) if changed_mask.any() else 0.0,\n"
            "}\n"
            "print(summary)\n\n"
            "plt.figure(figsize=(7, 4))\n"
            "plt.hist(sub['chirps_z'].dropna(), bins=28, color='#ffd166', edgecolor='black', alpha=0.85)\n"
            "plt.axvline(wet_threshold, color='#ffe600', linestyle='--', label='wet threshold')\n"
            "plt.title('Validation CHIRPS z-score distribution')\n"
            "plt.legend()\n"
            "plt.show()"
        ),
        md_cell(
            "## Step 8. Interpretation\n\n"
            "**这个步骤做什么**\n"
            "把 CHIRPS safe probe 放回到后期 tied-best 平台里解释。\n\n"
            "**为什么要做这个步骤**\n"
            "让外部读者理解：外部数据不是一定要大幅度改预测，更多时候是作为风险门控。\n\n"
            "**本分支结论**\n"
            "- round38 的 CHIRPS probe 只改变了湿月样本的 EC。\n"
            "- TA 与 DRP 保持 winner 锚点，这让变化幅度保持在安全区间。\n"
            "- 该策略最终与 frontier 并列，证明 external signals 可以以 guard 的方式进入后期提交流程。"
        ),
    ]
    nb['cells'] = cells
    return nb


def v42_notebook() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    cells = [
        md_cell(
            "# Round42 Full Workflow Notebook: `v42_5_ta60_ec60_challenger_push.csv`\n\n"
            "这个 notebook 展示平台期最激进但仍可解释的一类 challenger：把 TA/EC 同时推进到 `0.60 / 0.60`，同时在湿月样本上把 EC 放松回 `0.55`。\n\n"
            "**为什么这本 notebook 重要**\n"
            "- 它代表项目在 plateau 上继续探索外边界，而不是只重复 control。\n"
            "- 它延续了 round37 的 corridor 思路，但把系数推得更远。\n"
            "- 这个阶段也清楚说明了：后期很多 tied-best 文件其实是在探索边界安全范围。"
        ),
        md_cell(step_md(1, 'Experiment Objective', '说明 round42 challenger-push 的设计目标。', '平台期 notebook 的价值，在于把“为什么继续试”讲清楚。', '得到该分支在 plateau 上的角色说明。')),
        md_cell(
            "**本分支摘要**\n"
            "- Output file: `v42_5_ta60_ec60_challenger_push.csv`\n"
            "- TA alpha: `0.60`\n"
            "- EC alpha: `0.60`\n"
            "- Wet-month relax EC alpha: `0.55`\n"
            "- Base source: `round29 legacy control`\n"
            "- Delta source: `round37 control replay`"
        ),
        md_cell(step_md(2, 'Environment Setup', '导入依赖并定义官方数据和公开资产地址。', '确保 notebook 从第一步开始就完整自洽。', '得到统一环境和远程读取函数。')),
        code_cell(common_env_code()),
        md_cell(step_md(3, 'Load Raw Data, CHIRPS Lookup, And Anchors', '读取官方原始数据、CHIRPS lookup，以及构造 round42 所需的两个公开锚点。', '这一步决定了平台期 challenger 是建立在什么基准之上的。', '得到 round42 重建所需的全部输入。')),
        code_cell(
            "train_wq = read_csv_remote(f'{OFFICIAL_RAW}/water_quality_training_dataset.csv')\n"
            "val_tpl = read_csv_remote(f'{OFFICIAL_RAW}/submission_template.csv')\n"
            "chirps = read_csv_remote(f'{SHOWCASE_RAW}/notebooks/assets/cache/chirps_monthly_lookup.csv')\n"
            "legacy_control = read_csv_remote(f'{SHOWCASE_RAW}/notebooks/assets/anchors/round29/v29_5_static_hydro_ood_guard.csv')\n"
            "control_30 = read_csv_remote(f'{SHOWCASE_RAW}/notebooks/assets/anchors/round37/v37_1_control_v36_1.csv')\n"
            "reference_target = read_csv_remote(f'{SHOWCASE_RAW}/notebooks/assets/targets/v42_5_ta60_ec60_challenger_push.csv')\n\n"
            "print('train_wq:', train_wq.shape)\n"
            "print('val_tpl:', val_tpl.shape)\n"
            "print('chirps:', chirps.shape)\n"
            "print('legacy_control:', legacy_control.shape)\n"
            "print('control_30:', control_30.shape)"
        ),
        md_cell(step_md(4, 'Build Consensus Deltas And Wet-Month Mask', '同时构造 TA/EC 正向共识增量和 CHIRPS 湿月门控。', 'round42 的关键就是“更大外边界 + 轻门控回退”这两个部件一起工作。', '得到 challenger 渲染所需的 delta 和 wet mask。')),
        code_cell(
            "def add_year_month(df: pd.DataFrame) -> pd.DataFrame:\n"
            "    out = df.copy()\n"
            "    out['Sample Date'] = pd.to_datetime(out['Sample Date'], dayfirst=True, errors='coerce')\n"
            "    out['year'] = out['Sample Date'].dt.year.astype(int)\n"
            "    out['month'] = out['Sample Date'].dt.month.astype(int)\n"
            "    return out\n\n"
            "base_ta = legacy_control['Total Alkalinity'].to_numpy(dtype=float)\n"
            "base_ec = legacy_control['Electrical Conductance'].to_numpy(dtype=float)\n"
            "base_drp = legacy_control['Dissolved Reactive Phosphorus'].to_numpy(dtype=float)\n"
            "control_ta = control_30['Total Alkalinity'].to_numpy(dtype=float)\n"
            "control_ec = control_30['Electrical Conductance'].to_numpy(dtype=float)\n"
            "ta_consensus_delta = np.maximum(control_ta - base_ta, 0.0) / 0.30\n"
            "ec_consensus_delta = np.maximum(control_ec - base_ec, 0.0) / 0.30\n\n"
            "site_month_stats = (\n"
            "    chirps.groupby(['Latitude', 'Longitude', 'month'])['chirps_monthly_precip']\n"
            "    .agg(['mean', 'std'])\n"
            "    .reset_index()\n"
            "    .rename(columns={'mean': 'chirps_site_month_mean', 'std': 'chirps_site_month_std'})\n"
            ")\n"
            "train = add_year_month(train_wq).merge(chirps, on=['Latitude', 'Longitude', 'year', 'month'], how='left')\n"
            "train = train.merge(site_month_stats, on=['Latitude', 'Longitude', 'month'], how='left')\n"
            "train['chirps_site_month_std'] = train['chirps_site_month_std'].replace(0.0, np.nan)\n"
            "train['chirps_anom'] = train['chirps_monthly_precip'] - train['chirps_site_month_mean']\n"
            "train['chirps_z'] = train['chirps_anom'] / train['chirps_site_month_std']\n"
            "wet_threshold = float(train['chirps_z'].dropna().quantile(0.80))\n\n"
            "sub = add_year_month(val_tpl).merge(chirps, on=['Latitude', 'Longitude', 'year', 'month'], how='left')\n"
            "sub = sub.merge(site_month_stats, on=['Latitude', 'Longitude', 'month'], how='left')\n"
            "sub['chirps_site_month_std'] = sub['chirps_site_month_std'].replace(0.0, np.nan)\n"
            "sub['chirps_anom'] = sub['chirps_monthly_precip'] - sub['chirps_site_month_mean']\n"
            "sub['chirps_z'] = sub['chirps_anom'] / sub['chirps_site_month_std']\n"
            "wet_mask = (sub['chirps_z'] >= wet_threshold).fillna(False).to_numpy()\n\n"
            "print('wet_threshold_train_q80:', round(wet_threshold, 4))\n"
            "print('wet_row_count:', int(wet_mask.sum()))"
        ),
        md_cell(step_md(5, 'Render The 60/60 Challenger Push', '把 TA 和 EC 推到 0.60 / 0.60，同时在湿月把 EC 放松回 0.55。', '这是平台期最典型的“push with guard”思路。', '得到 round42 challenger-push 的最终预测。')),
        code_cell(
            "ta = np.clip(base_ta + 0.60 * ta_consensus_delta, 0, None)\n"
            "ec60 = np.clip(base_ec + 0.60 * ec_consensus_delta, 0, None)\n"
            "ec55 = np.clip(base_ec + 0.55 * ec_consensus_delta, 0, None)\n"
            "ec = ec60.copy()\n"
            "ec[wet_mask] = ec55[wet_mask]\n"
            "drp = np.clip(base_drp, 0, None)\n\n"
            "submission = val_tpl[['Latitude', 'Longitude', 'Sample Date']].copy()\n"
            "submission['Sample Date'] = pd.to_datetime(submission['Sample Date'], dayfirst=True, errors='coerce').dt.strftime('%d/%m/%Y')\n"
            "submission['Total Alkalinity'] = ta\n"
            "submission['Electrical Conductance'] = ec\n"
            "submission['Dissolved Reactive Phosphorus'] = drp\n"
            "submission = submission[['Latitude', 'Longitude', 'Sample Date', 'Total Alkalinity', 'Electrical Conductance', 'Dissolved Reactive Phosphorus']]\n"
            "display(submission.head(3))"
        ),
        md_cell(step_md(6, 'Export And Verify', '导出最终 csv，并与公开参考文件逐列比较。', '公开 notebook 需要证明自己生成的是正确目标文件。', '得到输出文件和 exact-match 复现结果。')),
        code_cell(
            "out_path = OUTPUT_DIR / 'v42_5_ta60_ec60_challenger_push.csv'\n"
            "submission.to_csv(out_path, index=False)\n"
            "print('saved to:', out_path.resolve())\n\n"
            "metric_cols = ['Total Alkalinity', 'Electrical Conductance', 'Dissolved Reactive Phosphorus']\n"
            "diff = (submission[metric_cols] - reference_target[metric_cols]).abs()\n"
            "print('max abs diff by target:')\n"
            "print(diff.max())\n"
            "print('exact match:', bool((diff.max() < 1e-12).all()))"
        ),
        md_cell(step_md(7, 'Diagnostics And Interpretation', '量化 challenger 相对 legacy control 的位移，以及湿月回退影响的行数。', '这样外部读者就能区分“push 的主体”与“guard 的范围”。', '得到 round42 challenger 的风险与位移摘要。')),
        code_cell(
            "changed_ec_mask = np.abs(ec60 - ec) > 1e-12\n"
            "summary = pd.DataFrame({\n"
            "    'metric': ['TA vs base', 'EC vs base', 'DRP vs base', 'Wet relaxed EC rows'],\n"
            "    'value': [\n"
            "        float(np.mean(np.abs(ta - base_ta))),\n"
            "        float(np.mean(np.abs(ec - base_ec))),\n"
            "        float(np.mean(np.abs(drp - base_drp))),\n"
            "        int(changed_ec_mask.sum()),\n"
            "    ]\n"
            "})\n"
            "display(summary)\n\n"
            "plt.figure(figsize=(7, 4))\n"
            "plt.hist(sub['chirps_z'].dropna(), bins=28, color='#ffd166', edgecolor='black', alpha=0.85)\n"
            "plt.axvline(wet_threshold, color='#ffe600', linestyle='--', label='wet threshold')\n"
            "plt.title('Round42 validation CHIRPS z-score distribution')\n"
            "plt.legend()\n"
            "plt.show()"
        ),
        md_cell(
            "## Step 8. Interpretation\n\n"
            "**这个步骤做什么**\n"
            "把 round42 challenger-push 放回平台期策略中解释。\n\n"
            "**为什么要做这个步骤**\n"
            "平台期最容易被误解成“重复提交”，但其实很多 tied-best 版本是在确认边界安全范围。\n\n"
            "**本分支结论**\n"
            "- `0.60 / 0.60` challenger 把 round37 的 corridor 推到了更远的外边界。\n"
            "- CHIRPS 门控只在湿月对 EC 做回退，因此风险控制仍然清晰。\n"
            "- 这本 notebook 体现了后期 plateau 阶段的典型思路：先 push，再用小门控把最危险的点收回来。"
        ),
    ]
    nb['cells'] = cells
    return nb


def write_notebook(path: Path, notebook: nbf.NotebookNode) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, path)


def write_manifest() -> None:
    manifest = [
        {
            'title': 'Official Benchmark Reference',
            'path': 'notebooks/reference_benchmark_model_notebook_snowflake.ipynb',
            'summary': 'Official starter notebook from the challenge package.',
        },
        {
            'title': 'Round 11 EC Guard Full Workflow',
            'path': 'notebooks/v11_4_guard_ec.ipynb',
            'summary': 'Full workflow notebook for the early EC-focused stabilization phase.',
        },
        {
            'title': 'Round 15 TA Refine Push Full Workflow',
            'path': 'notebooks/v15_3_ta_refine_push.ipynb',
            'summary': 'Full workflow notebook for the TA-focused refinement phase that moved the score into the mid-0.36 range.',
        },
        {
            'title': 'Round 20 Structural TA+EC Full Workflow',
            'path': 'notebooks/v20_4_ta_ec_struct_farcal_alt.ipynb',
            'summary': 'Full workflow notebook for the structural TA+EC routing phase before the later plateau.',
        },
        {
            'title': 'Round 37 Hydro Corridor Breakthrough',
            'path': 'notebooks/v37_5_ta40_ec40_push.ipynb',
            'summary': 'Full workflow notebook for the first 0.376 breakthrough using the 40/40 Hydro corridor push.',
        },
        {
            'title': 'Round 38 CHIRPS Safe Probe',
            'path': 'notebooks/v38_5_chirps_delta_safe.ipynb',
            'summary': 'Full workflow notebook showing how CHIRPS wet-month gating entered the late-stage frontier safely.',
        },
        {
            'title': 'Round 42 Challenger Push',
            'path': 'notebooks/v42_5_ta60_ec60_challenger_push.ipynb',
            'summary': 'Full workflow notebook for a late plateau challenger that pushed TA/EC outward with a CHIRPS-based EC guard.',
        },
    ]
    (NOTEBOOKS / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

    readme = """# Selected Notebooks

These are the public-facing notebooks that the showcase page links to.

Every notebook in this list is a full workflow notebook rather than a brief:
- package imports
- official GitHub data loading
- cleaning / feature construction
- strategy rendering
- export / diagnostics

Selected set:
- `reference_benchmark_model_notebook_snowflake.ipynb`
  - Official benchmark reference from the challenge package.
- `v11_4_guard_ec.ipynb`
  - Early EC-focused stabilization in full workflow form.
- `v15_3_ta_refine_push.ipynb`
  - TA refinement phase in full workflow form.
- `v20_4_ta_ec_struct_farcal_alt.ipynb`
  - Structural TA+EC phase in full workflow form.
- `v37_5_ta40_ec40_push.ipynb`
  - Breakthrough Hydro corridor notebook for the first 0.376 result.
- `v38_5_chirps_delta_safe.ipynb`
  - CHIRPS-gated safe probe notebook from the later frontier stage.
- `v42_5_ta60_ec60_challenger_push.ipynb`
  - Plateau challenger notebook showing a push-with-guard design.

Supporting CSV assets for the later notebooks live in `notebooks/assets/` so the public notebooks can explain their anchor files directly.
"""
    (NOTEBOOKS / 'README.md').write_text(readme, encoding='utf-8')


def main() -> None:
    NOTEBOOKS.mkdir(parents=True, exist_ok=True)
    copy_fullflow_notebooks()
    copy_public_assets()
    write_notebook(NOTEBOOKS / 'v37_5_ta40_ec40_push.ipynb', v37_notebook())
    write_notebook(NOTEBOOKS / 'v38_5_chirps_delta_safe.ipynb', v38_notebook())
    write_notebook(NOTEBOOKS / 'v42_5_ta60_ec60_challenger_push.ipynb', v42_notebook())
    write_manifest()
    print('Public notebooks rebuilt.')


if __name__ == '__main__':
    main()
