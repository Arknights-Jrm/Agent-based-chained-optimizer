import win32com.client
from bayes_opt import BayesianOptimization
import time
import re

# -----------------------------
# 1. 打开HFSS并获取活动设计
# -----------------------------
def open_hfss(project_name=None, design_name=None):
    print("启动 HFSS...")
    try:
        hfss_app = win32com.client.Dispatch("AnsoftHfss.HfssScriptInterface")
    except Exception as e:
        print("无法启动 HFSS:", e)
        return None

    hfss_desktop = hfss_app.GetAppDesktop()
    print("HFSS 已打开")

    active_project = hfss_desktop.GetActiveProject()
    if active_project is None:
        if project_name:
            print(f"尝试打开项目: {project_name}")
            try:
                active_project = hfss_desktop.OpenProject(project_name)
            except Exception as e:
                print("打开项目失败:", e)
                return None
        else:
            print("请提供 project_name 参数")
            return None

    print(f"活动项目: {active_project.GetName()}")

    active_design = active_project.GetActiveDesign()
    if active_design is None:
        if design_name:
            print(f"尝试激活设计: {design_name}")
            try:
                active_project.SetActiveDesign(design_name)
                active_design = active_project.GetActiveDesign()
            except Exception as e:
                print("激活设计失败:", e)
                return None
        else:
            print("请提供 design_name 参数")
            return None

    print(f"活动设计: {active_design.GetName()}")
    return active_design

# -----------------------------
# 2. 解析带单位的参数
# -----------------------------
def parse_value_with_units(val_str):
    if isinstance(val_str, (int, float)):
        return float(val_str)
    if not isinstance(val_str, str):
        return None

    val_str = val_str.strip().lower()
    match = re.match(r"([-+]?\d*\.?\d+)([a-z]*)", val_str)
    if not match:
        return None
    value, unit = match.groups()
    value = float(value)
    unit_multipliers = {
        "nm": 1e-9,
        "um": 1e-6,
        "mm": 1e-3,
        "cm": 1e-2,
        "m": 1,
        "ghz": 1e9,
        "mhz": 1e6,
        "khz": 1e3,
    }
    multiplier = unit_multipliers.get(unit, 1)
    return value * multiplier

# -----------------------------
# 3. 获取HFSS参数
# -----------------------------
def get_hfss_parameters(design):
    params = {}
    try:
        var_list = design.GetVariables()  # 获取所有参数
        print("发现参数:", var_list)
        for name in var_list:
            try:
                val_str = design.GetVariableValue(name)
                val = parse_value_with_units(val_str)
                if val is not None:
                    params[name] = val
            except Exception as e:
                print(f"获取参数 {name} 失败:", e)
    except Exception as e:
        print("无法获取设计参数:", e)
    return params

# -----------------------------
# 4. 设置HFSS参数
# -----------------------------
def set_hfss_parameters(design, param_dict):
    for name, value in param_dict.items():
        try:
            design.SetVariableValue(name, value)
        except Exception as e:
            print(f"设置参数 {name} 失败:", e)
    try:
        design.AnalyzeAll()
    except Exception as e:
        print("仿真启动失败:", e)
    print("HFSS 已更新参数并开始仿真")

# -----------------------------
# 5. 仿真并返回指标
# -----------------------------
def run_simulation_and_get_metric(design, metric_name="S11", freq=2.4e9):
    try:
        design.AnalyzeAll()
        time.sleep(1)
        # 获取 S11 或 Gain 示例
        results_module = design.GetModule("ReportSetup")
        if metric_name.upper() == "S11":
            # 注意：以下只是示例，需要根据你的 HFSS 报告名称修改
            s11 = float(results_module.GetSolutionData("S", "S(1,1)"))  # 替换为实际端口
            return -s11
        elif metric_name.upper() == "GAIN":
            gain = float(results_module.GetSolutionData("Gain", "Gain(1)"))  # 替换为实际报告
            return gain
        else:
            return 0
    except Exception as e:
        print("获取指标失败:", e)
        return 0

# -----------------------------
# 6. 贝叶斯优化
# -----------------------------
def bayes_optimize(design, metric_name="S11", freq=2.4e9, init_points=3, n_iter=10):
    current_params = get_hfss_parameters(design)
    if not current_params:
        print("没有可优化的参数，程序退出")
        return {}

    pbounds = {name: (value * 0.5, value * 1.5) for name, value in current_params.items()}
    print("优化参数范围:", pbounds)

    def objective(**params):
        set_hfss_parameters(design, params)
        metric = run_simulation_and_get_metric(design, metric_name=metric_name, freq=freq)
        print(f"当前参数: {params}, 指标: {metric}")
        return metric

    optimizer = BayesianOptimization(
        f=objective, pbounds=pbounds, random_state=42, allow_duplicate_points=True
    )
    optimizer.maximize(init_points=init_points, n_iter=n_iter)
    print("优化完成")
    print("最优参数:", optimizer.max['params'])
    return optimizer.max['params']

# -----------------------------
# 7. 主程序
# -----------------------------
if __name__ == "__main__":
    project_path = r"C:\Users\LBY\Documents\HFSS\my_project.aedt"  # 修改为你的路径
    design_name = "MyDesign"  # 修改为你的设计名

    design = open_hfss(project_name=project_path, design_name=design_name)
    if design is None:
        print("无法获取HFSS设计，程序退出")
        exit()

    params = get_hfss_parameters(design)
    print("当前HFSS参数:", params)

    best_params = bayes_optimize(design, metric_name="S11", freq=2.4e9, init_points=3, n_iter=5)
    print("最优参数:", best_params)

    if best_params:
        set_hfss_parameters(design, best_params)
        print("优化完成并更新HFSS设计")