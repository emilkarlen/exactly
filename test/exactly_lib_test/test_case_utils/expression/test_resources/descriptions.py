from typing import Sequence

from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.expression.grammar import OperatorExpressionDescription
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.str_.name import NameWithGenderWithFormatting, NameWithGender
from exactly_lib.util.textformat.structure.core import ParagraphItem


class ConstantPrimitiveExprDescription(grammar.PrimitiveExpressionDescriptionWithNameAsInitialSyntaxToken):
    def __init__(self,
                 argument_usage_list: Sequence[a.ArgumentUsage],
                 description_rest: Sequence[ParagraphItem],
                 syntax_elements: Sequence[SyntaxElementDescription] = (),
                 see_also_targets: Sequence[SeeAlsoTarget] = (),
                 ):
        self._argument_usage_list = argument_usage_list
        self._description_rest = description_rest
        self._see_also_targets = list(see_also_targets)
        self._syntax_elements = syntax_elements

    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return self._argument_usage_list

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return self._description_rest

    @property
    def syntax_elements(self) -> Sequence[SyntaxElementDescription]:
        return self._syntax_elements

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return self._see_also_targets


class ConstantOperatorExpressionDescription(OperatorExpressionDescription):
    def __init__(self,
                 description_rest: Sequence[ParagraphItem],
                 syntax_elements: Sequence[SyntaxElementDescription] = (),
                 see_also_targets: Sequence[SeeAlsoTarget] = (),
                 ):
        self._description_rest = description_rest
        self._see_also_targets = list(see_also_targets)
        self._syntax_elements = syntax_elements

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return self._description_rest

    @property
    def syntax_elements(self) -> Sequence[SyntaxElementDescription]:
        return self._syntax_elements

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return self._see_also_targets


CONCEPT = grammar.Concept(
    NameWithGenderWithFormatting(
        NameWithGender('a',
                       'concept singular',
                       'concept plural')),
    'type-system-name',
    a.Named('SYNTAX-ELEMENT-NAME'))