import unittest
from typing import List

from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_case_utils.files_matcher.models.test_resources.assertion import \
    ModelContentsAssertion
from exactly_lib_test.test_case_utils.matcher.test_resources import assertion_applier
from exactly_lib_test.test_case_utils.matcher.test_resources.assertion_applier import ApplicationAssertionSetup
from exactly_lib_test.test_resources.files.file_structure import FileSystemElement
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def matcher(put: unittest.TestCase,
            model_dir: PathSdv,
            expected_contents: List[FileSystemElement]) -> FilesMatcherSdv:
    return FilesMatcherSdv(
        assertion_applier.matcher(
            put,
            application_assertion=_ModeCheckerAssertionSetup(model_dir, expected_contents)
        )
    )


class _ModeCheckerAssertionSetup(ApplicationAssertionSetup[FilesMatcherModel, FilesMatcherModel]):
    def __init__(self,
                 model_dir: PathSdv,
                 expected_contents: List[FileSystemElement],
                 ):
        self._model_dir = model_dir
        self._expected_contents = expected_contents

    def get_assertion(self,
                      symbols: SymbolTable,
                      tcds: Tcds,
                      env: ApplicationEnvironment,
                      ) -> ValueAssertion[FilesMatcherModel]:
        return ModelContentsAssertion(
            self._model_dir.resolve(symbols).value_of_any_dependency(tcds),
            self._expected_contents,
        )

    def get_actual(self, model: FilesMatcherModel) -> FilesMatcherModel:
        return model
