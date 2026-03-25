from optimizer.bayesian import BayesianOptimizer
from simulator.interface import external_simulation_interface
from config import build_param_space

if __name__ == "__main__":
    # 自定义优化维度（示例：只优化3个核心变量）
    antenna_config = {
        "patch_length": (0.01, 0.1),
        "patch_width": (0.01, 0.1),
        "substrate_height": (0.001, 0.01),
        "feed_position_x": None,  # 不优化
        "feed_position_y": None   # 不优化
    }

    # 动态构建参数空间（自适应维度）
    PARAM_SPACE = build_param_space(antenna_config)
    print(f"优化维度：{len(PARAM_SPACE)}")
    print(f"优化变量：{[dim.name for dim in PARAM_SPACE]}")

    # 初始化并运行优化
    opt = BayesianOptimizer(
        param_space=PARAM_SPACE,
        simulator_func=external_simulation_interface
    )
    opt.run_optimization(n_calls=40)

    # 打印带变量名的最优解
    best_sol = opt.get_best_solution()
    print("最优解：", best_sol)