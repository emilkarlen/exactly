from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations import token_stream_parse_prime
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import TokenParserPrime
from exactly_lib.test_case_utils.parse import symbol_syntax
from .grammar import Grammar


def parse_from_parse_source(grammar: Grammar,
                            source: ParseSource):
    with token_stream_parse_prime.from_parse_source(source) as tp:
        return parse(grammar, tp)


def parse(grammar: Grammar,
          parser: TokenParserPrime):
    return _Parser(grammar, parser).parse()


class _Parser:
    def __init__(self,
                 grammar: Grammar,
                 parser: TokenParserPrime):
        self.parser = parser
        self.grammar = grammar
        self.complex_expressions_keys = self.grammar.complex_expressions.keys()
        self.prefix_expressions_keys = self.grammar.prefix_expressions.keys()
        self.missing_expression = 'Missing ' + self.grammar.concept.syntax_element.name

    def parse(self):
        if not self.grammar.complex_expressions:
            return self.parse_mandatory_simple()
        else:
            return self.parse_with_complex_expressions()

    def parse_with_complex_expressions(self):
        expression = self.parse_mandatory_simple()

        complex_operator_name = self.parse_optional_complex_operator_name()

        while complex_operator_name:
            expression = self.complex_operator_sequence_for_single_operator(complex_operator_name, expression)
            complex_operator_name = self.parse_optional_complex_operator_name()

        return expression

    def parse_optional_complex_operator_name(self) -> str:
        return self.parser.consume_optional_constant_string_that_must_be_unquoted_and_equal(
            self.complex_expressions_keys)

    def complex_operator_sequence_for_single_operator(self,
                                                      complex_operator_name: str,
                                                      first_expression):
        single_accepted_operator = [complex_operator_name]

        expressions = [first_expression]

        def parse_mandatory_simple_and_append():
            next_expression = self.parse_mandatory_simple()
            expressions.append(next_expression)

        parse_mandatory_simple_and_append()
        while self.parser.consume_optional_constant_string_that_must_be_unquoted_and_equal(single_accepted_operator):
            parse_mandatory_simple_and_append()

        return self.grammar.complex_expressions[complex_operator_name].mk_complex(expressions)

    def parse_mandatory_simple(self):
        self.parser.require_is_not_at_eol(self.missing_expression)

        if self.consume_optional_start_parentheses():
            expression = self.parse()
            self.consume_mandatory_end_parentheses()
            return expression
        else:
            mk_prefix_expr = self.consume_optional_prefix_operator()
            if mk_prefix_expr:
                expression = self.parse_mandatory_simple()
                return mk_prefix_expr(expression)
            else:
                return self.parser.parse_mandatory_string_that_must_be_unquoted(self.grammar.concept.name.singular,
                                                                                self.parse_simple,
                                                                                must_be_on_current_line=True)

    def parse_simple(self, selector_name: str):
        if selector_name in self.grammar.simple_expressions:
            return self.grammar.simple_expressions[selector_name].parse_arguments(self.parser)
        elif not symbol_syntax.is_symbol_name(selector_name):
            err_msg = symbol_syntax.invalid_symbol_name_error(selector_name)
            raise SingleInstructionInvalidArgumentException(err_msg)
        else:
            return self.grammar.mk_reference(selector_name)

    def consume_optional_prefix_operator(self):
        prefix_operator_name = self.parser.consume_optional_constant_string_that_must_be_unquoted_and_equal(
            self.prefix_expressions_keys)
        if prefix_operator_name:
            self.parser.require_is_not_at_eol(self.missing_expression + ' after ' + prefix_operator_name)
            return self.grammar.prefix_expressions[prefix_operator_name].mk_expression
        else:
            return None

    def consume_optional_start_parentheses(self) -> bool:
        start_parenthesis = self.parser.consume_optional_constant_string_that_must_be_unquoted_and_equal(['('])
        if start_parenthesis:
            self.parser.require_is_not_at_eol(self.missing_expression + ' after ' + start_parenthesis)
        return start_parenthesis is not None

    def consume_mandatory_end_parentheses(self):
        self.parser.require_is_not_at_eol('Missing )')
        self.parser.consume_mandatory_constant_string_that_must_be_unquoted_and_equal([')'],
                                                                                      _do_nothing,
                                                                                      'Expression inside ( )')


def _do_nothing(*arg, **kwargs):
    return None
