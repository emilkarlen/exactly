import pathlib

from exactly_lib.test_case_file_structure import file_refs
from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.path_part import PathPart
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants, \
    SpecificPathRelativity
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds, PathResolvingEnvironmentPreOrPostSds
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.value_definition.concrete_restrictions import EitherStringOrFileRefRelativityRestriction, \
    StringRestriction, FileRefRelativityRestriction
from exactly_lib.value_definition.concrete_values import ValueVisitor, FileRefValue, StringValue
from exactly_lib.value_definition.value_structure import ValueReference, ValueContainer


# Do not want to have this class as public - but want it in a separate file ...
# so lets it have a "protected" name.
class _IdenticalToReferencedFileRefOrWithStringValueAsSuffix(FileRef):
    """
    A file-ref from a symbol reference, that can be either a string or a file-ref
    """

    def __init__(self,
                 symbol_name: str,
                 default_relativity: RelOptionType,
                 accepted_relativity_variants: PathRelativityVariants):
        self.symbol_name = symbol_name
        self.accepted_relativity_variants = accepted_relativity_variants
        self.file_ref_resolver = _SymbolValue2FileRefVisitor(default_relativity)

    def value_references_of_paths(self) -> list:
        symbol_reference = ValueReference(self.symbol_name,
                                          EitherStringOrFileRefRelativityRestriction(
                                              StringRestriction(),
                                              FileRefRelativityRestriction(
                                                  self.accepted_relativity_variants),
                                          ))
        return [symbol_reference]

    def relativity(self, value_definitions: SymbolTable) -> SpecificPathRelativity:
        return self._file_ref_for_actual_symbol(value_definitions).relativity(value_definitions)

    def path_suffix(self, symbols: SymbolTable) -> PathPart:
        return self._file_ref_for_actual_symbol(symbols).path_suffix(symbols)

    def path_suffix_path(self, symbols: SymbolTable) -> pathlib.Path:
        return self._file_ref_for_actual_symbol(symbols).path_suffix_path(symbols)

    def path_suffix_str(self, symbols: SymbolTable) -> str:
        return self._file_ref_for_actual_symbol(symbols).path_suffix_str(symbols)

    def exists_pre_sds(self, value_definitions: SymbolTable) -> bool:
        return self._file_ref_for_actual_symbol(value_definitions).exists_pre_sds(value_definitions)

    def file_path_post_sds(self, environment: PathResolvingEnvironmentPostSds) -> pathlib.Path:
        return self._file_ref_for_actual_symbol(environment.value_definitions).file_path_post_sds(environment)

    def file_path_pre_sds(self, environment: PathResolvingEnvironmentPreSds) -> pathlib.Path:
        return self._file_ref_for_actual_symbol(environment.value_definitions).file_path_pre_sds(environment)

    def file_path_pre_or_post_sds(self, environment: PathResolvingEnvironmentPreOrPostSds) -> pathlib.Path:
        fr = self._file_ref_for_actual_symbol(environment.value_definitions)
        if fr.exists_pre_sds(environment.value_definitions):
            return fr.file_path_pre_sds(environment)
        else:
            return fr.file_path_post_sds(environment)

    def _file_ref_for_actual_symbol(self, symbols: SymbolTable) -> FileRef:
        symbol = symbols.lookup(self.symbol_name)
        assert isinstance(symbol, ValueContainer), 'Implementation consistency/ValueContainer'
        return self.file_ref_resolver.visit(symbol.value)


class _SymbolValue2FileRefVisitor(ValueVisitor):
    def __init__(self,
                 default_relativity: RelOptionType):
        self.default_relativity = default_relativity

    def _visit_file_ref(self, value: FileRefValue) -> FileRef:
        return value.file_ref

    def _visit_string(self, value: StringValue) -> FileRef:
        s = value.string
        path_value = pathlib.Path(s)
        if path_value.is_absolute():
            return file_refs.absolute_file_name(s)
        else:
            return file_refs.of_rel_option(self.default_relativity,
                                           PathPartAsFixedPath(s))
