from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations import token_parse
from exactly_lib.test_case_utils.file_transformer.actual_file_transformer import ActualFileTransformerResolver, \
    PathResolverForEnvVarReplacement
from exactly_lib.test_case_utils.file_transformer.actual_file_transformers import \
    ConstantActualFileTransformerResolver, ActualFileTransformerForEnvVarsReplacement
from exactly_lib.test_case_utils.file_transformer.actual_file_transformers import IdentityFileTransformer
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.option_parsing import matches
from exactly_lib.util.parse.token import TokenType

WITH_REPLACED_ENV_VARS_OPTION_NAME = a.OptionName(long_name='with-replaced-env-vars')
WITH_REPLACED_ENV_VARS_OPTION = option_syntax.option_syntax(WITH_REPLACED_ENV_VARS_OPTION_NAME)


class FileTransformerParser:
    def __init__(self, dst_path_resolver: PathResolverForEnvVarReplacement):
        self._dst_path_resolver = dst_path_resolver

    def parse_from_parse_source(self, source: ParseSource) -> ActualFileTransformerResolver:
        with_replaced_env_vars = False
        peek_source = source.copy
        next_arg = token_parse.parse_token_or_none_on_current_line(peek_source)
        if next_arg is not None and next_arg.type == TokenType.PLAIN and \
                matches(WITH_REPLACED_ENV_VARS_OPTION_NAME, next_arg.string):
            source.catch_up_with(peek_source)
            with_replaced_env_vars = True
        actual_file_transformer = IdentityFileTransformer()
        if with_replaced_env_vars:
            actual_file_transformer = ActualFileTransformerForEnvVarsReplacement(
                self._dst_path_resolver)
        return ConstantActualFileTransformerResolver(actual_file_transformer)
