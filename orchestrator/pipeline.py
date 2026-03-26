from config import build_param_space
from optimizer.bayesian import BayesianOptimizer
from orchestrator.stopping import EarlyStopper
from simulator.hfss_client import get_hfss_parameters, open_hfss
from simulator.interface import configure_simulation, external_simulation_interface
from utils.history import save_history


def run_optimization_pipeline(
    antenna_config,
    project_name=None,
    design_name=None,
    n_calls=40,
    metric_evaluator=None,
    default_unit="m",
    target_value=None,
    patience=None,
    min_delta=0.0,
    history_file="optimization_history.json",
):
    if metric_evaluator is None:
        raise ValueError("metric_evaluator 不能为空")

    param_space = build_param_space(antenna_config)
    print(f"优化维度: {len(param_space)}")
    print(f"优化变量: {[dim.name for dim in param_space]}")

    design = open_hfss(project_name=project_name, design_name=design_name)
    initial_params = get_hfss_parameters(design)
    print(f"HFSS 当前参数数量: {len(initial_params)}")

    configure_simulation(
        design=design,
        param_space=param_space,
        metric_evaluator=metric_evaluator,
        default_unit=default_unit,
    )

    history_params = []
    history_perf = []

    def objective(params):
        value = external_simulation_interface(params)
        mapped = {dim.name: val for dim, val in zip(param_space, params)}
        history_params.append(mapped)
        history_perf.append(value)
        print(f"当前目标值: {value}")
        return value

    callbacks = []
    if target_value is not None or patience is not None:
        callbacks.append(
            EarlyStopper(
                target_value=target_value,
                patience=patience,
                min_delta=min_delta,
            )
        )

    optimizer = BayesianOptimizer(
        param_space=param_space,
        simulator_func=objective,
    )
    optimizer.run_optimization(
        n_calls=n_calls,
        callbacks=callbacks if callbacks else None,
    )

    if history_params and history_perf:
        save_history(history_params, history_perf, filename=history_file)

    best_solution = optimizer.get_best_solution()
    best_value = min(history_perf) if history_perf else None

    return {
        "best_solution": best_solution,
        "best_value": best_value,
        "history_file": history_file,
        "n_evaluations": len(history_perf),
    }
