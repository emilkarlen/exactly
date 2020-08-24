from exactly_lib.definitions.entity import types, syntax_elements
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.test_case_utils.expression import grammar, parser as ep
from exactly_lib.test_case_utils.expression.parser import GrammarParsers
from exactly_lib.test_case_utils.string_transformer import names
from exactly_lib.test_case_utils.string_transformer import sdvs
from exactly_lib.test_case_utils.string_transformer.impl import filter, replace, sequence, identity
from exactly_lib.test_case_utils.string_transformer.impl.run_program import parse as parse_run
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.name_and_value import NameAndValue

STRING_TRANSFORMER_ARGUMENT = a.Named(types.STRING_TRANSFORMER_TYPE_INFO.syntax_element_name)


def parsers(must_be_on_current_line: bool = False) -> GrammarParsers[StringTransformerSdv]:
    return _PARSERS_FOR_MUST_BE_ON_CURRENT_LINE[must_be_on_current_line]


_CONCEPT = grammar.Concept(
    types.STRING_TRANSFORMER_TYPE_INFO.name,
    types.STRING_TRANSFORMER_TYPE_INFO.identifier,
    syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT.argument,
)


def _mk_reference(name: str) -> StringTransformerSdv:
    return sdvs.StringTransformerSdvReference(name)


GRAMMAR = grammar.Grammar(
    _CONCEPT,
    mk_reference=_mk_reference,
    primitive_expressions=(
        NameAndValue(
            names.REPLACE_TRANSFORMER_NAME,
            grammar.PrimitiveExpression(replace.parse_replace,
                                        replace.SyntaxDescription())
        ),
        NameAndValue(
            names.SELECT_TRANSFORMER_NAME,
            grammar.PrimitiveExpression(filter.parse_filter,
                                        filter.SyntaxDescription())
        ),
        NameAndValue(
            names.RUN_PROGRAM_TRANSFORMER_NAME,
            grammar.PrimitiveExpression(parse_run.parse,
                                        parse_run.SyntaxDescription())
        ),
        NameAndValue(
            names.IDENTITY_TRANSFORMER_NAME,
            grammar.PrimitiveExpression(identity.parse_identity,
                                        identity.SyntaxDescription())
        ),
    ),
    prefix_op_expressions=(),
    infix_op_expressions_in_order_of_decreasing_precedence=[[
        NameAndValue(
            names.SEQUENCE_OPERATOR_NAME,
            grammar.InfixOpExpression(
                sequence.StringTransformerSequenceSdv,
                sequence.SYNTAX_DESCRIPTION,
            )
        ),
    ]],
)

_PARSERS_FOR_MUST_BE_ON_CURRENT_LINE = ep.parsers_for_must_be_on_current_line(GRAMMAR)
