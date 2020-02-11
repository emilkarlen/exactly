from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, ParserFromTokens, \
    ErrorMessageConfiguration
from exactly_lib.test_case_utils.condition.integer.parse_integer_condition import MandatoryIntegerParser
from exactly_lib.test_case_utils.described_dep_val import LogicWithDescriberSdv
from exactly_lib.test_case_utils.file_matcher.impl import \
    dir_contents
from exactly_lib.test_case_utils.file_matcher.impl.file_contents_utils import ModelConstructor
from exactly_lib.test_case_utils.matcher.impls import parse_integer_matcher
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel


class Parser(ParserFromTokens[LogicWithDescriberSdv[ModelConstructor[FilesMatcherModel]]]):
    DEPTH_INTEGER_PARSER = MandatoryIntegerParser(parse_integer_matcher.validator_for_non_negative)

    def __init__(self, is_at_eol_and_must_be_on_current_line_err_msg: ErrorMessageConfiguration):
        self._is_at_eol_and_must_be_on_current_line_err_msg = is_at_eol_and_must_be_on_current_line_err_msg

    def parse(self,
              token_parser: TokenParser,
              must_be_on_current_line: bool = False) -> LogicWithDescriberSdv[ModelConstructor[FilesMatcherModel]]:
        if must_be_on_current_line:
            token_parser.require_is_not_at_eol__conf(self._is_at_eol_and_must_be_on_current_line_err_msg)

        return token_parser.consume_and_handle_optional_option(
            dir_contents.MODEL_CONSTRUCTOR__NON_RECURSIVE,
            self._parse_recursive,
            file_or_dir_contents.RECURSIVE_OPTION.name,
        )

    def _parse_recursive(self, token_parser: TokenParser) -> LogicWithDescriberSdv[ModelConstructor[FilesMatcherModel]]:
        mb_min_depth = token_parser.consume_and_handle_optional_option3(self.DEPTH_INTEGER_PARSER.parse,
                                                                        file_or_dir_contents.MIN_DEPTH_OPTION.name)
        mb_max_depth = token_parser.consume_and_handle_optional_option3(self.DEPTH_INTEGER_PARSER.parse,
                                                                        file_or_dir_contents.MAX_DEPTH_OPTION.name)
        return dir_contents.model_constructor__recursive(mb_min_depth, mb_max_depth)
