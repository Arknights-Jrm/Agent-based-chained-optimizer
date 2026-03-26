# Agent-based Chained Optimizer (HFSS)

本项目用于将 HFSS 参数化模型与 Python 贝叶斯优化串联，形成自动迭代优化闭环。

核心原则：
- 优化框架统一使用 `optimizer/bayesian.py`。
- `hfss_parameter_sweep.py` 仅作为 HFSS 连接能力来源，不作为优化主流程。

## 1. 项目目标

通过主入口统一执行以下流程：
1. 连接已打开的 HFSS（或按路径打开项目并激活设计）。
2. 获取并设置待优化参数。
3. 调用贝叶斯优化器生成候选参数。
4. 触发 HFSS 仿真并提取指标（如 S11、Gain）。
5. 根据终止条件循环，直到达到目标或迭代上限。

## 2. 当前代码能力概览

已具备：
- 动态参数空间构建：`config.py`
- 贝叶斯优化框架（skopt）：`optimizer/bayesian.py`
- HFSS 客户端能力：`simulator/hfss_client.py`
- 编排层闭环：`orchestrator/pipeline.py` + `orchestrator/stopping.py`
- 历史记录保存：`utils/history.py`
- 兼容导出层：`hfss_parameter_sweep.py`

## 3. 建议架构（三层）

- 第一层：编排层
  - `main.py`：程序唯一入口
  - `orchestrator/pipeline.py`：优化循环编排
  - `orchestrator/stopping.py`：终止条件

- 第二层：工作层
  - `optimizer/bayesian.py`：优化算法
  - `simulator/hfss_client.py`：HFSS 会话、参数、仿真读数
  - `simulator/interface.py`：面向优化器的统一仿真接口

- 第三层：展示层
  - 先用 CLI 输出状态与结果
  - 后续可扩展 Streamlit 作为简易前端

## 4. 目录（当前 + 规划）

```text
Agent-based-chained-optimizer/
├─ main.py
├─ config.py
├─ hfss_parameter_sweep.py
├─ orchestrator/
│  ├─ __init__.py
│  ├─ pipeline.py
│  └─ stopping.py
├─ optimizer/
│  └─ bayesian.py
├─ simulator/
│  ├─ interface.py
│  └─ hfss_client.py
├─ utils/
│  ├─ history.py
│  └─ logger.py
└─ docs/
   └─ REFACTOR_CHECKLIST.md
```

## 5. 运行前准备

1. 安装 Python 依赖（示例）
- `scikit-optimize`
- `pywin32`

当前主流程不依赖 `bayesian-optimization`。

2. 打开 HFSS 并确保：
- 项目可访问
- 设计名称正确
- 报告名称和表达式与代码一致

## 6. 最小运行路径（当前）

当前 `main.py` 已调用编排层并连接 HFSS 进行真实闭环。

默认示例中，目标值通过 HFSS 设计变量 `objective` 读取。
如果你的工程不是这个变量名，请修改 `main.py` 中 `metric_from_output_variable(...)`。

```bash
python main.py
```

输出包含：
- 优化维度
- 优化变量
- 最优解（按变量名映射）

## 7. 迁移到真实 HFSS 闭环的步骤

1. 按项目实际报告，替换 `main.py` 中的指标提取函数。
2. 确认参数单位是否为米（默认 `default_unit="m"`），必要时调整。
3. 根据任务目标设置 `target_value`、`patience`、`min_delta`。
4. 检查 `optimization_history.json` 的落盘结果是否符合预期。

## 8. 设计约定

- 参数顺序以 `param_space` 顺序为准。
- 建议统一目标方向为“最小化”。
- 仅保留一个优化框架（`optimizer/bayesian.py`），避免双框架并行。

## 9. 常见问题

1. 无法连接 HFSS
- 检查 HFSS 是否已启动
- 检查 COM 接口是否可用（`pywin32` 是否安装）

2. 能仿真但读不到指标
- 检查报告模块名称
- 检查表达式（如 `S(1,1)`）是否与工程一致

3. 优化过程很慢
- 减少每轮仿真次数
- 合理设置参数边界
- 增加终止条件（目标阈值、最小改进量）

## 10. 下一步建议

- 先完成 `simulator/hfss_client.py` 与 `simulator/interface.py` 改造，打通真实闭环。
- 再补 `orchestrator/pipeline.py`，让 `main.py` 成为纯入口。
- 最后再加前端（推荐先用 Streamlit）。
