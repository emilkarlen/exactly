import pathlib

from exactly_lib.symbol.concrete_restrictions import EitherStringOrFileRefRelativityRestriction, \
    StringRestriction, FileRefRelativityRestriction
from exactly_lib.symbol.concrete_values import ValueVisitor, FileRefResolver
from exactly_lib.symbol.string_resolver import StringResolver
from exactly_lib.symbol.value_structure import SymbolReference, ValueContainer
from exactly_lib.test_case_file_structure import file_refs
from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.util.symbol_table import SymbolTable


# Do not want to have this class as public - but want it in a separate file ...
# so lets it have a "protected" name.
class _ResolverThatIsIdenticalToReferencedFileRefOrWithStringValueAsSuffix(FileRefResolver):
    """
    A file-ref from a symbol reference, that can be either a string or a file-ref
    """

    def __init__(self,
                 symbol_name: str,
                 default_relativity: RelOptionType,
                 accepted_relativity_variants: PathRelativityVariants):
        self.default_relativity = default_relativity
        self.symbol_reference = SymbolReference(symbol_name,
                                                EitherStringOrFileRefRelativityRestriction(
                                                   StringRestriction(),
                                                   FileRefRelativityRestriction(
                                                       accepted_relativity_variants),
                                               ))

    def resolve(self, symbols: SymbolTable) -> FileRef:
        symbol_value_2_file_ref = _SymbolValue2FileRefVisitor(self.default_relativity, symbols)
        symbol = symbols.lookup(self.symbol_reference.name)
        assert isinstance(symbol, ValueContainer), 'Implementation consistency/ValueContainer'
        return symbol_value_2_file_ref.visit(symbol.value)

    @property
    def references(self) -> list:
        return [self.symbol_reference]


class _SymbolValue2FileRefVisitor(ValueVisitor):
    def __init__(self,
                 default_relativity: RelOptionType,
                 symbols: SymbolTable):
        self.symbols = symbols
        self.default_relativity = default_relativity

    def _visit_file_ref(self, value: FileRefResolver) -> FileRef:
        return value.resolve(self.symbols)

    def _visit_string(self, value: StringResolver) -> FileRef:
        sv = value.resolve(self.symbols)
        s = sv.value_when_no_dir_dependencies()
        path_value = pathlib.Path(s)
        if path_value.is_absolute():
            return file_refs.absolute_file_name(s)
        else:
            return file_refs.of_rel_option(self.default_relativity,
                                           PathPartAsFixedPath(s))
