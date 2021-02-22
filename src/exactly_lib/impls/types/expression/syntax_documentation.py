import itertools
from typing import List, Sequence

from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, InvokationVariant, \
    cli_argument_syntax_element_description, invokation_variant_from_args
from exactly_lib.definitions import formatting, misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements, concepts, types
from exactly_lib.definitions.entity.syntax_elements import SyntaxElementInfo
from exactly_lib.util import collection, name_and_value
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser
from .grammar import Grammar, PrimitiveDescription, OperatorDescription, ElementWithDescription


def syntax_element_description(grammar: Grammar) -> SyntaxElementDescription:
    return Syntax(grammar).syntax_element_description()


class Syntax:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.concept_argument = a.Single(a.Multiplicity.MANDATORY,
                                         self.grammar.concept.syntax_element)
        self.infix_operators__list = collection.concat_list(grammar.infix_ops_inc_precedence__seq)

        self._tp = TextParser({
            'symbol_concept': formatting.concept_name_with_formatting(concepts.SYMBOL_CONCEPT_INFO.name),
            'concept_name': self.grammar.concept.name,
            'string_type': types.STRING_TYPE_INFO.name,
            'BIN_OP_PRECEDENCE': _BIN_OP_PRECEDENCE,
            'whitespace': misc_texts.WHITESPACE,
        })

    def syntax_element_description(self) -> SyntaxElementDescription:
        return cli_argument_syntax_element_description(
            self.grammar.concept.syntax_element,
            [],
            self.invokation_variants()
        )

    def invokation_variants(self) -> List[InvokationVariant]:
        return (self._invokation_variants_primitive() +
                self._invokation_variants_prefix() +
                self._invokation_variants_infix() +
                self._invokation_variants_symbol_ref() +
                self._invokation_variants_parentheses()
                )

    def syntax_description(self) -> List[ParagraphItem]:
        return (
            self._tp.fnap(_DESCRIPTION__SYNTAX__W_OPERATORS)
            if self.infix_operators__list
            else
            self._tp.fnap(_DESCRIPTION__SYNTAX__WO_OPERATORS)
        )

    def precedence_description(self) -> List[ParagraphItem]:
        num_infix_op_levels = len(self.grammar.infix_ops_inc_precedence)
        has_infix_op = num_infix_op_levels > 0

        if not has_infix_op:
            return []

        has_prefix_ops = bool(self.grammar.prefix_operators__seq)

        if has_prefix_ops:
            return self._precedence_description_w_list()
        else:
            if num_infix_op_levels == 1:
                if len(self.grammar.infix_ops_inc_precedence[0]) <= 1:
                    return []
                else:
                    return self._tp.fnap(_DESCRIPTION__PRECEDENCE__SAME_PRECEDENCE)
            else:
                return self._precedence_description_w_list()

    def evaluation_description(self) -> List[ParagraphItem]:
        op_eval_lay_l_to_r = [
            operator.name
            for operator in self.infix_operators__list
            if operator.value.description().operand_evaluation__lazy__left_to_right
        ]

        if not op_eval_lay_l_to_r:
            return []

        operators_header = ', '.join(op_eval_lay_l_to_r)
        list_item = docs.simple_list(
            [lists.HeaderContentListItem(docs.text(operators_header),
                                         self._tp.fnap(_OPERANDS__LAZY__LEFT_TO_RIGHT))],
            lists.ListType.VARIABLE_LIST,
        )
        return [list_item]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        expression_lists = [
            self.grammar.primitives__seq,
            self.grammar.prefix_operators__seq,
            self.infix_operators__list,
        ]
        return list(itertools.chain.from_iterable(
            map(_seds_for_expr, expression_lists)
        ))

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        """
        :returns: A new list, which may contain duplicate elements.
        """
        expression_dicts = [
            self.grammar.primitives,
            self.grammar.prefix_operators,
            name_and_value.to_dict(self.infix_operators__list),
        ]
        return list(itertools.chain.from_iterable(
            map(_see_also_targets_for_expr,
                expression_dicts)
        ))

    def _precedence_description_w_list(self) -> List[ParagraphItem]:
        levels_navs = [self.grammar.prefix_operators__seq]
        levels_navs += reversed(self.grammar.infix_ops_inc_precedence__seq)

        levels_list = docs.simple_header_only_list([
            ', '.join(map(NameAndValue.name.fget, level_navs))
            for level_navs in levels_navs
        ],
            lists.ListType.ORDERED_LIST,
        )
        return [levels_list]

    def _invokation_variants_primitive(self) -> List[InvokationVariant]:
        def invokation_variant_of(name: str,
                                  syntax: PrimitiveDescription) -> InvokationVariant:
            all_arguments = [syntax.initial_argument(name)] + list(syntax.argument_usage_list)
            return invokation_variant_from_args(all_arguments,
                                                syntax.description_rest)

        return [
            invokation_variant_of(expr.name, expr.value.syntax)
            for expr in self.grammar.primitives__seq
        ]

    def _invokation_variants_symbol_ref(self) -> List[InvokationVariant]:
        def invokation_variant(syntax_element: SyntaxElementInfo,
                               description: Sequence[ParagraphItem]) -> InvokationVariant:
            return invokation_variant_from_args([
                a.Single(a.Multiplicity.MANDATORY,
                         syntax_element.argument)
            ],
                description
            )

        description_of_sym_ref = self._symbol_ref_description()
        description_of_sym_name = description_of_sym_ref + self._symbol_name_additional_description()

        return [
            invokation_variant(syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT,
                               description_of_sym_ref,
                               ),
            invokation_variant(syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT,
                               description_of_sym_name,
                               ),
        ]

    def _invokation_variants_infix(self) -> List[InvokationVariant]:
        def invokation_variant_of(operator_name: str,
                                  syntax: OperatorDescription) -> InvokationVariant:
            operator_argument = a.Single(a.Multiplicity.MANDATORY,
                                         a.Constant(operator_name))
            all_arguments = [self.concept_argument, operator_argument, self.concept_argument]
            return invokation_variant_from_args(all_arguments,
                                                syntax.description_rest)

        return [
            invokation_variant_of(expr.name, expr.value.syntax)
            for expr in itertools.chain.from_iterable(self.grammar.infix_ops_inc_precedence__seq)
        ]

    def _invokation_variants_prefix(self) -> List[InvokationVariant]:
        def invokation_variant_of(operator_name: str,
                                  syntax: OperatorDescription) -> InvokationVariant:
            operator_argument = a.Single(a.Multiplicity.MANDATORY,
                                         a.Constant(operator_name))
            all_arguments = [operator_argument, self.concept_argument]
            return invokation_variant_from_args(all_arguments,
                                                syntax.description_rest)

        return [
            invokation_variant_of(expr.name, expr.value.syntax)
            for expr in self.grammar.prefix_operators__seq
        ]

    def _invokation_variants_parentheses(self) -> List[InvokationVariant]:
        arguments = [
            a.Single(a.Multiplicity.MANDATORY,
                     a.Constant('(')),
            self.concept_argument,
            a.Single(a.Multiplicity.MANDATORY,
                     a.Constant(')')),
        ]
        iv = invokation_variant_from_args(arguments)
        return [iv]

    def _symbol_ref_description(self) -> List[ParagraphItem]:
        return self._tp.fnap(_SYMBOL_REF_DESCRIPTION)

    def _symbol_name_additional_description(self) -> List[ParagraphItem]:
        return self._tp.fnap(_SYMBOL_NAME_ADDITIONAL_DESCRIPTION)


def _see_also_targets_for_expr(expressions_dict: dict) -> List[SeeAlsoTarget]:
    from_expressions = list(itertools.chain.from_iterable(
        map(lambda expr: expr.syntax.see_also_targets,
            expressions_dict.values())))

    always = [
        syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.cross_reference_target,
        syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT.cross_reference_target,
    ]

    return from_expressions + always


def _seds_for_expr(expressions: List[NameAndValue[ElementWithDescription]]) -> List[SyntaxElementDescription]:
    return list(itertools.chain.from_iterable([
        expr.value.description().syntax_elements
        for expr in expressions
    ]))


_SYMBOL_REF_DESCRIPTION = """\
Reference to {symbol_concept:a},
that must have been defined as {concept_name:a}.
"""

_SYMBOL_NAME_ADDITIONAL_DESCRIPTION = """\
An unquoted {string_type} that is not a reserved word
is interpreted as the name of {symbol_concept:a}.
"""

_BIN_OP_PRECEDENCE = 'All binary operators have the same precedence.'

_DESCRIPTION__PRECEDENCE__ONLY_BINARY = """\
{BIN_OP_PRECEDENCE}
"""

_DESCRIPTION__PRECEDENCE__PREFIX_AND_BINARY = """\
Prefix operators have the highest precedence.

{BIN_OP_PRECEDENCE}
"""

_DESCRIPTION__PRECEDENCE__SAME_PRECEDENCE = """\
All operators have the same precedence.
"""

_DESCRIPTION__SYNTAX__W_OPERATORS = """\
Operators and parentheses must be separated by {whitespace}.
"""

_DESCRIPTION__SYNTAX__WO_OPERATORS = """\
Parentheses must be separated by {whitespace}.
"""

_OPERANDS__LAZY__LEFT_TO_RIGHT = """\
Operands are evaluated lazily, from left to right.
"""
