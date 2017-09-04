from exactly_lib.named_element.resolver_structure import LinesTransformerResolver
from exactly_lib.test_case_utils.file_transformer import file_transformers
from exactly_lib.test_case_utils.file_transformer.file_transformer import FileTransformerResolver, FileTransformer
from exactly_lib.test_case_utils.lines_transformer.transformers import IdentityLinesTransformer
from exactly_lib.util.symbol_table import SymbolTable


class ResolveFileTransformerFromLinesTransformer(FileTransformerResolver):
    def __init__(self, lines_transformer_resolver: LinesTransformerResolver):
        self._lines_transformer_resolver = lines_transformer_resolver

    def resolve(self, named_elements: SymbolTable) -> FileTransformer:
        lines_transformer = self._lines_transformer_resolver.resolve(named_elements)
        if isinstance(lines_transformer, IdentityLinesTransformer):
            return file_transformers.IdentityFileTransformer()
        else:
            from exactly_lib.test_case_utils.file_transformer.from_lines_transformer import \
                FileTransformerFromLinesTransformer
            return FileTransformerFromLinesTransformer(lines_transformer)

    @property
    def references(self) -> list:
        return self._lines_transformer_resolver.references
