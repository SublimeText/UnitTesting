class StackMeter:

    def __init__(self, depth=0):
        super().__init__()
        self.depth = depth

    def __enter__(self):  # noqa: D105 Missing docstring in magic method
        depth = self.depth
        self.depth += 1
        return depth

    def __exit__(self, *exc_info):  # noqa: D105 Missing docstring in magic method
        self.depth -= 1
