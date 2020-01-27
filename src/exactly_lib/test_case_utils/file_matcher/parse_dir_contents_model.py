from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case_utils.condition.integer.parse_integer_condition import MandatoryIntegerParser
from exactly_lib.test_case_utils.file_matcher.impl import \
    dir_contents
from exactly_lib.test_case_utils.file_matcher.impl.file_contents_utils import ModelConstructor
from exactly_lib.test_case_utils.generic_dependent_value import Sdv
from exactly_lib.test_case_utils.matcher.impls import parse_integer_matcher
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel


def parse(token_parser: TokenParser
          ) -> Sdv[ModelConstructor[FilesMatcherModel]]:
    return token_parser.consume_and_handle_optional_option(
        dir_contents.MODEL_CONSTRUCTOR__NON_RECURSIVE,
        _parse_recursive_model,
        file_or_dir_contents.RECURSIVE_OPTION.name,
    )


_DEPTH_INTEGER_PARSER = MandatoryIntegerParser(parse_integer_matcher.validator_for_non_negative)


def _parse_recursive_model(token_parser: TokenParser
                           ) -> Sdv[ModelConstructor[FilesMatcherModel]]:
    mb_min_depth = token_parser.consume_and_handle_optional_option3(_DEPTH_INTEGER_PARSER.parse,
                                                                    file_or_dir_contents.MIN_DEPTH_OPTION.name)
    mb_max_depth = token_parser.consume_and_handle_optional_option3(_DEPTH_INTEGER_PARSER.parse,
                                                                    file_or_dir_contents.MAX_DEPTH_OPTION.name)
    return dir_contents.model_constructor__recursive(mb_min_depth, mb_max_depth)
