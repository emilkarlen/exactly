from exactly_lib.processing.test_case_processing import TestCaseFileReference, AccessorError, AccessErrorType, ErrorInfo
from exactly_lib_test.processing.test_resources import result_assertions
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def equals_test_case_reference(expected: TestCaseFileReference) -> Assertion[TestCaseFileReference]:
    return asrt.is_instance_with__many(
        TestCaseFileReference,
        [
            asrt.sub_component('file_path',
                               TestCaseFileReference.file_path.fget,
                               asrt.equals(expected.file_path)
                               ),
            asrt.sub_component('path_relativity_root_dir',
                               TestCaseFileReference.path_relativity_root_dir.fget,
                               asrt.equals(expected.path_relativity_root_dir)
                               ),
        ])


def accessor_error_matches(error: Assertion[AccessErrorType] = asrt.anything_goes(),
                           error_info: Assertion[ErrorInfo] = result_assertions.error_info_matches()
                           ) -> Assertion[AccessorError]:
    return asrt.is_instance_with__many(
        AccessorError,
        [
            asrt.sub_component('error',
                               AccessorError.error.fget,
                               asrt.is_instance_with(AccessErrorType, error)
                               ),
            asrt.sub_component('error_info',
                               AccessorError.error_info.fget,
                               asrt.is_instance_with(ErrorInfo, error_info)
                               ),
        ])
