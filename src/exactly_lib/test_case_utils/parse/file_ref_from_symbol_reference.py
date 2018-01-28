import pathlib
from typing import Sequence

from exactly_lib.symbol.data.concrete_resolvers import SymbolValueResolverVisitor
from exactly_lib.symbol.data.path_resolver import FileRefResolver
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.data.value_resolvers.file_ref_with_symbol import StackedFileRef
from exactly_lib.symbol.data.value_resolvers.path_part_resolver import PathPartResolver
from exactly_lib.symbol.resolver_structure import SymbolContainer, DataValueResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.util.symbol_table import SymbolTable


# Do not want to have this class as public - but want it in a separate file ...
# so lets it have a "protected" name.
class _ResolverThatIsIdenticalToReferencedFileRefOrWithStringValueAsSuffix(FileRefResolver):
    """
    A file-ref from a symbol reference, that can be either a string or a file-ref
    """

    def __init__(self,
                 file_ref_or_string_symbol: SymbolReference,
                 suffix_resolver: PathPartResolver,
                 default_relativity: RelOptionType):
        self._file_ref_or_string_symbol = file_ref_or_string_symbol
        self._suffix_resolver = suffix_resolver
        self.default_relativity = default_relativity

    def resolve(self, symbols: SymbolTable) -> FileRef:
        symbol_value_2_file_ref = _SymbolSymbolValue2FileRefResolverVisitor(self._suffix_resolver,
                                                                            self.default_relativity,
                                                                            symbols)
        container = symbols.lookup(self._file_ref_or_string_symbol.name)
        assert isinstance(container, SymbolContainer), 'Implementation consistency/SymbolContainer'
        resolver = container.resolver
        assert isinstance(resolver, DataValueResolver), 'Implementation consistency/SymbolValueResolver'
        return symbol_value_2_file_ref.visit(resolver)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return [self._file_ref_or_string_symbol] + self._suffix_resolver.references


class _SymbolSymbolValue2FileRefResolverVisitor(SymbolValueResolverVisitor):
    def __init__(self,
                 suffix_resolver: PathPartResolver,
                 default_relativity: RelOptionType,
                 symbols: SymbolTable):
        self.suffix_resolver = suffix_resolver
        self.symbols = symbols
        self.default_relativity = default_relativity

    def _visit_file_ref(self, value: FileRefResolver) -> FileRef:
        file_ref = value.resolve(self.symbols)
        suffix_str = self.suffix_resolver.resolve(self.symbols).value()
        if not suffix_str:
            return file_ref
        suffix_str = suffix_str.lstrip('/')
        return StackedFileRef(file_ref, PathPartAsFixedPath(suffix_str))

    def _visit_string(self, value: StringResolver) -> FileRef:
        sv = value.resolve(self.symbols)
        first_suffix_str = sv.value_when_no_dir_dependencies()
        following_suffix_str = self.suffix_resolver.resolve(self.symbols).value()
        path_str = first_suffix_str + following_suffix_str
        path_value = pathlib.Path(path_str)
        if path_value.is_absolute():
            return file_refs.absolute_file_name(path_str)
        else:
            return file_refs.of_rel_option(self.default_relativity,
                                           PathPartAsFixedPath(path_str))
