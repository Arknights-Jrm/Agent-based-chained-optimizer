import numpy as np
from skopt import gp_minimize
from skopt.utils import use_named_args

class BayesianOptimizer:
    def __init__(self, param_space, simulator_func):
        self.param_space = param_space
        self.param_names = [dim.name for dim in param_space]
        self.simulator_func = simulator_func
        self.history_params = []
        self.history_perf = []
        self.optimization_result = None

        # 算法优化：防止重复采样（提速+避免浪费仿真）
        self.sampled_set = set()

    def _objective_function(self, **params):
        # 生成参数列表
        param_list = [params[name] for name in self.param_names]

        # 去重（非常关键：不重复计算相同尺寸）
        key = tuple(round(v, 6) for v in param_list)
        if key in self.sampled_set:
            return float('inf')
        self.sampled_set.add(key)

        # 运行仿真
        perf = self.simulator_func(param_list)

        # 记录历史
        self.history_params.append(param_list)
        self.history_perf.append(perf)

        return perf

    def run_optimization(self, n_calls=40, n_random_starts=10, random_state=42):
        # 包装目标函数
        obj_wrapped = use_named_args(self.param_space)(self._objective_function)

        # ==============================
        # 🔥 核心：速率 + 全局精度 平衡版
        # ==============================
        self.optimization_result = gp_minimize(
            func=obj_wrapped,
            dimensions=self.param_space,
            n_calls=n_calls,
            n_random_starts=n_random_starts,
            acq_func="gp_hedge",        # 自适应采集函数（速率+精度最强平衡）
            acq_optimizer="lbfgs",      # 快速+高精度
            kappa=2.0,                  # 平衡全局探索 + 局部求精
            xi=0.01,                    # 精细优化
            random_state=random_state,
            verbose=True
        )
        return self.optimization_result

    def get_best_solution(self):
        if not self.optimization_result:
            raise RuntimeError("请先运行 run_optimization()")
            
        best_params = dict(zip(self.param_names, self.optimization_result.x))
        return {
            "best_params": best_params,
            "best_vswr": round(float(self.optimization_result.fun), 4),
            "total_iterations": len(self.history_perf)
        }