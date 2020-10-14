import unittest
from typing import Callable, List, Sequence, Iterator

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


def empty(put: unittest.TestCase,
          may_depend_on_external_resources: bool = False,
          ) -> ModelConstructor:
    return of_str(put, '', may_depend_on_external_resources)


def of_str(put: unittest.TestCase, contents: str,
           may_depend_on_external_resources: bool = False,
           ) -> ModelConstructor:
    return _ModelOfString(put, contents, may_depend_on_external_resources).construct


def of_str(put: unittest.TestCase, contents: str,
           may_depend_on_external_resources: bool = False,
           ) -> ModelConstructor:
    return _ModelOfString(put, contents, may_depend_on_external_resources).construct


def of_lines(put: unittest.TestCase, lines: List[str],
             may_depend_on_external_resources: bool = False,
             ) -> ModelConstructor:
    return _ModelOfLines(put, lines, may_depend_on_external_resources).construct


def of_lines__w_max_1_invocation(put: unittest.TestCase, lines: List[str],
                                 ) -> ModelConstructor:
    return _ModelOfOnlyAsLinesWithMax1Invocation(put, lines).construct


def of_lines__w_max_1_invocation__w_max_lines_from_iter(put: unittest.TestCase,
                                                        lines: List[str],
                                                        max_num_lines_from_iter: int,
                                                        ) -> ModelConstructor:
    return _ModelOfOnlyAsLinesWithMax1InvocationAndMaxNumLinesFromIter(
        put,
        lines,
        max_num_lines_from_iter,
    ).construct


def of_lines_wo_nl(put: unittest.TestCase, lines: List[str],
                   may_depend_on_external_resources: bool = False,
                   ) -> ModelConstructor:
    return _ModelOfLines(put, with_appended_new_lines(lines),
                         may_depend_on_external_resources).construct


def must_not_be_used(environment: FullResolvingEnvironment) -> StringModel:
    return MODEL_THAT_MUST_NOT_BE_USED


def arbitrary(put: unittest.TestCase,
              may_depend_on_external_resources: bool = True) -> ModelConstructor:
    return empty(put, may_depend_on_external_resources)


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


MODEL_THAT_MUST_NOT_BE_USED = string_models.string_model_that_must_not_be_used()


class _ModelOfString:
    def __init__(self,
                 put: unittest.TestCase,
                 contents: str,
                 may_depend_on_external_resources: bool = False,
                 ):
        self.put = put
        self.contents = contents
        self.may_depend_on_external_resources = may_depend_on_external_resources

    def construct(self, environment: FullResolvingEnvironment) -> StringModel:
        return StringModelThatThatChecksLines(
            self.put,
            string_models.of_string(
                self.contents,
                environment.application_environment.tmp_files_space,
                self.may_depend_on_external_resources,
            )
        )


class _ModelOfLines:
    def __init__(self,
                 put: unittest.TestCase,
                 lines: Sequence[str],
                 may_depend_on_external_resources: bool = False,
                 ):
        self.put = put
        self.lines = lines
        self.may_depend_on_external_resources = may_depend_on_external_resources

    def construct(self, environment: FullResolvingEnvironment) -> StringModel:
        return StringModelThatThatChecksLines(
            self.put,
            string_models.StringModelFromLines(
                self.lines,
                environment.application_environment.tmp_files_space.sub_dir_space(),
                self.may_depend_on_external_resources,
            )
        )


class _ModelOfOnlyAsLinesWithMax1Invocation:
    def __init__(self,
                 put: unittest.TestCase,
                 lines: Sequence[str],
                 ):
        self.put = put
        self.lines = lines
        self._as_lines_has_been_invoked = False

    def get_lines(self) -> Iterator[str]:
        if self._as_lines_has_been_invoked:
            self.put.fail('as_lines has already been invoked')

        self._as_lines_has_been_invoked = True

        return iter(self.lines)

    def construct(self, environment: FullResolvingEnvironment) -> StringModel:
        return StringModelThatThatChecksLines(
            self.put,
            string_models.StringModelThat.new_w_defaults_of_not_impl(
                as_lines=self.get_lines,
            )
        )


class _ModelOfOnlyAsLinesWithMax1InvocationAndMaxNumLinesFromIter:
    def __init__(self,
                 put: unittest.TestCase,
                 lines: Sequence[str],
                 max_num_lines_from_iter: int,
                 ):
        self.put = put
        self.lines = lines
        self._as_lines_has_been_invoked = False
        self.max_num_lines_from_iter = max_num_lines_from_iter

    def get_lines(self) -> Iterator[str]:
        if self._as_lines_has_been_invoked:
            self.put.fail('as_lines has already been invoked')

        for line_num, line_contents in enumerate(self.lines):
            if line_num == self.max_num_lines_from_iter:
                self.put.fail('Max num lines from iter exceeded, for line num ' + str(line_num + 1))
            yield line_contents

    def construct(self, environment: FullResolvingEnvironment) -> StringModel:
        return StringModelThatThatChecksLines(
            self.put,
            string_models.StringModelThat.new_w_defaults_of_not_impl(
                as_lines=self.get_lines,
            )
        )
