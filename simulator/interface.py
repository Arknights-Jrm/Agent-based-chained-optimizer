from simulator.hfss_client import run_and_extract_metric, set_hfss_parameters


_RUNTIME_CONTEXT = {
    "design": None,
    "param_space": None,
    "metric_evaluator": None,
    "default_unit": "m",
}


def configure_simulation(design, param_space, metric_evaluator, default_unit="m"):
    _RUNTIME_CONTEXT["design"] = design
    _RUNTIME_CONTEXT["param_space"] = param_space
    _RUNTIME_CONTEXT["metric_evaluator"] = metric_evaluator
    _RUNTIME_CONTEXT["default_unit"] = default_unit


def external_simulation_interface(params):
    design = _RUNTIME_CONTEXT["design"]
    param_space = _RUNTIME_CONTEXT["param_space"]
    metric_evaluator = _RUNTIME_CONTEXT["metric_evaluator"]
    default_unit = _RUNTIME_CONTEXT["default_unit"]

    if design is None or param_space is None or metric_evaluator is None:
        raise RuntimeError("仿真接口未初始化，请先调用 configure_simulation()")

    param_dict = {
        dim.name: val
        for dim, val in zip(param_space, params)
    }

    set_hfss_parameters(
        design=design,
        param_dict=param_dict,
        trigger_simulation=False,
        default_unit=default_unit,
    )
    return run_and_extract_metric(design, metric_evaluator)