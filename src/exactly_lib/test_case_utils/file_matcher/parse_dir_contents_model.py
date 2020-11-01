from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, ParserFromTokens
from exactly_lib.test_case_utils.described_dep_val import LogicWithDetailsDescriptionSdv
from exactly_lib.test_case_utils.file_matcher.impl import \
    dir_contents
from exactly_lib.test_case_utils.file_matcher.impl.model_constructor import ModelConstructor
from exactly_lib.test_case_utils.integer import parse_integer
from exactly_lib.type_val_prims.matcher.files_matcher import FilesMatcherModel


class Parser(ParserFromTokens[LogicWithDetailsDescriptionSdv[ModelConstructor[FilesMatcherModel]]]):
    DEPTH_INTEGER_PARSER = parse_integer.MandatoryIntegerParser(parse_integer.validator_for_non_negative)

    def parse(self,
              token_parser: TokenParser,
              ) -> LogicWithDetailsDescriptionSdv[ModelConstructor[FilesMatcherModel]]:
        return token_parser.consume_and_handle_optional_option(
            dir_contents.MODEL_CONSTRUCTOR__NON_RECURSIVE,
            self._parse_recursive,
            file_or_dir_contents.RECURSIVE_OPTION.name,
        )

    def _parse_recursive(self, token_parser: TokenParser,
                         ) -> LogicWithDetailsDescriptionSdv[ModelConstructor[FilesMatcherModel]]:
        mb_min_depth = token_parser.consume_and_handle_optional_option3(self.DEPTH_INTEGER_PARSER.parse,
                                                                        file_or_dir_contents.MIN_DEPTH_OPTION.name)
        mb_max_depth = token_parser.consume_and_handle_optional_option3(self.DEPTH_INTEGER_PARSER.parse,
                                                                        file_or_dir_contents.MAX_DEPTH_OPTION.name)
        return dir_contents.model_constructor__recursive(mb_min_depth, mb_max_depth)
