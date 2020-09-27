from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.tcfs.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib_test.test_resources.files import file_structure
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.file_assertions import DirContainsExactly
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def dir_contains_exactly(relativity_option: RelOptionType,
                         expected_contents: file_structure.DirContents
                         ) -> ValueAssertion[TestCaseDs]:
    return asrt.sub_component('relativity_option=' + str(relativity_option),
                              REL_OPTIONS_MAP[relativity_option].root_resolver.from_tcds,
                              DirContainsExactly(expected_contents))
