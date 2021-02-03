from typing import Generic, Optional, Callable, Mapping, Sequence, AbstractSet, List

from exactly_lib.definitions import formatting
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.ps_or_tp import parsers as parser_impls
from exactly_lib.section_document.element_parsers.ps_or_tp.parser import Parser
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol import symbol_syntax
from exactly_lib.util import collection
from exactly_lib.util.name_and_value import NameAndValue
from .grammar import Grammar, EXPR, InfixOperator


class GrammarParsers(Generic[EXPR]):
    def __init__(self,
                 simple: Parser[EXPR],
                 full: Parser[EXPR],
                 ):
        self._simple = simple
        self._full = full

    @property
    def simple(self) -> Parser[EXPR]:
        """A parser that parses a simple expression - i.e. without binary operators
        (except when inside parentheses, of course).
        """
        return self._simple

    @property
    def full(self) -> Parser[EXPR]:
        """A parser that parses a full expression - i.e. with binary operators"""
        return self._full


def parsers(grammar: Grammar[EXPR],
            must_be_on_current_line: bool = True,
            ) -> GrammarParsers[EXPR]:
    """Parsers that parses a mandatory EXPR"""
    return GrammarParsers(
        simple=parser_impls.parser_for_must_be_on_current_line(
            grammar,
            _SimpleParserOnAnyLineParser(grammar),
            must_be_on_current_line,
        ),
        full=parser_impls.parser_for_must_be_on_current_line(
            grammar,
            _FullParserOnAnyLineParser(grammar),
            must_be_on_current_line,
        ),
    )


def parsers_for_must_be_on_current_line(grammar: Grammar[EXPR]) -> Mapping[bool, GrammarParsers[EXPR]]:
    return {
        b: parsers(grammar, must_be_on_current_line=b)
        for b in [False, True]
    }


class _SimpleParserOnAnyLineParser(Generic[EXPR], parser_impls.ParserFromTokenParserBase[EXPR]):
    def __init__(self, grammar: Grammar[EXPR]):
        super().__init__(False, False)
        self._grammar = grammar

    def parse_from_token_parser(self, parser: TokenParser) -> EXPR:
        return _Parser(self._grammar, parser).parse_mandatory_primitive(False)


class _FullParserOnAnyLineParser(Generic[EXPR], parser_impls.ParserFromTokenParserBase[EXPR]):
    def __init__(self, grammar: Grammar[EXPR]):
        super().__init__(False, False)
        self._grammar = grammar

    def parse_from_token_parser(self, parser: TokenParser) -> EXPR:
        return _Parser(self._grammar, parser).parse(_NEXT_EXPR_ON_ANY_LINE)


_IS_INSIDE_PARENTHESES = 1
_NEXT_EXPR_ON_ANY_LINE = 2


class _Parser(Generic[EXPR]):
    def __init__(self,
                 grammar: Grammar[EXPR],
                 parser: TokenParser,
                 ):
        self.parser = parser
        self.grammar = grammar
        self.prefix_operator_names = self.grammar.prefix_operators.keys()
        self._err_msg_renderer = _ErrorMessageRenderer(grammar)

    def parse(self, new_line_ignore: Optional[int]) -> EXPR:
        return self.parse_w_maybe_infix_ops(new_line_ignore,
                                            self.grammar.infix_ops_inc_precedence)

    def parse_w_maybe_infix_ops(
            self,
            new_line_ignore: Optional[int],
            infix_ops_levels: Sequence[Mapping[str, InfixOperator[EXPR]]],
    ) -> EXPR:
        return (
            self.parse_w_infix_ops(new_line_ignore,
                                   infix_ops_levels)
            if infix_ops_levels
            else
            self.parse_mandatory_primitive(new_line_ignore is None)
        )

    def parse_w_infix_ops(
            self,
            new_line_ignore: Optional[int],
            infix_ops_levels: Sequence[Mapping[str, InfixOperator[EXPR]]],
    ) -> EXPR:
        infix_ops__curr_level = infix_ops_levels[0]
        infix_op_names__curr_level = infix_ops__curr_level.keys()
        infix_ops__next_levels = infix_ops_levels[1:]

        expression = self.parse_w_maybe_infix_ops(new_line_ignore is None,
                                                  infix_ops__next_levels)

        if new_line_ignore is _NEXT_EXPR_ON_ANY_LINE:
            new_line_ignore = None

        infix_operator_name = self.parse_optional_infix_op_name(new_line_ignore is None,
                                                                infix_op_names__curr_level)

        while infix_operator_name:
            expression = self.infix_op_sequence_for_single_op(
                infix_operator_name,
                infix_ops__curr_level[infix_operator_name],
                expression,
                infix_ops__next_levels,
                is_inside_parens=new_line_ignore is _IS_INSIDE_PARENTHESES
            )
            infix_operator_name = self.parse_optional_infix_op_name(new_line_ignore is None,
                                                                    infix_op_names__curr_level)

        return expression

    def parse_optional_infix_op_name(self,
                                     must_be_on_current_line: bool,
                                     operators: AbstractSet[str],
                                     ) -> str:
        return self.parser.consume_optional_constant_string_that_must_be_unquoted_and_equal(
            operators,
            must_be_on_current_line,
        )

    def infix_op_sequence_for_single_op(
            self,
            operator_name: str,
            operator: InfixOperator[EXPR],
            first_operand: EXPR,
            infix_ops_levels: Sequence[Mapping[str, InfixOperator[EXPR]]],
            is_inside_parens: bool,
    ) -> EXPR:
        single_accepted_operator = (operator_name,)

        operands = [first_operand]

        def parse_mandatory_operand_and_append():
            next_operand = self.parse_w_maybe_infix_ops(_NEXT_EXPR_ON_ANY_LINE,
                                                        infix_ops_levels)
            operands.append(next_operand)

        parse_mandatory_operand_and_append()
        while self.parser.consume_optional_constant_string_that_must_be_unquoted_and_equal(
                single_accepted_operator,
                must_be_on_current_line=not is_inside_parens):
            parse_mandatory_operand_and_append()

        return operator.mk_expression(operands)

    def parse_mandatory_primitive(self, must_be_on_current_line: bool) -> EXPR:
        if must_be_on_current_line:
            self.parser.require_is_not_at_eol(self._err_msg_renderer.missing_element())

        if self.consume_optional_start_parentheses():
            expression = self.parse(_IS_INSIDE_PARENTHESES)
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

        if primitive_name in self.grammar.primitives:
            return self.grammar.primitives[primitive_name].parse_arguments(self.parser)
        elif not symbol_syntax.is_symbol_name(primitive_name):
            err_msg = self._err_msg_renderer.unknown_primitive(primitive_name)
            raise SingleInstructionInvalidArgumentException(err_msg)
        else:
            return self.grammar.mk_reference(primitive_name)

    def consume_optional_prefix_operator(self) -> Optional[Callable[[EXPR], EXPR]]:
        prefix_operator_name = self.parser.consume_optional_constant_string_that_must_be_unquoted_and_equal(
            self.prefix_operator_names,
            must_be_on_current_line=False
        )
        if prefix_operator_name:
            return self.grammar.prefix_operators[prefix_operator_name].mk_expression
        else:
            return None

    def consume_optional_start_parentheses(self) -> bool:
        start_parenthesis = self.parser.consume_optional_constant_string_that_must_be_unquoted_and_equal(
            ('(',),
            False,
        )
        return start_parenthesis is not None

    def consume_mandatory_end_parentheses(self) -> None:
        self.parser.consume_mandatory_constant_string_that_must_be_unquoted_and_equal(
            [')', ] + self._infix_op_names(),
            lambda x: None,
            'Expression inside ( )',
        )

    def _infix_op_names(self) -> List[str]:
        return collection.concat_list([
            list(map(NameAndValue.name.fget, precedence_level))
            for precedence_level in self.grammar.infix_ops_inc_precedence__seq
        ])


class _ErrorMessageRenderer:
    def __init__(self, grammar: Grammar):
        self._grammar = grammar

    def missing_element(self) -> str:
        return 'Missing ' + self._grammar.concept.syntax_element.name

    def unknown_primitive(self, primitive_name: str) -> str:
        lines = [
            'Unknown {}: {}'.format(self._grammar.concept.syntax_element.name,
                                    formatting.parsed_str(primitive_name)),
            '',
            'Expecting one of',
        ]
        lines += [
            '  ' + primitive
            for primitive in self._known_primitives_and_prefix_operators()
        ]
        lines += [
            '',
            symbol_syntax.SYMBOL_SYNTAX_DESCRIPTION_LINE,
        ]
        return '\n'.join(lines)

    def _known_primitives_and_prefix_operators(self) -> List[str]:
        ret_val = [
            formatting.keyword(primitive.name)
            for primitive in self._grammar.primitives__seq
        ]
        ret_val += [
            formatting.keyword(prefix_operator.name)
            for prefix_operator in self._grammar.prefix_operators__seq
        ]
        ret_val += [
            syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT.singular_name,
            syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.singular_name,
            formatting.keyword('('),
        ]
        return ret_val
