from exactly_lib.named_element.resolver_structure import NamedElementResolver
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils import token_stream_parse_prime
from exactly_lib.test_case_utils.parse import symbol_syntax
from exactly_lib.test_case_utils.token_stream_parse_prime import TokenParserPrime
from .grammar import Grammar


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
