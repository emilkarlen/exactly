from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_utils.file_transformer.file_transformer import FileTransformerResolver
from exactly_lib.test_case_utils.file_transformer.resolver_using_lines_transformers import \
    ResolveFileTransformerFromLinesTransformer
from exactly_lib.test_case_utils.lines_transformers.parse_lines_transformer import parse_lines_transformer


def parse_from_parse_source(source: ParseSource) -> FileTransformerResolver:
    lines_transformer = parse_lines_transformer(source)
    return ResolveFileTransformerFromLinesTransformer(lines_transformer)
