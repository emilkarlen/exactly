from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.path_relativity import RelHdsOptionType
from exactly_lib.tcfs.relative_path_options import REL_HDS_OPTIONS_MAP
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib_test.test_resources.files import file_structure
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.file_assertions import DirContainsExactly
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def dir_contains_exactly(relativity_option: RelHdsOptionType,
                         expected_contents: file_structure.DirContents
                         ) -> ValueAssertion[HomeDs]:
    return asrt.sub_component('relativity_option=' + str(relativity_option),
                              REL_HDS_OPTIONS_MAP[relativity_option].root_resolver.from_hds,
                              DirContainsExactly(expected_contents))


def hds_2_tcds_assertion(assertion_on_hds: ValueAssertion[HomeDs]
                         ) -> ValueAssertion[TestCaseDs]:
    return asrt.sub_component('hds',
                              TestCaseDs.hds.fget,
                              assertion_on_hds)
