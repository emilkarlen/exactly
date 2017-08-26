from exactly_lib.named_element.resolver_structure import LinesTransformerResolver
from exactly_lib.test_case_utils.file_transformer import file_transformers
from exactly_lib.test_case_utils.file_transformer.env_vars_replacement_transformer import \
    PathResolverForEnvVarReplacement, FileTransformerForEnvVarsReplacement
from exactly_lib.test_case_utils.file_transformer.file_transformer import FileTransformerResolver, FileTransformer
from exactly_lib.type_system_values.lines_transformer import LinesTransformerStructureVisitor, IdentityLinesTransformer, \
    CustomLinesTransformer
from exactly_lib.util.symbol_table import SymbolTable


class ResolveFileTransformerFromLinesTransformer(FileTransformerResolver):
    def __init__(self,
                 dst_path_resolver: PathResolverForEnvVarReplacement,
                 lines_transformer_resolver: LinesTransformerResolver):
        self._dst_path_resolver = dst_path_resolver
        self._lines_transformer_resolver = lines_transformer_resolver

    def resolve(self, named_elements: SymbolTable) -> FileTransformer:
        lines_transformer = self._lines_transformer_resolver.resolve(named_elements)
        resolver = _FileTransformerResolver(self._dst_path_resolver)
        return resolver.visit(lines_transformer)


class _FileTransformerResolver(LinesTransformerStructureVisitor):
    def __init__(self,
                 dst_path_resolver: PathResolverForEnvVarReplacement):
        self._dst_path_resolver = dst_path_resolver

    def visit_identity(self, transformer: IdentityLinesTransformer) -> FileTransformer:
        return file_transformers.IdentityFileTransformer()

    def visit_custom(self, transformer: CustomLinesTransformer) -> FileTransformer:
        from exactly_lib.test_case_utils.lines_transformers import custom_transformer_names
        if transformer.name == custom_transformer_names.ENV_VAR_REPLACEMENT_TRANSFORMER_NAME:
            return FileTransformerForEnvVarsReplacement(self._dst_path_resolver)
        err_msg = 'Unknown {}: "{}"'.format(CustomLinesTransformer, transformer.name)
        raise ValueError(err_msg)
