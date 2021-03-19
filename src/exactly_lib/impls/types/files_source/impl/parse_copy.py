from exactly_lib.impls.types.path import parse_path
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, ParserFromTokens
from exactly_lib.type_val_deps.types.files_source.sdv import FilesSourceSdv
from . import copy_dir_contents
from ...path.rel_opts_configuration import RelOptionArgumentConfiguration


class ParserOfCopy(ParserFromTokens[FilesSourceSdv]):
    def __init__(self, source_dir_argument: RelOptionArgumentConfiguration):
        self._src_path_parser = parse_path.PathParser(source_dir_argument)

    def parse(self, token_parser: TokenParser) -> FilesSourceSdv:
        src_dir_path = self._src_path_parser.parse_from_token_parser(token_parser)
        return copy_dir_contents.CopyDirContentsSdv(src_dir_path)
