from exactly_lib.processing.test_case_processing import TestCaseFileReference
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def equals_test_case_reference(expected: TestCaseFileReference) -> ValueAssertion[TestCaseFileReference]:
    return asrt.and_([
        asrt.sub_component('file_path',
                           TestCaseFileReference.file_path.fget,
                           asrt.equals(expected.file_path)
                           ),
        asrt.sub_component('file_reference_relativity_root_dir',
                           TestCaseFileReference.file_reference_relativity_root_dir.fget,
                           asrt.equals(expected.file_reference_relativity_root_dir)
                           ),
    ])
