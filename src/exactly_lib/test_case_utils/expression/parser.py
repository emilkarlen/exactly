from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol import symbol_syntax
from .grammar import Grammar


def parse_from_parse_source(grammar: Grammar,
                            source: ParseSource):
    with token_stream_parser.from_parse_source(source) as tp:
        return parse(grammar, tp)


def parse(grammar: Grammar,
          parser: TokenParser):
    return _Parser(grammar, parser).parse(must_be_on_current_line=True)


class _Parser:
    def __init__(self,
                 grammar: Grammar,
                 parser: TokenParser):
        self.parser = parser
        self.grammar = grammar
        self.complex_expressions_keys = self.grammar.complex_expressions.keys()
        self.prefix_expressions_keys = self.grammar.prefix_expressions.keys()
        self.missing_expression = 'Missing ' + self.grammar.concept.syntax_element.name

    def parse(self, must_be_on_current_line: bool):
        if not self.grammar.complex_expressions:
            return self.parse_mandatory_simple(must_be_on_current_line=must_be_on_current_line)
        else:
            return self.parse_with_complex_expressions(must_be_on_current_line=must_be_on_current_line)

    def parse_with_complex_expressions(self, must_be_on_current_line: bool = True):
        expression = self.parse_mandatory_simple(must_be_on_current_line)

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
            next_expression = self.parse_mandatory_simple(must_be_on_current_line=False)
            expressions.append(next_expression)

        parse_mandatory_simple_and_append()
        while self.parser.consume_optional_constant_string_that_must_be_unquoted_and_equal(single_accepted_operator):
            parse_mandatory_simple_and_append()

        return self.grammar.complex_expressions[complex_operator_name].mk_complex(expressions)

    def parse_mandatory_simple(self, must_be_on_current_line: bool = True):
        if must_be_on_current_line:
            self.parser.require_is_not_at_eol(self.missing_expression)

        if self.consume_optional_start_parentheses():
            expression = self.parse(must_be_on_current_line=False)
            self.consume_mandatory_end_parentheses()
            return expression
        else:
            mk_prefix_expr = self.consume_optional_prefix_operator()
            if mk_prefix_expr:
                expression = self.parse_mandatory_simple(must_be_on_current_line=True)
                return mk_prefix_expr(expression)
            else:
                return self.parser.parse_mandatory_string_that_must_be_unquoted(
                    self.grammar.concept.name.singular,
                    self.parse_simple,
                    must_be_on_current_line=must_be_on_current_line)

    def parse_simple(self, simple_name: str):
        if simple_name in self.grammar.simple_expressions:
            return self.grammar.simple_expressions[simple_name].parse_arguments(self.parser)
        elif not symbol_syntax.is_symbol_name(simple_name):
            err_msg = symbol_syntax.invalid_symbol_name_error(simple_name)
            raise SingleInstructionInvalidArgumentException(err_msg)
        else:
            return self.grammar.mk_reference(simple_name)

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
        return start_parenthesis is not None

    def consume_mandatory_end_parentheses(self):
        self.parser.consume_mandatory_constant_string_that_must_be_unquoted_and_equal([')'],
                                                                                      lambda x: None,
                                                                                      'Expression inside ( )')
