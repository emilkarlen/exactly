from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
from exactly_lib_test.test_resources.value_assertions.file_assertions import DirContainsExactly__Va


def act_dir_contains_exactly(expected_contents: file_structure.DirContents) -> va.ValueAssertion:
    return va.sub_component('act dir',
                            SandboxDirectoryStructure.act_dir.fget,
                            DirContainsExactly__Va(expected_contents))


def tmp_user_dir_contains_exactly(expected_contents: file_structure.DirContents) -> va.ValueAssertion:
    return va.sub_component('tmp/usr dir',
                            lambda eds: eds.tmp.user_dir,
                            DirContainsExactly__Va(expected_contents))


def tmp_internal_dir_contains_exactly(expected_contents: file_structure.DirContents) -> va.ValueAssertion:
    return va.sub_component('tmp/internal dir',
                            lambda eds: eds.tmp.internal_dir,
                            DirContainsExactly__Va(expected_contents))


def result_dir_contains_exactly(expected_contents: file_structure.DirContents) -> va.ValueAssertion:
    return va.sub_component('result dir',
                            lambda eds: eds.result.root_dir,
                            DirContainsExactly__Va(expected_contents))
