from exactly_lib.definitions.entity import types, syntax_elements
from exactly_lib.impls.types.expression import grammar, parser as ep
from exactly_lib.impls.types.expression.parser import GrammarParsers
from exactly_lib.impls.types.string_transformer import names
from exactly_lib.impls.types.string_transformer import sdvs
from exactly_lib.impls.types.string_transformer.impl import sequence_sdv, identity, case_converters, \
    tcds_paths_replacement, strip_space
from exactly_lib.impls.types.string_transformer.impl.filter import parse as parse_filter
from exactly_lib.impls.types.string_transformer.impl.replace import setup as _replace_setup
from exactly_lib.impls.types.string_transformer.impl.run_program import parse as parse_run
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
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
    primitives=(
        NameAndValue(
            names.FILTER_TRANSFORMER_NAME,
            grammar.Primitive(
                parse_filter.Parser(names.FILTER_TRANSFORMER_NAME).parse,
                parse_filter.SyntaxDescription(),
            )
        ),
        NameAndValue(
            names.GREP_TRANSFORMER_NAME,
            grammar.Primitive(
                parse_filter.GrepShortcutParser(names.FILTER_TRANSFORMER_NAME).parse,
                parse_filter.GrepShortcutSyntaxDescription(names.FILTER_TRANSFORMER_NAME),
            )
        ),
        NameAndValue(
            names.REPLACE_TRANSFORMER_NAME,
            grammar.Primitive(_replace_setup.ParserOfReplace().parse,
                              _replace_setup.SyntaxDescription())
        ),
        NameAndValue(
            names.CHARACTER_CASE,
            grammar.Primitive(case_converters.Parser().parse,
                              case_converters.SyntaxDescription())
        ),
        NameAndValue(
            names.STRIP_SPACE,
            grammar.Primitive(strip_space.Parser().parse,
                              strip_space.SyntaxDescription())
        ),
        NameAndValue(
            names.RUN_PROGRAM_TRANSFORMER_NAME,
            grammar.Primitive(parse_run.parse,
                              parse_run.SyntaxDescription())
        ),
        NameAndValue(
            names.TCDS_PATH_REPLACEMENT,
            grammar.Primitive(tcds_paths_replacement.parse,
                              tcds_paths_replacement.SyntaxDescription())
        ),
        NameAndValue(
            names.IDENTITY_TRANSFORMER_NAME,
            grammar.Primitive(identity.parse_identity,
                              identity.SyntaxDescription())
        ),
    ),
    prefix_operators=(),
    infix_operators_in_order_of_increasing_precedence=[[
        NameAndValue(
            names.SEQUENCE_OPERATOR_NAME,
            grammar.InfixOperator(
                sequence_sdv.StringTransformerSequenceSdv,
                sequence_sdv.SYNTAX_DESCRIPTION,
            )
        ),
    ]],
)

_PARSERS_FOR_MUST_BE_ON_CURRENT_LINE = ep.parsers_for_must_be_on_current_line(GRAMMAR)
