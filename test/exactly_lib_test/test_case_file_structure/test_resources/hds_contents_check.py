from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import RelHdsOptionType
from exactly_lib.test_case_file_structure.relative_path_options import REL_HDS_OPTIONS_MAP
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib_test.test_resources.files import file_structure
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.file_assertions import DirContainsExactly
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def dir_contains_exactly(relativity_option: RelHdsOptionType,
                         expected_contents: file_structure.DirContents
                         ) -> ValueAssertion[HomeDirectoryStructure]:
    return asrt.sub_component('relativity_option=' + str(relativity_option),
                              REL_HDS_OPTIONS_MAP[relativity_option].root_resolver.from_hds,
                              DirContainsExactly(expected_contents))


def hds_2_tcds_assertion(assertion_on_hds: ValueAssertion[HomeDirectoryStructure]
                         ) -> ValueAssertion[Tcds]:
    return asrt.sub_component('hds',
                              Tcds.hds.fget,
                              assertion_on_hds)
