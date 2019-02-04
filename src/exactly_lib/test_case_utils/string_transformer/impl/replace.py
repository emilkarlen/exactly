from exactly_lib.definitions.entity import types
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.string_transformer import StringTransformerResolver
from exactly_lib.test_case_utils.parse import parse_reg_ex
from exactly_lib.test_case_utils.string_transformer import resolvers
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerModel
from exactly_lib.util.cli_syntax.elements import argument as a

REPLACE_REPLACEMENT_ARGUMENT = a.Named(types.STRING_TYPE_INFO.syntax_element_name)
_MISSING_REPLACEMENT_ARGUMENT_ERR_MSG = 'Missing ' + REPLACE_REPLACEMENT_ARGUMENT.name


def parse_replace(parser: TokenParser) -> StringTransformerResolver:
    regex = parse_reg_ex.parse_regex(parser)
    parser.require_is_not_at_eol(_MISSING_REPLACEMENT_ARGUMENT_ERR_MSG)
    replacement = parser.consume_mandatory_token(_MISSING_REPLACEMENT_ARGUMENT_ERR_MSG)
    return resolvers.StringTransformerConstant(ReplaceStringTransformer(regex, replacement.string))


class ReplaceStringTransformer(StringTransformer):
    def __init__(self, compiled_regular_expression, replacement: str):
        self._compiled_regular_expression = compiled_regular_expression
        self._replacement = replacement

    @property
    def regex_pattern_string(self) -> str:
        return self._compiled_regular_expression.pattern

    @property
    def replacement(self) -> str:
        return self._replacement

    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        return (
            self._process_line(line)
            for line in lines
        )

    def _process_line(self, line: str) -> str:
        if line and line[-1] == '\n':
            return self._compiled_regular_expression.sub(self._replacement, line[:-1]) + '\n'
        else:
            return self._compiled_regular_expression.sub(self._replacement, line)

    def __str__(self):
        return '{}({})'.format(type(self).__name__,
                               str(self._compiled_regular_expression))
