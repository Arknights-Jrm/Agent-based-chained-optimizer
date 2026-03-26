# HFSS + Bayesian Optimizer 改造清单

## 1. 改造目标

- 统一使用 `optimizer/bayesian.py` 作为唯一优化框架。
- `hfss_parameter_sweep.py` 仅保留 HFSS 连接与参数读写相关能力，不再使用其中 `bayes_opt` 优化流程。
- 将流程拆分为三层：
  - 编排层：主流程、循环、终止条件
  - 工作层：HFSS 适配、优化器、目标函数计算
  - 展示层：CLI（后续可扩展简单前端）

## 2. 最终建议文件架构

```text
Agent-based-chained-optimizer/
├─ main.py
├─ config.py
├─ orchestrator/
│  ├─ __init__.py
│  ├─ pipeline.py
│  └─ stopping.py
├─ optimizer/
│  ├─ __init__.py
│  └─ bayesian.py
├─ simulator/
│  ├─ __init__.py
│  ├─ interface.py
│  └─ hfss_client.py
├─ utils/
│  ├─ history.py
│  └─ logger.py
├─ hfss_parameter_sweep.py
└─ docs/
  └─ REFACTOR_CHECKLIST.md
```

说明：
- 兼容你当前代码，保留原文件 `hfss_parameter_sweep.py`，但仅作为“HFSS连接能力来源/过渡文件”。
- 推荐新增 `simulator/hfss_client.py`，逐步把 HFSS 连接函数从旧脚本迁移到这里。

## 3. 现有文件保留与改造范围

### 3.1 可直接保留

1. `optimizer/bayesian.py`
- 保留 `BayesianOptimizer` 类。
- 作为全项目唯一优化入口。

2. `config.py`
- 保留 `HFSS_VARIABLE_POOL`。
- 保留 `build_param_space(antenna_config)`。

3. `utils/history.py`
- 保留 `save_history(...)`。
- 建议后续扩展保存字段：迭代轮次、时间戳、metric 名称。

### 3.2 仅部分保留（重点）

`hfss_parameter_sweep.py` 仅保留以下函数逻辑（可先原样，后续迁移到 `simulator/hfss_client.py`）：

- `open_hfss(...)`
- `parse_value_with_units(...)`
- `get_hfss_parameters(...)`
- `set_hfss_parameters(...)`

建议处理：
- 删除或停用 `bayes_optimize(...)`。
- 删除或停用 `if __name__ == "__main__":` 脚本入口。
- 删除对 `bayes_opt` 的依赖导入。

### 3.3 需要替换/扩展

1. `simulator/interface.py`
- 当前是数学占位函数。
- 需要改成调用 HFSS 的真实仿真接口，签名建议保持 `external_simulation_interface(params)` 供 `BayesianOptimizer` 直接调用。

2. `main.py`
- 当前已接入 `optimizer/bayesian.py`，这点正确。
- 需要从占位仿真切换到真实 HFSS 流程（通过 `simulator/hfss_client.py` + `simulator/interface.py`）。

## 4. 需要新增的文件与代码职责

1. `orchestrator/pipeline.py`
- 职责：主循环编排（参数建议 -> HFSS设置 -> 仿真 -> 指标回传 -> 优化迭代）。
- 对外方法建议：`run_optimization_pipeline(config)`。

2. `orchestrator/stopping.py`
- 职责：终止条件判定。
- 建议规则：
  - 达到目标阈值
  - 连续 N 轮改进小于 epsilon
  - 达到最大迭代次数

3. `simulator/hfss_client.py`
- 职责：承接原 `hfss_parameter_sweep.py` 的 HFSS 能力函数。
- 建议提供：
  - `connect(project_name, design_name)`
  - `get_parameters(design)`
  - `set_parameters(design, params, with_unit=True)`
  - `run_and_extract_metric(design, metric_spec)`

4. `utils/logger.py`
- 职责：统一日志，区分 INFO/WARN/ERROR。

## 5. 关键接口约定（避免后续冲突）

1. 优化器输入输出
- 输入：参数向量列表（按 `param_space` 顺序）。
- 输出：标量目标值（越小越优，或统一成越小越优）。

2. HFSS 仿真接口
- 输入：参数向量
- 步骤：映射到变量名 -> 写入 HFSS -> 执行 Analyze -> 读取指标
- 输出：目标函数值

3. 变量顺序一致性
- 统一使用 `param_space` 中维度顺序进行索引。
- 禁止在接口中再次按字典无序展开。

## 6. 分阶段实施建议

1. 第一阶段（最小可用）
- 保持 `main.py + optimizer/bayesian.py`。
- 把 `simulator/interface.py` 从数学占位替换为真实 HFSS 调用。

2. 第二阶段（结构化）
- 新增 `orchestrator/pipeline.py` 和 `simulator/hfss_client.py`。
- `main.py` 只负责读取配置并调用 pipeline。

3. 第三阶段（可视化）
- 先做最小展示层（CLI 状态面板）。
- 再评估是否添加 Streamlit 前端。

## 7. 风险与注意事项

- HFSS 报告名称和表达式必须与你工程实际一致，否则读数失败。
- 参数写入单位需要统一（mm/m/GHz），避免隐式单位导致仿真偏差。
- 避免在“设置参数”和“读取指标”两个位置重复触发 `AnalyzeAll()`。
- 同一轮仿真建议加入超时与失败重试。

## 8. 验收标准

- 仅通过 `main.py` 即可执行完整优化闭环。
- 优化调用路径只经过 `optimizer/bayesian.py`。
- `hfss_parameter_sweep.py` 不再承担优化流程。
- 每轮参数与指标可落盘（JSON）并可复盘最优解。
