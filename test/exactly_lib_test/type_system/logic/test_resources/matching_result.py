from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib.util.description_tree import renderers, tree


def of(x: bool,
       header: str = 'header') -> MatchingResult:
    return MatchingResult(
        x,
        renderers.Constant(
            tree.Node.empty(header, x)
        )
    )
