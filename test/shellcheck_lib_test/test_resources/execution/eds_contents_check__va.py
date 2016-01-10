from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib_test.test_resources import file_structure, file_checks
from shellcheck_lib_test.test_resources import value_assertion as va


def act_dir_contains_exactly(expected_contents: file_structure.DirContents) -> va.ValueAssertion:
    return va.sub_component('act dir',
                            ExecutionDirectoryStructure.act_dir.fget,
                            file_checks.DirContainsExactly__Va(expected_contents))


def tmp_user_dir_contains_exactly(expected_contents: file_structure.DirContents) -> va.ValueAssertion:
    return va.sub_component('tmp/usr dir',
                            lambda eds: eds.tmp.user_dir,
                            file_checks.DirContainsExactly__Va(expected_contents))


def tmp_internal_dir_contains_exactly(expected_contents: file_structure.DirContents) -> va.ValueAssertion:
    return va.sub_component('tmp/internal dir',
                            lambda eds: eds.tmp.internal_dir,
                            file_checks.DirContainsExactly__Va(expected_contents))


def result_dir_contains_exactly(expected_contents: file_structure.DirContents) -> va.ValueAssertion:
    return va.sub_component('result dir',
                            lambda eds: eds.result.root_dir,
                            file_checks.DirContainsExactly__Va(expected_contents))
