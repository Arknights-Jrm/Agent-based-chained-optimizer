from skopt.space import Real

# HFSS 常用变量池
HFSS_VARIABLE_POOL = {
    "patch_length": Real(low=0.01, high=0.1, prior="uniform"),
    "patch_width": Real(low=0.01, high=0.1, prior="uniform"),
    "substrate_height": Real(low=0.001, high=0.01, prior="uniform"),
    "feed_position_x": Real(low=0.005, high=0.095, prior="uniform"),
    "feed_position_y": Real(low=0.005, high=0.095, prior="uniform"),
}

def build_param_space(antenna_config):
    param_space = []
    valid_vars = set(HFSS_VARIABLE_POOL.keys())
    for var_name, bounds in antenna_config.items():
        if bounds is None:
            continue
        if var_name not in valid_vars:
            raise ValueError(f"未知变量：{var_name}")
        param_space.append(Real(name=var_name, low=bounds[0], high=bounds[1], prior="uniform"))
    if not param_space:
        raise ValueError("参数空间为空，请至少指定一个优化变量！")
    return param_space