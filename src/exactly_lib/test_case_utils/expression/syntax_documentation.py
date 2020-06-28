import itertools
from typing import List, Sequence

from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, InvokationVariant, \
    cli_argument_syntax_element_description, invokation_variant_from_args
from exactly_lib.definitions import formatting
from exactly_lib.definitions.entity import syntax_elements, concepts
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser
from .grammar import Grammar, PrimitiveExpressionDescription, OperatorExpressionDescription, ExpressionWithDescription
from ...definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from ...definitions.entity.syntax_elements import SyntaxElementInfo
from ...util.name_and_value import NameAndValue


def syntax_element_description(grammar: Grammar) -> SyntaxElementDescription:
    return Syntax(grammar).syntax_element_description()


class Syntax:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.concept_argument = a.Single(a.Multiplicity.MANDATORY,
                                         self.grammar.concept.syntax_element)

        self._tp = TextParser({
            'symbol_concept': formatting.concept_name_with_formatting(concepts.SYMBOL_CONCEPT_INFO.name),
            'concept_name': self.grammar.concept.name,
            'BIN_OP_PRECEDENCE': _BIN_OP_PRECEDENCE,
        })

    def syntax_element_description(self) -> SyntaxElementDescription:
        return cli_argument_syntax_element_description(
            self.grammar.concept.syntax_element,
            [],
            self.invokation_variants()
        )

    def invokation_variants(self) -> List[InvokationVariant]:
        return (self._invokation_variants_simple() +
                self._invokation_variants_prefix() +
                self._invokation_variants_complex() +
                self._invokation_variants_symbol_ref() +
                self._invokation_variants_parentheses()
                )

    def global_description(self) -> List[ParagraphItem]:
        ret_val = self._precedence_description()
        ret_val += self._tp.fnap(_DESCRIPTION__SYNTAX)
        return ret_val

    def _precedence_description(self) -> List[ParagraphItem]:
        has_prefix_op = bool(self.grammar.prefix_op_expressions)
        has_bin_op = bool(self.grammar.infix_op_expressions)

        if has_bin_op:
            if has_prefix_op:
                return self._tp.fnap(_DESCRIPTION__PRECEDENCE__PREFIX_AND_BINARY)
            else:
                return self._tp.fnap(_DESCRIPTION__PRECEDENCE__ONLY_BINARY)
        else:
            return []

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        expression_lists = [
            self.grammar.primitive_expressions_list,
            self.grammar.prefix_op_expressions_list,
            self.grammar.infix_op_expressions_list,
        ]
        return list(itertools.chain.from_iterable(
            map(_seds_for_expr, expression_lists)
        ))

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        """
        :returns: A new list, which may contain duplicate elements.
        """
        expression_dicts = [
            self.grammar.primitive_expressions,
            self.grammar.prefix_op_expressions,
            self.grammar.infix_op_expressions,
        ]
        return list(itertools.chain.from_iterable(
            map(_see_also_targets_for_expr,
                expression_dicts)
        ))

    def _invokation_variants_simple(self) -> List[InvokationVariant]:
        def invokation_variant_of(name: str,
                                  syntax: PrimitiveExpressionDescription) -> InvokationVariant:
            all_arguments = [syntax.initial_argument(name)] + list(syntax.argument_usage_list)
            return invokation_variant_from_args(all_arguments,
                                                syntax.description_rest)

        return [
            invokation_variant_of(expr.name, expr.value.syntax)
            for expr in self.grammar.primitive_expressions_list
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

    def _invokation_variants_complex(self) -> List[InvokationVariant]:
        def invokation_variant_of(operator_name: str,
                                  syntax: OperatorExpressionDescription) -> InvokationVariant:
            operator_argument = a.Single(a.Multiplicity.MANDATORY,
                                         a.Constant(operator_name))
            all_arguments = [self.concept_argument, operator_argument, self.concept_argument]
            return invokation_variant_from_args(all_arguments,
                                                syntax.description_rest)

        return [
            invokation_variant_of(expr.name, expr.value.syntax)
            for expr in self.grammar.infix_op_expressions_list
        ]

    def _invokation_variants_prefix(self) -> List[InvokationVariant]:
        def invokation_variant_of(operator_name: str,
                                  syntax: OperatorExpressionDescription) -> InvokationVariant:
            operator_argument = a.Single(a.Multiplicity.MANDATORY,
                                         a.Constant(operator_name))
            all_arguments = [operator_argument, self.concept_argument]
            return invokation_variant_from_args(all_arguments,
                                                syntax.description_rest)

        return [
            invokation_variant_of(expr.name, expr.value.syntax)
            for expr in self.grammar.prefix_op_expressions_list
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


def _seds_for_expr(expressions: List[NameAndValue[ExpressionWithDescription]]) -> List[SyntaxElementDescription]:
    return list(itertools.chain.from_iterable([
        expr.value.description().syntax_elements
        for expr in expressions
    ]))


_SYMBOL_REF_DESCRIPTION = """\
Reference to {symbol_concept:a},
that must have been defined as {concept_name:a}.
"""

_SYMBOL_NAME_ADDITIONAL_DESCRIPTION = """\
A string that is not the name of {concept_name:a}
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

_DESCRIPTION__SYNTAX = """\
Operators and parentheses must be separated by whitespace.
"""
