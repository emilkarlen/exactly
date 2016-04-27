class Composition:
    def __init__(self, g, f):
        self.g = g
        self.f = f

    def __call__(self, arg):
        return self.g(self.f(arg))
