import pathlib

from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
from exactly_lib_test.test_resources.value_assertions.file_assertions import _DirContainsExactly


def act_dir_contains_exactly(expected_contents: file_structure.DirContents) -> va.ValueAssertion:
    return va.sub_component('act dir',
                            SandboxDirectoryStructure.act_dir.fget,
                            _DirContainsExactly(expected_contents))


def test_case_dir_contains_exactly(expected_contents: file_structure.DirContents) -> va.ValueAssertion:
    return va.sub_component('act dir',
                            SandboxDirectoryStructure.test_case_dir.fget,
                            _DirContainsExactly(expected_contents))


def tmp_user_dir_contains_exactly(expected_contents: file_structure.DirContents) -> va.ValueAssertion:
    return va.sub_component('tmp/usr dir',
                            lambda sds: sds.tmp.user_dir,
                            _DirContainsExactly(expected_contents))


def tmp_internal_dir_contains_exactly(expected_contents: file_structure.DirContents) -> va.ValueAssertion:
    return va.sub_component('tmp/internal dir',
                            lambda sds: sds.tmp.internal_dir,
                            _DirContainsExactly(expected_contents))


def result_dir_contains_exactly(expected_contents: file_structure.DirContents) -> va.ValueAssertion:
    return va.sub_component('result dir',
                            lambda sds: sds.result.root_dir,
                            _DirContainsExactly(expected_contents))


def cwd_contains_exactly(expected_contents: file_structure.DirContents) -> va.ValueAssertion:
    return va.sub_component('result dir',
                            lambda sds: pathlib.Path().cwd(),
                            _DirContainsExactly(expected_contents))
