from typing import Sequence, Callable

from exactly_lib.symbol.logic.file_matcher import FileMatcherSdv
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.file_matcher.sdvs import file_matcher_sdv_from_ddv_parts
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherDdv
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers


def file_matcher_sdv_from_parts(references: Sequence[SymbolReference],
                                validator: DdvValidator,
                                matcher: Callable[[PathResolvingEnvironmentPreOrPostSds], FileMatcher],
                                ) -> FileMatcherSdv:
    def make_ddv(symbols: SymbolTable) -> FileMatcherDdv:
        def make_primitive(tcds: Tcds) -> FileMatcher:
            return matcher(PathResolvingEnvironmentPreOrPostSds(
                tcds,
                symbols
            ))

        return matchers.MatcherDdvFromPartsTestImpl(
            make_primitive,
            validator,
        )

    return file_matcher_sdv_from_ddv_parts(
        references,
        make_ddv,
    )
