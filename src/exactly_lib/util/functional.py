import types


def compose_first_and_second(f, g):
    return Composition(g, f)


class Composition:
    def __init__(self, g, f):
        self.g = g
        self.f = f

    def __call__(self, arg):
        return self.g(self.f(arg))


def and_predicate(predicates: list) -> types.FunctionType:
    if not predicates:
        return lambda x: True
    if len(predicates) == 1:
        return predicates[0]
    return _AndPredicate(predicates)


class _AndPredicate:
    def __init__(self, predicates: list):
        self.predicates = predicates

    def __call__(self, *args, **kwargs):
        for predicate in self.predicates:
            if not predicate(*args, **kwargs):
                return False
        return True
