from typing import Generic, Optional, Callable

from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol import symbol_syntax
from .grammar import Grammar, EXPR
from ...util.cli_syntax import option_syntax


def parse_from_parse_source(grammar: Grammar[EXPR],
                            source: ParseSource,
                            must_be_on_current_line: bool = True) -> EXPR:
    with token_stream_parser.from_parse_source(source) as tp:
        return parse(grammar, tp, must_be_on_current_line)


def parse(grammar: Grammar[EXPR],
          parser: TokenParser,
          must_be_on_current_line: bool = True) -> EXPR:
    return _Parser(grammar, parser).parse(None if must_be_on_current_line else _NEXT_EXPR_ON_ANY_LINE)


_IS_INSIDE_PARENTHESIS = 1
_NEXT_EXPR_ON_ANY_LINE = 2


class _Parser(Generic[EXPR]):
    def __init__(self,
                 grammar: Grammar[EXPR],
                 parser: TokenParser,
                 ):
        self.parser = parser
        self.grammar = grammar
        self.infix_op_expressions_keys = self.grammar.infix_op_expressions.keys()
        self.prefix_op_expressions_keys = self.grammar.prefix_op_expressions.keys()
        self.missing_expression = 'Missing ' + self.grammar.concept.syntax_element.name

    def parse(self, new_line_ignore: Optional[int]) -> EXPR:
        if not self.grammar.infix_op_expressions:
            return self.parse_mandatory_primitive(new_line_ignore is None)
        else:
            return self.parse_with_infix_op_expressions(new_line_ignore)

    def parse_with_infix_op_expressions(self, new_line_ignore: Optional[int]) -> EXPR:
        expression = self.parse_mandatory_primitive(new_line_ignore is None)

        if new_line_ignore is _NEXT_EXPR_ON_ANY_LINE:
            new_line_ignore = None

        infix_operator_name = self.parse_optional_infix_operator_name(new_line_ignore is None)

        while infix_operator_name:
            expression = self.infix_operator_sequence_for_single_operator(
                infix_operator_name,
                expression,
                is_inside_parens=new_line_ignore is _IS_INSIDE_PARENTHESIS
            )
            infix_operator_name = self.parse_optional_infix_operator_name(new_line_ignore is None)

        return expression

    def parse_optional_infix_operator_name(self, must_be_on_current_line: bool) -> str:
        return self.parser.consume_optional_constant_string_that_must_be_unquoted_and_equal(
            self.infix_op_expressions_keys,
            must_be_on_current_line,
        )

    def infix_operator_sequence_for_single_operator(self,
                                                    infix_operator_name: str,
                                                    first_expression: EXPR,
                                                    is_inside_parens: bool) -> EXPR:
        single_accepted_operator = [infix_operator_name]

        expressions = [first_expression]

        def parse_mandatory_primitive_and_append():
            next_expression = self.parse_mandatory_primitive(must_be_on_current_line=False)
            expressions.append(next_expression)

        parse_mandatory_primitive_and_append()
        while self.parser.consume_optional_constant_string_that_must_be_unquoted_and_equal(
                single_accepted_operator,
                must_be_on_current_line=not is_inside_parens):
            parse_mandatory_primitive_and_append()

        return self.grammar.infix_op_expressions[infix_operator_name].mk_complex(expressions)

    def parse_mandatory_primitive(self, must_be_on_current_line: bool) -> EXPR:
        if must_be_on_current_line:
            self.parser.require_is_not_at_eol(self.missing_expression)

        if self.consume_optional_start_parentheses():
            expression = self.parse(_IS_INSIDE_PARENTHESIS)
            self.consume_mandatory_end_parentheses()
            return expression
        else:
            mk_prefix_op_expr = self.consume_optional_prefix_operator()
            if mk_prefix_op_expr:
                expression = self.parse_mandatory_primitive(must_be_on_current_line=False)
                return mk_prefix_op_expr(expression)
            else:
                return self.parser.parse_mandatory_string_that_must_be_unquoted(
                    self.grammar.concept.syntax_element.name,
                    self.parse_primitive,
                    must_be_on_current_line=False)

    def parse_primitive(self, primitive_name: str) -> EXPR:
        symbol_name_of_symbol_reference = symbol_syntax.parse_symbol_reference__from_str(primitive_name)

        if symbol_name_of_symbol_reference is not None:
            return self.grammar.mk_reference(symbol_name_of_symbol_reference)

        if primitive_name in self.grammar.primitive_expressions:
            return self.grammar.primitive_expressions[primitive_name].parse_arguments(self.parser)
        elif not symbol_syntax.is_symbol_name(primitive_name):
            if primitive_name.startswith(option_syntax.OPTION_PREFIX_CHARACTER):
                raise SingleInstructionInvalidArgumentException(
                    'Invalid option: ' + primitive_name
                )
            else:
                err_msg = symbol_syntax.invalid_symbol_name_error(primitive_name)
                raise SingleInstructionInvalidArgumentException(err_msg)
        else:
            return self.grammar.mk_reference(primitive_name)

    def consume_optional_prefix_operator(self) -> Optional[Callable[[EXPR], EXPR]]:
        prefix_operator_name = self.parser.consume_optional_constant_string_that_must_be_unquoted_and_equal(
            self.prefix_op_expressions_keys,
            must_be_on_current_line=False
        )
        if prefix_operator_name:
            return self.grammar.prefix_op_expressions[prefix_operator_name].mk_expression
        else:
            return None

    def consume_optional_start_parentheses(self) -> bool:
        start_parenthesis = self.parser.consume_optional_constant_string_that_must_be_unquoted_and_equal(
            ['('],
            False)
        return start_parenthesis is not None

    def consume_mandatory_end_parentheses(self) -> None:
        self.parser.consume_mandatory_constant_string_that_must_be_unquoted_and_equal([')'],
                                                                                      lambda x: None,
                                                                                      'Expression inside ( )')
