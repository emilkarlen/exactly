from typing import AbstractSet

from exactly_lib.section_document.element_parsers.ps_or_tp.parsers import ParserFromTokenParserBase
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.types.string_model.sdv import StringModelSdv


class StringModelParser(ParserFromTokenParserBase[StringModelSdv]):
    def __init__(self, accepted_file_relativities: AbstractSet[RelOptionType]):
        super().__init__()
        self._accepted_file_relativities = accepted_file_relativities

    def parse_from_token_parser(self, parser: TokenParser) -> StringModelSdv:
        raise NotImplementedError('todo')
