from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependencies, DirDependentValue
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib_test.test_case_file_structure.test_resources import dir_dep_value_assertions as asrt_dir_dep_val
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def value_matches_line_matcher(expected: ValueAssertion[LineMatcher],
                               dir_dependencies: DirDependencies = DirDependencies.NONE,
                               ) -> ValueAssertion[DirDependentValue[LineMatcher]]:
    return asrt_dir_dep_val.matches_multi_dir_dependent_value(
        dir_dependencies,
        lambda tcds: expected,
    )
