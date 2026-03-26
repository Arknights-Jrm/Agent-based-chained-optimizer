from skopt import gp_minimize


class BayesianOptimizer:
    def __init__(self, param_space, simulator_func):
        self.param_space = param_space
        self.simulator_func = simulator_func
        self._result = None

    def run_optimization(self, n_calls=40, callbacks=None):
        self._result = gp_minimize(
            func=self.simulator_func,
            dimensions=self.param_space,
            n_calls=n_calls,
            random_state=42,
            callback=callbacks,
        )

    def get_best_solution(self):
        if self._result is None:
            raise RuntimeError("请先调用 run_optimization()")
        return {
            dim.name: val
            for dim, val in zip(self.param_space, self._result.x)
        }
