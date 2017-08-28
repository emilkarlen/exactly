from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, InvokationVariant
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.name_and_cross_ref import Name
from exactly_lib.help_texts.test_case.instructions.assign_symbol import syntax_of_type_name_in_text
from exactly_lib.named_element.resolver_structure import NamedElementResolver
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils import token_stream_parse_prime
from exactly_lib.test_case_utils.parse import symbol_syntax
from exactly_lib.test_case_utils.token_stream_parse_prime import TokenParserPrime
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.parse import normalize_and_parse


class SimpleExpressionDescription:
    def __init__(self,
                 argument_usage_list: list,
                 description_rest: list):
        self.argument_usage_list = argument_usage_list
        self.description_rest = description_rest


class SimpleExpression:
    def __init__(self,
                 parse_arguments,
                 syntax: SimpleExpressionDescription):
        """
        :param parse_arguments: TokenParserPrime -> NamedElementResolver
        """
        self.parse_arguments = parse_arguments
        self.syntax = syntax


class ComplexExpressionDescription:
    def __init__(self,
                 description_rest: list):
        self.description_rest = description_rest


class ComplexExpression:
    def __init__(self,
                 mk_complex,
                 syntax: ComplexExpressionDescription):
        """
        :param mk_complex: [NamedElementResolver] -> NamedElementResolver
        """
        self.mk_complex = mk_complex
        self.syntax = syntax


class Concept:
    def __init__(self,
                 name: Name,
                 type_system_type_name: str,
                 syntax_element_name: a.Named):
        self.type_system_type_name = type_system_type_name
        self.name = name
        self.syntax_element = syntax_element_name


class Grammar:
    def __init__(self,
                 concept: Concept,
                 mk_reference,
                 simple_expressions: dict,
                 complex_expressions: dict):
        """
        :param mk_reference: str -> NamedElementResolver
        :param simple_expressions: dict str -> :class:`SimpleExpression`
        """
        self.concept = concept
        self.mk_reference = mk_reference
        self.simple_expressions = simple_expressions
        self.complex_expressions = complex_expressions


class Syntax:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar

    def syntax_element_description(self) -> SyntaxElementDescription:
        return cl_syntax.cli_argument_syntax_element_description(
            self.grammar.concept.syntax_element,
            [],
            self.invokation_variants()
        )

    def invokation_variants(self) -> list:
        return (self.invokation_variants_simple() +
                self.invokation_variants_symbol_ref() +
                self.invokation_variants_complex())

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
        operand_argument = a.Single(a.Multiplicity.MANDATORY,
                                    self.grammar.concept.syntax_element)

        def invokation_variant_of(operator_name: str,
                                  syntax: ComplexExpressionDescription) -> InvokationVariant:
            operator_argument = a.Single(a.Multiplicity.MANDATORY,
                                         a.Constant(operator_name))
            all_arguments = [operand_argument, operator_argument, operand_argument]
            return InvokationVariant(cl_syntax.cl_syntax_for_args(all_arguments),
                                     syntax.description_rest)

        return [
            invokation_variant_of(name, self.grammar.complex_expressions[name].syntax)
            for name in sorted(self.grammar.complex_expressions.keys())
        ]

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


def parse_from_parse_source(grammar: Grammar,
                            source: ParseSource) -> NamedElementResolver:
    with token_stream_parse_prime.from_parse_source(source) as tp:
        return parse(grammar, tp)


def parse(grammar: Grammar,
          parser: TokenParserPrime) -> NamedElementResolver:
    return _Parser(grammar, parser).parse()


class _Parser:
    def __init__(self,
                 grammar: Grammar,
                 parser: TokenParserPrime):
        self.parser = parser
        self.grammar = grammar
        self.complex_expressions_keys = self.grammar.complex_expressions.keys()

    def parse(self) -> NamedElementResolver:
        if not self.grammar.complex_expressions:
            return self.parse_mandatory_simple()
        else:
            return self.parse_with_complex_expressions()

    def parse_with_complex_expressions(self) -> NamedElementResolver:
        expression = self.parse_mandatory_simple()

        complex_operator_name = self.parse_optional_complex_operator_name()

        while complex_operator_name:
            expression = self.complex_operator_sequence_for_single_operator(complex_operator_name, expression)
            complex_operator_name = self.parse_optional_complex_operator_name()

        return expression

    def parse_optional_complex_operator_name(self):
        return self.parser.consume_optional_constant_string_that_must_be_unquoted_and_equal(
            self.complex_expressions_keys)

    def complex_operator_sequence_for_single_operator(self,
                                                      complex_operator_name: str,
                                                      first_expression: NamedElementResolver) -> NamedElementResolver:
        single_accepted_operator = [complex_operator_name]

        expressions = [first_expression]

        def parse_mandatory_simple_and_append():
            next_expression = self.parse_mandatory_simple()
            expressions.append(next_expression)

        parse_mandatory_simple_and_append()
        while self.parser.consume_optional_constant_string_that_must_be_unquoted_and_equal(single_accepted_operator):
            parse_mandatory_simple_and_append()

        return self.grammar.complex_expressions[complex_operator_name].mk_complex(expressions)

    def parse_mandatory_simple(self) -> NamedElementResolver:
        return self.parser.parse_mandatory_string_that_must_be_unquoted(self.grammar.concept.name.singular,
                                                                        self.parse_simple,
                                                                        must_be_on_current_line=True)

    def parse_simple(self, selector_name: str) -> NamedElementResolver:
        if selector_name in self.grammar.simple_expressions:
            return self.grammar.simple_expressions[selector_name].parse_arguments(self.parser)
        elif not symbol_syntax.is_symbol_name(selector_name):
            err_msg = symbol_syntax.invalid_symbol_name_error(selector_name)
            raise SingleInstructionInvalidArgumentException(err_msg)
        else:
            return self.grammar.mk_reference(selector_name)
