from bayes_opt import BayesianOptimization
import numpy as np

class BayesianOptimizer:
    def __init__(self, param_space, simulator_func):
        self.param_space = param_space
        self.simulator_func = simulator_func
        self.optimizer = None
        self.best_solution = None

    def _objective(self, **params):
        # 将参数字典转换为列表，按照param_space的顺序
        param_values = [params[dim.name] for dim in self.param_space]
        return -self.simulator_func(param_values)  # 假设是最小化，bayes_opt是最大化，所以取负

    def run_optimization(self, n_calls=100):
        # 定义参数边界
        pbounds = {dim.name: (dim.low, dim.high) for dim in self.param_space}
        
        self.optimizer = BayesianOptimization(
            f=self._objective,
            pbounds=pbounds,
            verbose=2,
            random_state=1,
        )
        
        self.optimizer.maximize(init_points=5, n_iter=n_calls-5)

    def get_best_solution(self):
        if self.optimizer is None:
            raise ValueError("Optimization has not been run yet.")
        
        best_params = self.optimizer.max['params']
        # 转换为列表，按照param_space顺序
        param_values = [best_params[dim.name] for dim in self.param_space]
        return param_values