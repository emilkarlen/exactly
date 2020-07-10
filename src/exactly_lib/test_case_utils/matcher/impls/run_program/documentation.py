from abc import ABC
from typing import Sequence

from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.util.cli_syntax.elements import argument as a


class SyntaxDescriptionBase(grammar.PrimitiveExpressionDescriptionWithNameAsInitialSyntaxToken, ABC):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [
            syntax_elements.PROGRAM_SYNTAX_ELEMENT.single_mandatory
        ]

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return syntax_elements.PROGRAM_SYNTAX_ELEMENT.cross_reference_target,
