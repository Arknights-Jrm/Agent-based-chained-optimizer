import re
from typing import Callable, Dict, Optional

try:
    import win32com.client  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    win32com = None


class HFSSConnectionError(RuntimeError):
    pass


def open_hfss(project_name: Optional[str] = None, design_name: Optional[str] = None):
    if win32com is None:
        raise HFSSConnectionError("未安装 pywin32，无法连接 HFSS")

    try:
        hfss_app = win32com.client.Dispatch("AnsoftHfss.HfssScriptInterface")
    except Exception as exc:
        raise HFSSConnectionError(f"启动 HFSS 失败: {exc}") from exc

    hfss_desktop = hfss_app.GetAppDesktop()
    active_project = hfss_desktop.GetActiveProject()

    if active_project is None:
        if not project_name:
            raise HFSSConnectionError("没有活动项目，请提供 project_name")
        try:
            active_project = hfss_desktop.OpenProject(project_name)
        except Exception as exc:
            raise HFSSConnectionError(f"打开项目失败: {exc}") from exc

    active_design = active_project.GetActiveDesign()
    if active_design is None:
        if not design_name:
            raise HFSSConnectionError("没有活动设计，请提供 design_name")
        try:
            active_project.SetActiveDesign(design_name)
            active_design = active_project.GetActiveDesign()
        except Exception as exc:
            raise HFSSConnectionError(f"激活设计失败: {exc}") from exc

    return active_design


def parse_value_with_units(val_str):
    if isinstance(val_str, (int, float)):
        return float(val_str)
    if not isinstance(val_str, str):
        return None

    val_str = val_str.strip().lower()
    match = re.match(r"([-+]?\d*\.?\d+)([a-z]*)", val_str)
    if not match:
        return None

    value_str, unit = match.groups()
    value = float(value_str)
    unit_multipliers = {
        "nm": 1e-9,
        "um": 1e-6,
        "mm": 1e-3,
        "cm": 1e-2,
        "m": 1.0,
        "khz": 1e3,
        "mhz": 1e6,
        "ghz": 1e9,
    }
    return value * unit_multipliers.get(unit, 1.0)


def get_hfss_parameters(design) -> Dict[str, float]:
    params: Dict[str, float] = {}
    var_list = design.GetVariables()
    for name in var_list:
        try:
            raw_value = design.GetVariableValue(name)
            parsed = parse_value_with_units(raw_value)
            if parsed is not None:
                params[name] = parsed
        except Exception:
            continue
    return params


def _format_hfss_value(value, default_unit: str = "m"):
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        return f"{value}{default_unit}"
    raise ValueError(f"不支持的参数类型: {type(value)}")


def set_hfss_parameters(
    design,
    param_dict: Dict[str, object],
    trigger_simulation: bool = False,
    default_unit: str = "m",
):
    for name, value in param_dict.items():
        hfss_value = _format_hfss_value(value, default_unit=default_unit)
        design.SetVariableValue(name, hfss_value)

    if trigger_simulation:
        design.AnalyzeAll()


def run_analysis(design):
    design.AnalyzeAll()


def run_and_extract_metric(design, metric_evaluator: Callable[[object], float]) -> float:
    run_analysis(design)
    metric = metric_evaluator(design)
    try:
        return float(metric)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"指标值无法转换为 float: {metric}") from exc
