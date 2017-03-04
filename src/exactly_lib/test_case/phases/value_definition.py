class ValueUsage(object):
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class ValueReference(ValueUsage):
    pass


class ValueDefinition(ValueUsage):
    def __init__(self, name: str):
        super().__init__(name)


def empty_symbol_table() -> set:
    return set()


def singleton_symbol_table(element) -> set:
    return {element}
