import pathlib
from typing import Callable

from exactly_lib.impls.types.files_source import parse
from exactly_lib.type_val_deps.types.files_source.ddv import FilesSourceAdv
from exactly_lib.type_val_deps.types.files_source.sdv import FilesSourceSdv
from exactly_lib.type_val_prims.files_source.files_source import FilesSource
from exactly_lib_test.impls.types.logic.test_resources.integration_check import IntegrationChecker
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Arrangement, AssertionResolvingEnvironment, \
    ExecutionExpectation, adv_asrt__any, prim_asrt__any
from exactly_lib_test.impls.types.test_resources.parse_checker import parse_checker
from exactly_lib_test.test_resources.files.file_structure import FileSystemElements
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.dep_variants.test_resources.full_deps import execution_check
from exactly_lib_test.type_val_deps.types.files_source.test_resources.properties_configuration import \
    FilesSourcePropertiesConfiguration

_PROPERTIES_CONFIGURATION = FilesSourcePropertiesConfiguration()

CHECKER: IntegrationChecker[FilesSource, FileSystemElements, pathlib.Path] = IntegrationChecker(
    parse.parsers().full,
    _PROPERTIES_CONFIGURATION,
    check_application_result_with_tcds=True,
)

PARSE_CHECKER__FULL = parse_checker(parse.parsers().full)


def execution_assertion(
        model: FileSystemElements,
        arrangement: Arrangement,
        execution: ExecutionExpectation[pathlib.Path] = ExecutionExpectation(),
        primitive: Callable[[AssertionResolvingEnvironment], Assertion[FilesSource]] = prim_asrt__any,
        adv: Callable[[AssertionResolvingEnvironment], Assertion[FilesSourceAdv]] = adv_asrt__any,
) -> Assertion[FilesSourceSdv]:
    return execution_check.ExecutionAssertion(
        model,
        arrangement,
        adv,
        primitive,
        execution,
        _PROPERTIES_CONFIGURATION.applier(),
        _PROPERTIES_CONFIGURATION.new_execution_checker(),
        check_application_result_with_tcds=True,
    )
