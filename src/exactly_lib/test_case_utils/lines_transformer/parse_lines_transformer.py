from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.entity import types, syntax_elements
from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.resolver_structure import LinesTransformerResolver
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.err_msg.error_info import ErrorMessagePartConstructor
from exactly_lib.test_case_utils.expression import grammar, parser as parse_expression
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.test_case_utils.lines_transformer import resolvers
from exactly_lib.test_case_utils.lines_transformer.transformers import IdentityLinesTransformer, \
    ReplaceLinesTransformer
from exactly_lib.test_case_utils.parse import parse_reg_ex
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.textformat_parser import TextParser

IDENTITY_TRANSFORMER_RESOLVER = resolvers.LinesTransformerConstant(IdentityLinesTransformer())

REPLACE_TRANSFORMER_NAME = 'replace'

SELECT_TRANSFORMER_NAME = 'select'

SEQUENCE_OPERATOR_NAME = '|'

REPLACE_REGEX_ARGUMENT = instruction_arguments.REG_EX

REPLACE_REPLACEMENT_ARGUMENT = a.Named(types.STRING_TYPE_INFO.syntax_element_name)

_MISSING_REPLACEMENT_ARGUMENT_ERR_MSG = 'Missing ' + REPLACE_REPLACEMENT_ARGUMENT.name

LINES_TRANSFORMER_ARGUMENT = a.Named(types.LINES_TRANSFORMER_TYPE_INFO.syntax_element_name)


class LinesTransformerDescriptor(ErrorMessagePartConstructor):
    def __init__(self, resolver: LinesTransformerResolver):
        self.resolver = resolver

    def lines(self, environment: InstructionEnvironmentForPostSdsStep) -> list:
        transformer = self.resolver.resolve(environment.symbols)
        # FIXME
        line = types.LINES_TRANSFORMER_TYPE_INFO.syntax_element_name + ' : (FIXME) ' + str(transformer)
        return [line]


def parse_lines_transformer(source: ParseSource) -> LinesTransformerResolver:
    with token_stream_parser.from_parse_source(source) as tp:
        return parse_optional_transformer_resolver(tp)


def parse_optional_transformer_resolver(parser: TokenParser) -> LinesTransformerResolver:
    """
    :return: The identity transformer, if transformer option is not given.
    """
    return parser.consume_and_handle_optional_option(
        IDENTITY_TRANSFORMER_RESOLVER,
        parse_lines_transformer_from_token_parser,
        instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION_NAME)


def parse_optional_transformer_resolver_preceding_mandatory_element(parser: TokenParser,
                                                                    mandatory_element_name: str
                                                                    ) -> LinesTransformerResolver:
    """
    :return: The identity transformer, if transformer option is not given.
    """
    parser.require_existing_valid_head_token(mandatory_element_name)
    return parse_optional_transformer_resolver(parser)


def parse_lines_transformer_from_token_parser(parser: TokenParser) -> LinesTransformerResolver:
    return parse_expression.parse(GRAMMAR, parser)


def parse_replace(parser: TokenParser) -> LinesTransformerResolver:
    regex = parse_reg_ex.parse_regex(parser)
    parser.require_is_not_at_eol(_MISSING_REPLACEMENT_ARGUMENT_ERR_MSG)
    replacement = parser.consume_mandatory_token(_MISSING_REPLACEMENT_ARGUMENT_ERR_MSG)
    return resolvers.LinesTransformerConstant(ReplaceLinesTransformer(regex, replacement.string))


def parse_select(parser: TokenParser) -> LinesTransformerResolver:
    line_matcher = parse_line_matcher.parse_line_matcher_from_token_parser(parser)
    return resolvers.LinesTransformerSelectResolver(line_matcher)


ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS = {
    '_REG_EX_': REPLACE_REGEX_ARGUMENT.name,
    '_STRING_': REPLACE_REPLACEMENT_ARGUMENT.name,
    '_TRANSFORMER_': types.LINES_TRANSFORMER_TYPE_INFO.name.singular,
    '_LINE_MATCHER_': types.LINE_MATCHER_TYPE_INFO.name.singular,
    '_TRANSFORMERS_': types.LINES_TRANSFORMER_TYPE_INFO.name.plural,
}

_TEXT_PARSER = TextParser(ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS)

_REPLACE_TRANSFORMER_SED_DESCRIPTION = """\
Replaces parts of the contents of a file.


Every occurrence of regular expression {_REG_EX_} - on a single line - is replaced with {_STRING_}.


Backslash escapes in {_STRING_} are processed.
That is, \\n is converted to a single newline character, \\r is converted to a carriage return, and so forth.


Unknown escapes such as \\& are left alone.


Backreferences, such as \\6, are replaced with the substring matched by group 6 in {_REG_EX_}.
"""

_SELECT_TRANSFORMER_SED_DESCRIPTION = """\
Keeps lines matched by the given {_LINE_MATCHER_},
and discards lines not matched."""

_SEQUENCE_TRANSFORMER_SED_DESCRIPTION = """\
Sequence of two or more {_TRANSFORMERS_}.

The result of the {_TRANSFORMER_} to the left is feed to the
{_TRANSFORMER_} to the right.
"""

_REPLACE_SYNTAX_DESCRIPTION = grammar.SimpleExpressionDescription(
    argument_usage_list=[
        a.Single(a.Multiplicity.MANDATORY,
                 REPLACE_REGEX_ARGUMENT),
        a.Single(a.Multiplicity.MANDATORY,
                 REPLACE_REPLACEMENT_ARGUMENT),
    ],
    description_rest=_TEXT_PARSER.fnap(_REPLACE_TRANSFORMER_SED_DESCRIPTION),
    see_also_targets=[syntax_elements.REGEX_SYNTAX_ELEMENT.cross_reference_target],
)

_SELECT_SYNTAX_DESCRIPTION = grammar.SimpleExpressionDescription(
    argument_usage_list=[
        a.Single(a.Multiplicity.MANDATORY,
                 instruction_arguments.LINE_MATCHER),
    ],
    description_rest=_TEXT_PARSER.fnap(_SELECT_TRANSFORMER_SED_DESCRIPTION),
    see_also_targets=[types.LINE_MATCHER_TYPE_INFO.cross_reference_target],
)

_SEQUENCE_SYNTAX_DESCRIPTION = grammar.OperatorExpressionDescription(
    _TEXT_PARSER.fnap(_SEQUENCE_TRANSFORMER_SED_DESCRIPTION)
)

_CONCEPT = grammar.Concept(
    types.LINES_TRANSFORMER_TYPE_INFO.name,
    types.LINES_TRANSFORMER_TYPE_INFO.identifier,
    LINES_TRANSFORMER_ARGUMENT,
)

GRAMMAR = grammar.Grammar(
    _CONCEPT,
    mk_reference=resolvers.LinesTransformerReference,
    simple_expressions={
        REPLACE_TRANSFORMER_NAME:
            grammar.SimpleExpression(parse_replace,
                                     _REPLACE_SYNTAX_DESCRIPTION),
        SELECT_TRANSFORMER_NAME:
            grammar.SimpleExpression(parse_select,
                                     _SELECT_SYNTAX_DESCRIPTION),
    },
    complex_expressions={
        SEQUENCE_OPERATOR_NAME: grammar.ComplexExpression(
            resolvers.LinesTransformerSequenceResolver,
            _SEQUENCE_SYNTAX_DESCRIPTION,
        ),
    },
    prefix_expressions={},
)
