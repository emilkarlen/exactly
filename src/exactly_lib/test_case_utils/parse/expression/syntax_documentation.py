from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, InvokationVariant
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.type_system import syntax_of_type_name_in_text
from exactly_lib.test_case_utils.parse import symbol_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.parse import normalize_and_parse
from .grammar import Grammar, SimpleExpressionDescription, OperatorExpressionDescription


def syntax_element_description(grammar: Grammar) -> SyntaxElementDescription:
    return Syntax(grammar).syntax_element_description()


class Syntax:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.concept_argument = a.Single(a.Multiplicity.MANDATORY,
                                         self.grammar.concept.syntax_element)

    def syntax_element_description(self) -> SyntaxElementDescription:
        return cl_syntax.cli_argument_syntax_element_description(
            self.grammar.concept.syntax_element,
            [],
            self.invokation_variants()
        )

    def invokation_variants(self) -> list:
        return (self.invokation_variants_simple() +
                self.invokation_variants_symbol_ref() +
                self.invokation_variants_complex() +
                self.invokation_variants_parentheses()
                )

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
                                   a.Named(symbol_syntax.SYMBOL_SYNTAX_ELEMENT_NAME))
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

    def invokation_variants_parentheses(self) -> list:
        arguments = [
            a.Single(a.Multiplicity.MANDATORY,
                     a.Constant('(')),
            self.concept_argument,
            a.Single(a.Multiplicity.MANDATORY,
                     a.Constant(')')),
        ]
        iv = InvokationVariant(cl_syntax.cl_syntax_for_args(arguments),
                               [])
        return [iv]

    def _symbol_ref_description(self):
        return normalize_and_parse(
            _SYMBOL_REF_DESCRIPTION.format(
                concept_name=self.grammar.concept.name.singular,
                concept_type_name=syntax_of_type_name_in_text(self.grammar.concept.type_system_type_name),

            ))


_SYMBOL_REF_DESCRIPTION = """\
Reference to a {concept_name} symbol,
that must be defined as a {concept_type_name}.
"""
