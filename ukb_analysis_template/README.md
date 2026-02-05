# UKB Analysis Template (通用版)

这是一个可复制粘贴、可直接二次开发的 **UK Biobank / 通用队列数据分析模板**。
目标是支持：
- 各种数据来源（TSV/CSV/Parquet，字段命名不统一也可）
- 各种结局类型（连续型、二分类、生存分析）
- 各种课题（流行病学、医学统计、风险预测、敏感性分析）

> ⚠️ 请先阅读 `config/project.example.yaml` 和 `config/fields.example.yaml`，把所有 `REPLACE_ME` 项替换成你自己的内容。

## 1) 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config/project.example.yaml config/project.yaml
cp config/fields.example.yaml config/fields.yaml
```

然后替换配置中的 `REPLACE_ME` 值，再运行：

```bash
python scripts/run_pipeline.py --project config/project.yaml --fields config/fields.yaml
```

## 2) 目录说明

```text
ukb_analysis_template/
├─ config/
│  ├─ project.example.yaml      # 项目参数（路径、模型、输出）
│  └─ fields.example.yaml       # 字段映射（原始列名 -> 标准列名）
├─ src/ukb_pipeline/
│  ├─ config.py                 # 配置加载/校验
│  ├─ io.py                     # 数据读取与写出
│  ├─ preprocess.py             # 缺失值、异常值、编码处理
│  ├─ cohort.py                 # 纳排标准与样本流程
│  ├─ models.py                 # 线性/Logistic/Cox
│  ├─ evaluation.py             # 指标与结果整理
│  ├─ report.py                 # 输出表格和日志摘要
│  └─ utils.py
├─ scripts/
│  └─ run_pipeline.py           # 一键执行
├─ tests/
│  └─ test_smoke.py             # 冒烟测试
└─ outputs/
   ├─ tables/
   ├─ figures/
   └─ models/
```

## 3) 你需要替换的地方（务必）

1. `config/project.yaml`
   - `data.input_path` → 你的数据文件路径
   - `data.format` → `csv` / `tsv` / `parquet`
   - `analysis.outcome.type` → `continuous` / `binary` / `survival`
   - `analysis.outcome.column` → 你的结局变量列名
   - `analysis.exposure.columns` → 暴露变量
   - `analysis.covariates.columns` → 协变量

2. `config/fields.yaml`
   - `rename_map`：把原始列名映射到标准列名
   - `missing_codes`：你数据里的缺失编码（如 `-1`, `-3`, `999`）
   - `category_maps`：分类变量重编码方案

3. 生存分析专用（当 `outcome.type=survival`）
   - `analysis.outcome.time_column`（随访时间）
   - `analysis.outcome.event_column`（事件0/1）

## 4) 输出内容

- `outputs/tables/model_summary.csv`：核心回归结果（系数、OR/HR、CI、P值）
- `outputs/tables/cohort_flow.csv`：纳排流程
- `outputs/tables/data_profile.csv`：变量缺失与分布概览
- `logs/pipeline.log`：全流程日志

## 5) 适配建议

- 复杂课题可在 `preprocess.py` 增加：倾向评分、IPW、多重插补。
- 组学或高维特征可在 `models.py` 增加：L1/L2、XGBoost、交叉验证。
- 多模型批量跑可扩展 `project.yaml` 的 `analysis.model_grid`。

## 6) 合规提醒

- UKB 数据使用需遵守 UKB 协议与伦理审批。
- 输出文件中避免泄露直接可识别信息。
