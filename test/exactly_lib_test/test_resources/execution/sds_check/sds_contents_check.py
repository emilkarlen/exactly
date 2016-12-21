import pathlib
import types
import unittest

from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
from exactly_lib_test.test_resources.value_assertions.file_assertions import DirContainsExactly
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder


def act_dir_contains_exactly(expected_contents: file_structure.DirContents) -> va.ValueAssertion:
    return va.sub_component('act dir',
                            SandboxDirectoryStructure.act_dir.fget,
                            DirContainsExactly(expected_contents))


def test_case_dir_contains_exactly(expected_contents: file_structure.DirContents) -> va.ValueAssertion:
    return va.sub_component('act dir',
                            SandboxDirectoryStructure.test_case_dir.fget,
                            DirContainsExactly(expected_contents))


def tmp_user_dir_contains_exactly(expected_contents: file_structure.DirContents) -> va.ValueAssertion:
    return va.sub_component('tmp/usr dir',
                            lambda sds: sds.tmp.user_dir,
                            DirContainsExactly(expected_contents))


def tmp_internal_dir_contains_exactly(expected_contents: file_structure.DirContents) -> va.ValueAssertion:
    return va.sub_component('tmp/internal dir',
                            lambda sds: sds.tmp.internal_dir,
                            DirContainsExactly(expected_contents))


def result_dir_contains_exactly(expected_contents: file_structure.DirContents) -> va.ValueAssertion:
    return va.sub_component('result dir',
                            lambda sds: sds.result.root_dir,
                            DirContainsExactly(expected_contents))


def cwd_contains_exactly(expected_contents: file_structure.DirContents) -> va.ValueAssertion:
    return va.sub_component('result dir',
                            lambda sds: pathlib.Path().cwd(),
                            DirContainsExactly(expected_contents))


class SubDirOfSdsContainsExactly(va.ValueAssertion):
    def __init__(self,
                 sds__2__root_dir_path: types.FunctionType,
                 expected_contents: file_structure.DirContents,
                 description: str = 'custom sub dir of sds'):
        self._description = description
        self._expected_contents = expected_contents
        self.sds__2__root_dir_path = sds__2__root_dir_path

    def apply(self,
              put: unittest.TestCase,
              sds: SandboxDirectoryStructure,
              message_builder: MessageBuilder = MessageBuilder()):
        return va.sub_component(self._description,
                                self.sds__2__root_dir_path,
                                DirContainsExactly(self._expected_contents))
