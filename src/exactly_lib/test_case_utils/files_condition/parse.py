from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import ParserWithCurrentLineVariants, PARSE_RESULT
from exactly_lib.test_case_utils.files_condition.structure import FilesConditionSdv


def parser() -> ParserWithCurrentLineVariants[FilesConditionSdv]:
    return _PARSER


class _Parser(ParserWithCurrentLineVariants[FilesConditionSdv]):
    def __init__(self):
        super().__init__(consume_last_line_if_is_at_eol_after_parse=True)

    def parse_from_token_parser(self,
                                tokens: TokenParser,
                                must_be_on_current_line: bool = False) -> PARSE_RESULT:
        raise NotImplementedError('todo')


def parse(tokens: TokenParser,
          must_be_on_current_line: bool = True) -> FilesConditionSdv:
    return _PARSER.parse_from_token_parser(tokens, must_be_on_current_line)


_PARSER = _Parser()
