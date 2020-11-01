from exactly_lib.util.description_tree.renderer import NodeRenderer

TraceRenderer = NodeRenderer[bool]


class MatchingResult:
    """The result of applying a matcher."""

    def __init__(self,
                 value: bool,
                 trace: TraceRenderer):
        self._value = value
        self._trace = trace

    @property
    def value(self) -> bool:
        return self._value

    @property
    def trace(self) -> TraceRenderer:
        return self._trace
