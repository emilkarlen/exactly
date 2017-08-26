from exactly_lib.named_element.lines_transformers import LinesTransformerConstant
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations import token_parse
from exactly_lib.test_case_utils.file_transformer.file_transformer import FileTransformerResolver
from exactly_lib.test_case_utils.file_transformer.from_lines_transformer import DestinationFilePathResolver
from exactly_lib.test_case_utils.file_transformer.resolver_using_lines_transformers import \
    ResolveFileTransformerFromLinesTransformer
from exactly_lib.test_case_utils.lines_transformers import custom_transformers as ct
from exactly_lib.type_system_values.lines_transformer import IdentityLinesTransformer
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.option_parsing import matches
from exactly_lib.util.parse.token import TokenType

WITH_REPLACED_ENV_VARS_OPTION_NAME = a.OptionName(long_name='with-replaced-env-vars')
WITH_REPLACED_ENV_VARS_OPTION = option_syntax.option_syntax(WITH_REPLACED_ENV_VARS_OPTION_NAME)


class FileTransformerParser:
    def __init__(self, dst_path_resolver: DestinationFilePathResolver):
        self._dst_path_resolver = dst_path_resolver

    def parse_from_parse_source(self, source: ParseSource) -> FileTransformerResolver:
        with_replaced_env_vars = False
        peek_source = source.copy
        next_arg = token_parse.parse_token_or_none_on_current_line(peek_source)
        if next_arg is not None and next_arg.type == TokenType.PLAIN and \
                matches(WITH_REPLACED_ENV_VARS_OPTION_NAME, next_arg.string):
            source.catch_up_with(peek_source)
            with_replaced_env_vars = True
        lines_transformer = IdentityLinesTransformer()
        if with_replaced_env_vars:
            lines_transformer = ct.CUSTOM_LINES_TRANSFORMERS[ct.ENV_VAR_REPLACEMENT_TRANSFORMER_NAME]
        transformer_resolver = LinesTransformerConstant(lines_transformer)
        return ResolveFileTransformerFromLinesTransformer(self._dst_path_resolver,
                                                          transformer_resolver)
