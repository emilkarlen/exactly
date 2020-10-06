import unittest
from typing import Callable, List, Sequence

from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.util.str_.misc_formatting import with_appended_new_lines
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.tcfs.test_resources.paths import fake_tcds
from exactly_lib_test.test_case.test_resources.os_services_that_raises import OsServicesThatRaises
from exactly_lib_test.type_system.logic.string_model.test_resources import string_models
from exactly_lib_test.type_system.logic.string_model.test_resources.assertions import StringModelThatThatChecksLines
from exactly_lib_test.util.file_utils.test_resources import tmp_file_spaces
from exactly_lib_test.util.process_execution.test_resources.proc_exe_env import proc_exe_env_for_test

ModelConstructor = Callable[[FullResolvingEnvironment], StringModel]


def empty(put: unittest.TestCase) -> ModelConstructor:
    return of_str(put, '')


def of_str(put: unittest.TestCase, contents: str) -> ModelConstructor:
    return _ModelOfString(put, contents).construct


def of_str(put: unittest.TestCase, contents: str) -> ModelConstructor:
    return _ModelOfString(put, contents).construct


def of_lines(put: unittest.TestCase, lines: List[str]) -> ModelConstructor:
    return _ModelOfLines(put, lines).construct


def of_lines_wo_nl(put: unittest.TestCase, lines: List[str]) -> ModelConstructor:
    return _ModelOfLines(put, with_appended_new_lines(lines)).construct


def must_not_be_used(environment: FullResolvingEnvironment) -> StringModel:
    return MODEL_THAT_MUST_NOT_BE_USED


def arbitrary(put: unittest.TestCase) -> ModelConstructor:
    return empty(put)


def resolving_env_w_custom_dir_space(sds: SandboxDs) -> FullResolvingEnvironment:
    return FullResolvingEnvironment(
        SymbolTable.empty(),
        fake_tcds(),
        ApplicationEnvironment(
            OsServicesThatRaises(),
            proc_exe_env_for_test(),
            tmp_file_spaces.tmp_dir_file_space_for_test(
                sds.internal_tmp_dir / 'string-model-dir-for-test'
            )
        )
    )


MODEL_THAT_MUST_NOT_BE_USED = string_models.StringModelThatMustNotBeUsed()


class _ModelOfString:
    def __init__(self,
                 put: unittest.TestCase,
                 contents: str,
                 ):
        self.put = put
        self.contents = contents

    def construct(self, environment: FullResolvingEnvironment) -> StringModel:
        return StringModelThatThatChecksLines(
            self.put,
            string_models.of_string(
                self.contents,
                environment.application_environment.tmp_files_space.sub_dir_space(),
            )
        )


class _ModelOfLines:
    def __init__(self,
                 put: unittest.TestCase,
                 lines: Sequence[str],
                 ):
        self.put = put
        self.lines = lines

    def construct(self, environment: FullResolvingEnvironment) -> StringModel:
        return StringModelThatThatChecksLines(
            self.put,
            string_models.StringModelFromLines(
                self.lines,
                environment.application_environment.tmp_files_space.sub_dir_space(),
            )
        )
