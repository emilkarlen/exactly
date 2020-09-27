import pathlib
import unittest
from typing import List

from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.sdv_structure import SymbolContainer
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, FilesMatcherSdv
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_case_utils.files_matcher.models.test_resources.assertion import \
    FilesMatcherModelContentsAssertion
from exactly_lib_test.test_case_utils.files_matcher.test_resources.symbol_context import FilesMatcherSymbolValueContext
from exactly_lib_test.test_case_utils.matcher.test_resources import assertion_applier
from exactly_lib_test.test_case_utils.matcher.test_resources.assertion_applier import ApplicationAssertionSetup
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def matcher(put: unittest.TestCase,
            model_dir: PathSdv,
            expected_contents: List[pathlib.Path]) -> FilesMatcherSdv:
    return assertion_applier.matcher(
        put,
        application_assertion=_ModelCheckerAssertionSetup(model_dir, expected_contents)
    )


def matcher__sym_tbl_container(put: unittest.TestCase,
                               model_dir: PathSdv,
                               expected_contents: List[pathlib.Path]) -> SymbolContainer:
    return FilesMatcherSymbolValueContext.of_sdv(
        matcher(put, model_dir, expected_contents)
    ).container


class _ModelCheckerAssertionSetup(ApplicationAssertionSetup[FilesMatcherModel, FilesMatcherModel]):
    def __init__(self,
                 model_dir: PathSdv,
                 expected_contents: List[pathlib.Path],
                 ):
        self._model_dir = model_dir
        self._expected_contents = expected_contents

    def get_assertion(self,
                      symbols: SymbolTable,
                      tcds: TestCaseDs,
                      env: ApplicationEnvironment,
                      ) -> ValueAssertion[FilesMatcherModel]:
        return FilesMatcherModelContentsAssertion(
            self._model_dir.resolve(symbols).value_of_any_dependency(tcds),
            self._expected_contents,
        )

    def get_actual(self, model: FilesMatcherModel) -> FilesMatcherModel:
        return model
