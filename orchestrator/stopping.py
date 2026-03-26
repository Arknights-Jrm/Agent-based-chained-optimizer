class EarlyStopper:
    def __init__(self, target_value=None, patience=None, min_delta=0.0):
        self.target_value = target_value
        self.patience = patience
        self.min_delta = float(min_delta)
        self.best_so_far = None
        self.no_improve_steps = 0

    def __call__(self, result):
        if len(result.func_vals) == 0:
            return False

        current_best = float(min(result.func_vals))

        if self.target_value is not None and current_best <= self.target_value:
            print(f"达到目标阈值，提前停止。best={current_best}")
            return True

        if self.patience is None:
            return False

        if self.best_so_far is None:
            self.best_so_far = current_best
            self.no_improve_steps = 0
            return False

        if current_best < (self.best_so_far - self.min_delta):
            self.best_so_far = current_best
            self.no_improve_steps = 0
            return False

        self.no_improve_steps += 1
        if self.no_improve_steps >= self.patience:
            print(
                "连续未改进轮次达到阈值，提前停止。"
                f"best={current_best}, patience={self.patience}"
            )
            return True

        return False
