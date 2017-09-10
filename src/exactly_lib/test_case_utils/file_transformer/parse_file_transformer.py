from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import TokenParserPrime
from exactly_lib.test_case_utils.file_transformer.file_transformer import FileTransformerResolver
from exactly_lib.test_case_utils.file_transformer.resolver_using_lines_transformers import \
    ResolveFileTransformerFromLinesTransformer
from exactly_lib.test_case_utils.lines_transformer import parse_lines_transformer


def parse_optional_from_parse_source(source: ParseSource) -> FileTransformerResolver:
    lines_transformer = parse_lines_transformer.parse_lines_transformer(source)
    return ResolveFileTransformerFromLinesTransformer(lines_transformer)


def parse_optional_from_token_parser(parser: TokenParserPrime) -> FileTransformerResolver:
    lines_transformer = parse_lines_transformer.parse_optional_transformer_resolver(parser)
    return ResolveFileTransformerFromLinesTransformer(lines_transformer)
