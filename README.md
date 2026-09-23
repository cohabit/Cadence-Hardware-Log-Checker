# Cadence-Hardware-Log-Checker

脱敏样本驱动的 Cadence/EDA 硬件日志解析与测试性核查 Demo。项目把固定包头、动态字段和分段日志流式解析成 Pandas DataFrame，再将实测参数与结构化规则逐字段比对，输出异常差异报告。

> 仓库不包含涉密 EDA 工程文件。`data/` 中的日志和规则均为模拟样本；规则抽取模块用 JSON 文件模拟本地模型输出，最终判定由程序化规则完成。

## 处理链路

```text
Cadence 日志
  -> 固定包头/字段识别
  -> Python 正则流式清洗
  -> 元器件/焊盘 DataFrame
  -> 结构化测试规则快照
  -> 电压应力、间距等逐字段比对
  -> CSV + JSON 审计报告
```

## 工程结构

```text
core/log_parser.py       流式日志解析和解析统计
core/rule_extractor.py   规则 JSON 校验；可替换为本地 Qwen3-32B 抽取适配器
core/knowledge_base.py   脱敏演示规则和阈值查询
core/cross_checker.py    应力比例、间距和异常等级核查
data/                    模拟日志与规则快照
runtime_output/          运行产物（已被 gitignore 忽略）
demo.py                  端到端演示和 5 万行压测
```

## 运行

```bash
pip install -r requirements.txt
python demo.py
```

会生成：

- `runtime_output/cadence_parsed_components.csv`：结构化元器件数据；
- `runtime_output/violations_summary.csv`：异常差异与整改建议；
- `runtime_output/extracted_rules.json`：版本化规则快照；
- `runtime_output/testability_cross_check_report.json`：解析统计、覆盖维度、性能和审计结果。

## 面试边界

- 解析吞吐量只以本机运行结果为准，README 不预置固定性能数字。
- 规则抽取和规则判定分离：模型可以抽取候选 JSON，但不能绕过程序化阈值校验。
- 公开仓库是个人脱敏验证 Demo，不等同于涉密项目的完整交付系统。
