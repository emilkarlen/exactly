import itertools
from typing import List, Sequence

from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, InvokationVariant, \
    cli_argument_syntax_element_description
from exactly_lib.definitions import formatting
from exactly_lib.definitions.argument_rendering import cl_syntax
from exactly_lib.definitions.entity import syntax_elements, concepts
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser
from .grammar import Grammar, SimpleExpressionDescription, OperatorExpressionDescription
from ...definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from ...definitions.entity.syntax_elements import SyntaxElementInfo


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
        })

    def syntax_element_description(self) -> SyntaxElementDescription:
        return cli_argument_syntax_element_description(
            self.grammar.concept.syntax_element,
            [],
            self.invokation_variants()
        )

    def invokation_variants(self) -> list:
        return (self.invokation_variants_simple() +
                self.invokation_variants_prefix() +
                self.invokation_variants_complex() +
                self.invokation_variants_symbol_ref() +
                self.invokation_variants_parentheses()
                )

    def global_description(self) -> List[ParagraphItem]:
        return self._tp.fnap(_GLOBAL_DESCRIPTION)

    def invokation_variants_simple(self) -> List[InvokationVariant]:
        def invokation_variant_of(name: str,
                                  syntax: SimpleExpressionDescription) -> InvokationVariant:
            name_argument = a.Single(a.Multiplicity.MANDATORY,
                                     a.Constant(name))
            all_arguments = [name_argument] + list(syntax.argument_usage_list)
            return InvokationVariant(cl_syntax.cl_syntax_for_args(all_arguments),
                                     syntax.description_rest)

        return [
            invokation_variant_of(expr.name, expr.value.syntax)
            for expr in self.grammar.simple_expressions_list
        ]

    def invokation_variants_symbol_ref(self) -> List[InvokationVariant]:
        def invokation_variant(syntax_element: SyntaxElementInfo,
                               description: Sequence[ParagraphItem]) -> InvokationVariant:
            return InvokationVariant(cl_syntax.cl_syntax_for_args([
                a.Single(a.Multiplicity.MANDATORY,
                         syntax_element.argument)
            ]),
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

    def invokation_variants_complex(self) -> List[InvokationVariant]:
        def invokation_variant_of(operator_name: str,
                                  syntax: OperatorExpressionDescription) -> InvokationVariant:
            operator_argument = a.Single(a.Multiplicity.MANDATORY,
                                         a.Constant(operator_name))
            all_arguments = [self.concept_argument, operator_argument, self.concept_argument]
            return InvokationVariant(cl_syntax.cl_syntax_for_args(all_arguments),
                                     syntax.description_rest)

        return [
            invokation_variant_of(expr.name, expr.value.syntax)
            for expr in self.grammar.complex_expressions_list
        ]

    def invokation_variants_prefix(self) -> List[InvokationVariant]:
        def invokation_variant_of(operator_name: str,
                                  syntax: OperatorExpressionDescription) -> InvokationVariant:
            operator_argument = a.Single(a.Multiplicity.MANDATORY,
                                         a.Constant(operator_name))
            all_arguments = [operator_argument, self.concept_argument]
            return InvokationVariant(cl_syntax.cl_syntax_for_args(all_arguments),
                                     syntax.description_rest)

        return [
            invokation_variant_of(expr.name, expr.value.syntax)
            for expr in self.grammar.prefix_expressions_list
        ]

    def invokation_variants_parentheses(self) -> List[InvokationVariant]:
        arguments = [
            a.Single(a.Multiplicity.MANDATORY,
                     a.Constant('(')),
            self.concept_argument,
            a.Single(a.Multiplicity.MANDATORY,
                     a.Constant(')')),
        ]
        iv = InvokationVariant(cl_syntax.cl_syntax_for_args(arguments))
        return [iv]

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        """
        :returns: A new list, which may contain duplicate elements.
        """
        expression_dicts = [
            self.grammar.simple_expressions,
            self.grammar.prefix_expressions,
            self.grammar.complex_expressions,
        ]
        return list(itertools.chain.from_iterable(
            map(_see_also_targets_for_expr,
                expression_dicts)
        ))

    def _symbol_ref_description(self) -> List[ParagraphItem]:
        return self._tp.fnap(_SYMBOL_REF_DESCRIPTION)

    def _symbol_name_additional_description(self) -> List[ParagraphItem]:
        return self._tp.fnap(_SYMBOL_NAME_ADDITIONAL_DESCRIPTION)


def _see_also_targets_for_expr(expressions_dict: dict) -> iter:
    from_expressions = list(itertools.chain.from_iterable(
        map(lambda expr: expr.syntax.see_also_targets,
            expressions_dict.values())))

    always = [
        syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.cross_reference_target,
        syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT.cross_reference_target,
    ]

    return from_expressions + always


_SYMBOL_REF_DESCRIPTION = """\
Reference to {symbol_concept:a},
that must have been defined as {concept_name:a}.
"""

_SYMBOL_NAME_ADDITIONAL_DESCRIPTION = """\
A string that is not the name of {concept_name:a}
is interpreted as the name of {symbol_concept:a}.
"""

_GLOBAL_DESCRIPTION = """\
All operators have the same precedence.


Operators and parentheses must be separated by whitespace.
"""
