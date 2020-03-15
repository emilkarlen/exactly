from exactly_lib.symbol.logic.files_matcher import FilesMatcherStv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_utils.matcher.impls import constant
from exactly_lib.type_system.logic.files_matcher import GenericFilesMatcherSdv, FilesMatcher
from exactly_lib_test.symbol.test_resources.files_matcher import is_reference_to_files_matcher__ref
from exactly_lib_test.symbol.test_resources.symbols_setup import LogicSymbolTypeContext, LogicTypeSymbolContext
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class FilesMatcherSymbolTypeContext(LogicSymbolTypeContext[FilesMatcherStv]):
    @staticmethod
    def of_generic(sdv: GenericFilesMatcherSdv) -> 'FilesMatcherSymbolTypeContext':
        return FilesMatcherSymbolTypeContext(FilesMatcherStv(sdv))

    @staticmethod
    def of_primitive(primitive: FilesMatcher) -> 'FilesMatcherSymbolTypeContext':
        return FilesMatcherSymbolTypeContext.of_generic(matchers.sdv_from_primitive_value(primitive))

    def reference_assertion(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return is_reference_to_files_matcher__ref(symbol_name)


class FilesMatcherSymbolContext(LogicTypeSymbolContext[FilesMatcherStv]):
    def __init__(self,
                 name: str,
                 type_context: FilesMatcherSymbolTypeContext,
                 ):
        super().__init__(name, type_context)

    @staticmethod
    def of_sdtv(name: str, sdtv: FilesMatcherStv) -> 'FilesMatcherSymbolContext':
        return FilesMatcherSymbolContext(
            name,
            FilesMatcherSymbolTypeContext(sdtv)
        )

    @staticmethod
    def of_generic(name: str, sdv: GenericFilesMatcherSdv) -> 'FilesMatcherSymbolContext':
        return FilesMatcherSymbolContext(
            name,
            FilesMatcherSymbolTypeContext.of_generic(sdv)
        )

    @staticmethod
    def of_primitive(name: str, primitive: FilesMatcher) -> 'FilesMatcherSymbolContext':
        return FilesMatcherSymbolContext(
            name,
            FilesMatcherSymbolTypeContext.of_primitive(primitive)
        )


ARBITRARY_SYMBOL_VALUE_CONTEXT = FilesMatcherSymbolTypeContext.of_primitive(constant.MatcherWithConstantResult(True))
