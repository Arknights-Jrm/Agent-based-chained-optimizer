from orchestrator.pipeline import run_optimization_pipeline
from simulator.hfss_client import parse_value_with_units


def metric_from_output_variable(design, variable_name="objective"):
    """
    默认示例：从 HFSS 设计变量中读取目标值。
    你可以按项目需求替换为 ReportSetup 数据提取逻辑。
    """
    raw_value = design.GetVariableValue(variable_name)
    parsed = parse_value_with_units(raw_value)
    if parsed is None:
        raise ValueError(f"无法解析指标变量 {variable_name}: {raw_value}")
    return parsed

if __name__ == "__main__":
    antenna_config = {
        "patch_length": (0.01, 0.1),
        "patch_width": (0.01, 0.1),
        "substrate_height": (0.001, 0.01),
        "feed_position_x": None,
        "feed_position_y": None,
    }

    result = run_optimization_pipeline(
        antenna_config=antenna_config,
        project_name=None,
        design_name=None,
        n_calls=40,
        metric_evaluator=lambda design: metric_from_output_variable(design, "objective"),
        default_unit="m",
        target_value=None,
        patience=8,
        min_delta=1e-6,
        history_file="optimization_history.json",
    )

    print("优化完成")
    print("最优解:", result["best_solution"])
    print("最佳目标值:", result["best_value"])
    print("评估次数:", result["n_evaluations"])