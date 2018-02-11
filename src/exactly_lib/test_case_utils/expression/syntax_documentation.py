import itertools

from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, InvokationVariant, \
    cli_argument_syntax_element_description
from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.entity.concepts import SYMBOL_CONCEPT_INFO
from exactly_lib.help_texts.entity.syntax_elements import SYMBOL_NAME_SYNTAX_ELEMENT
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.textformat_parser import TextParser
from .grammar import Grammar, SimpleExpressionDescription, OperatorExpressionDescription


def syntax_element_description(grammar: Grammar) -> SyntaxElementDescription:
    return Syntax(grammar).syntax_element_description()


class Syntax:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.concept_argument = a.Single(a.Multiplicity.MANDATORY,
                                         self.grammar.concept.syntax_element)

        self._tp = TextParser({
            'symbol_concept': formatting.concept_(SYMBOL_CONCEPT_INFO),
            'concept_name': self.grammar.concept.name.singular,
        })

    def syntax_element_description(self) -> SyntaxElementDescription:
        return cli_argument_syntax_element_description(
            self.grammar.concept.syntax_element,
            [],
            self.invokation_variants()
        )

    def invokation_variants(self) -> list:
        return (self.invokation_variants_simple() +
                self.invokation_variants_symbol_ref() +
                self.invokation_variants_prefix() +
                self.invokation_variants_complex() +
                self.invokation_variants_parentheses()
                )

    def global_description(self) -> list:
        return self._tp.fnap(_GLOBAL_DESCRIPTION)

    def invokation_variants_simple(self) -> list:
        def invokation_variant_of(name: str,
                                  syntax: SimpleExpressionDescription) -> InvokationVariant:
            name_argument = a.Single(a.Multiplicity.MANDATORY,
                                     a.Constant(name))
            all_arguments = [name_argument] + syntax.argument_usage_list
            return InvokationVariant(cl_syntax.cl_syntax_for_args(all_arguments),
                                     syntax.description_rest)

        return [
            invokation_variant_of(name, self.grammar.simple_expressions[name].syntax)
            for name in sorted(self.grammar.simple_expressions.keys())
        ]

    def invokation_variants_symbol_ref(self) -> list:
        symbol_argument = a.Single(a.Multiplicity.MANDATORY,
                                   SYMBOL_NAME_SYNTAX_ELEMENT.argument)
        iv = InvokationVariant(cl_syntax.cl_syntax_for_args([symbol_argument]),
                               self._symbol_ref_description())
        return [iv]

    def invokation_variants_complex(self) -> list:
        def invokation_variant_of(operator_name: str,
                                  syntax: OperatorExpressionDescription) -> InvokationVariant:
            operator_argument = a.Single(a.Multiplicity.MANDATORY,
                                         a.Constant(operator_name))
            all_arguments = [self.concept_argument, operator_argument, self.concept_argument]
            return InvokationVariant(cl_syntax.cl_syntax_for_args(all_arguments),
                                     syntax.description_rest)

        return [
            invokation_variant_of(name, self.grammar.complex_expressions[name].syntax)
            for name in sorted(self.grammar.complex_expressions.keys())
        ]

    def invokation_variants_prefix(self) -> list:
        def invokation_variant_of(operator_name: str,
                                  syntax: OperatorExpressionDescription) -> InvokationVariant:
            operator_argument = a.Single(a.Multiplicity.MANDATORY,
                                         a.Constant(operator_name))
            all_arguments = [operator_argument, self.concept_argument]
            return InvokationVariant(cl_syntax.cl_syntax_for_args(all_arguments),
                                     syntax.description_rest)

        return [
            invokation_variant_of(name, self.grammar.prefix_expressions[name].syntax)
            for name in sorted(self.grammar.prefix_expressions.keys())
        ]

    def invokation_variants_parentheses(self) -> list:
        arguments = [
            a.Single(a.Multiplicity.MANDATORY,
                     a.Constant('(')),
            self.concept_argument,
            a.Single(a.Multiplicity.MANDATORY,
                     a.Constant(')')),
        ]
        iv = InvokationVariant(cl_syntax.cl_syntax_for_args(arguments))
        return [iv]

    def see_also_targets(self) -> list:
        """
        :returns: A new list of :class:`SeeAlsoTarget`, which may contain duplicate elements.
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

    def _symbol_ref_description(self):
        return self._tp.fnap(_SYMBOL_REF_DESCRIPTION)


def _see_also_targets_for_expr(expressions_dict: dict) -> iter:
    from_expressions = list(itertools.chain.from_iterable(
        map(lambda expr: expr.syntax.see_also_targets,
            expressions_dict.values())))

    always = [SYMBOL_NAME_SYNTAX_ELEMENT.cross_reference_target]

    return from_expressions + always


_SYMBOL_REF_DESCRIPTION = """\
Reference to a {symbol_concept},
that must have been defined as a {concept_name}.
"""

_GLOBAL_DESCRIPTION = """\
All operators have the same precedence.


Operators and parentheses must be separated by whitespace.
"""
