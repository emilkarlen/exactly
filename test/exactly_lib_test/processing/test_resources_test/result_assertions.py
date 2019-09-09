import unittest

from exactly_lib.execution.full_execution import result as full_exe_result
from exactly_lib.execution.result import ActionToCheckOutcome
from exactly_lib.processing import test_case_processing
from exactly_lib.processing.test_case_processing import ErrorInfo, AccessErrorType
from exactly_lib.section_document.source_location import SourceLocationPath
from exactly_lib.test_case import error_description
from exactly_lib.util.simple_textstruct.rendering import renderer_combinators as rend_comb
from exactly_lib_test.execution.full_execution.test_resources import result_assertions as asrt_full_exe_result
from exactly_lib_test.processing.test_resources import result_assertions as sut
from exactly_lib_test.section_document.test_resources.source_elements import ARBITRARY_SOURCE_LOCATION_PATH
from exactly_lib_test.test_case.test_resources import error_description_assertions as asrt_err_descr
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_sds
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import NIE, NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestErrorInfoMatches),
        unittest.makeSuite(TestResultMatches),
        unittest.makeSuite(TestResultIsAccessError),
    ])


_ERROR_DESCRIPTION_OF_EMPTY_MESSAGE = error_description.of_message(rend_comb.ConstantSequenceR([]))


class TestErrorInfoMatches(unittest.TestCase):
    _SECTION_NAME = 'a section name'

    def test_matches(self):
        cases = [
            NIE('default assertion',
                input_value=ErrorInfo(_ERROR_DESCRIPTION_OF_EMPTY_MESSAGE),
                expected_value=sut.error_info_matches(),
                ),
            NIE('description',
                input_value=ErrorInfo(_ERROR_DESCRIPTION_OF_EMPTY_MESSAGE),
                expected_value=sut.error_info_matches(
                    description=asrt_err_descr.matches_message()
                ),
                ),
            NIE('source location path',
                input_value=ErrorInfo(
                    _ERROR_DESCRIPTION_OF_EMPTY_MESSAGE,
                    source_location_path=ARBITRARY_SOURCE_LOCATION_PATH,
                ),
                expected_value=sut.error_info_matches(
                    source_location_path=asrt.is_instance(SourceLocationPath)
                ),
                ),
            NIE('section_name',
                input_value=ErrorInfo(
                    _ERROR_DESCRIPTION_OF_EMPTY_MESSAGE,
                    section_name=self._SECTION_NAME,
                ),
                expected_value=sut.error_info_matches(
                    section_name=asrt.equals(self._SECTION_NAME)
                ),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected_value.apply_without_message(self, case.input_value)

    def test_not_matches(self):
        cases = [
            NIE('default assertion/object of unexpected type',
                input_value='not an ErrorInfo',
                expected_value=sut.error_info_matches(),
                ),
            NIE('description',
                input_value=ErrorInfo(_ERROR_DESCRIPTION_OF_EMPTY_MESSAGE),
                expected_value=sut.error_info_matches(
                    description=asrt_err_descr.matches_exception()
                ),
                ),
            NIE('source location path',
                input_value=ErrorInfo(
                    _ERROR_DESCRIPTION_OF_EMPTY_MESSAGE,
                    source_location_path=ARBITRARY_SOURCE_LOCATION_PATH,
                ),
                expected_value=sut.error_info_matches(
                    source_location_path=asrt.is_none
                ),
                ),
            NIE('section_name',
                input_value=ErrorInfo(
                    _ERROR_DESCRIPTION_OF_EMPTY_MESSAGE,
                    section_name=self._SECTION_NAME + 'unexpected',
                ),
                expected_value=sut.error_info_matches(
                    section_name=asrt.equals(self._SECTION_NAME)
                ),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected_value, case.input_value)


_FULL_EXE_RESULT__ARBITRARY = full_exe_result.new_skipped()

_FULL_EXE_RESULT__SKIPPED = full_exe_result.new_skipped()
_FULL_EXE_RESULT__PASS = full_exe_result.new_pass(fake_sds(),
                                                  ActionToCheckOutcome(0))

_ERROR_INFO__WITH_DESCRIPTION = ErrorInfo(
    description=error_description.of_constant_message('error info message')
)


class TestResultMatches(unittest.TestCase):
    _SECTION_NAME = 'a section name'
    _AN_ACCESS_ERROR_TYPE = test_case_processing.AccessErrorType.FILE_ACCESS_ERROR

    def test_matches(self):
        cases = [
            NEA('default/skipped',
                actual=test_case_processing.new_executed(_FULL_EXE_RESULT__SKIPPED),
                expected=sut.result_matches(),
                ),
            NEA('default/pass',
                actual=test_case_processing.new_executed(_FULL_EXE_RESULT__PASS),
                expected=sut.result_matches(),
                ),
            NEA('status',
                actual=test_case_processing.new_executed(_FULL_EXE_RESULT__PASS),
                expected=sut.result_matches(status=asrt.equals(test_case_processing.Status.EXECUTED)),
                ),
            NEA('error_info',
                actual=test_case_processing.new_internal_error(_ERROR_INFO__WITH_DESCRIPTION),
                expected=sut.result_matches(error_info=asrt.is_instance(ErrorInfo)),
                ),
            NEA('access_error_type',
                actual=test_case_processing.new_access_error(self._AN_ACCESS_ERROR_TYPE,
                                                             _ERROR_INFO__WITH_DESCRIPTION),
                expected=sut.result_matches(access_error_type=asrt.is_instance(test_case_processing.AccessErrorType)),
                ),
            NEA('execution_result',
                actual=test_case_processing.new_executed(_FULL_EXE_RESULT__PASS),
                expected=sut.result_matches(execution_result=asrt.is_instance(test_case_processing.FullExeResult)),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('default/invalid type',
                actual='not a result',
                expected=sut.result_matches(),
                ),
            NEA('status',
                actual=test_case_processing.new_executed(_FULL_EXE_RESULT__PASS),
                expected=sut.result_matches(status=asrt.equals(test_case_processing.Status.ACCESS_ERROR)),
                ),
            NEA('error_info',
                actual=test_case_processing.new_internal_error(_ERROR_INFO__WITH_DESCRIPTION),
                expected=sut.result_matches(error_info=sut.error_info_matches(description=asrt.is_none)),
                ),
            NEA('access_error_type',
                actual=test_case_processing.new_access_error(test_case_processing.AccessErrorType.FILE_ACCESS_ERROR,
                                                             _ERROR_INFO__WITH_DESCRIPTION),
                expected=sut.result_matches(
                    access_error_type=asrt.is_(test_case_processing.AccessErrorType.PRE_PROCESS_ERROR)
                ),
                ),
            NEA('execution_result',
                actual=test_case_processing.new_executed(_FULL_EXE_RESULT__PASS),
                expected=sut.result_matches(execution_result=asrt_full_exe_result.is_xpass()),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestResultIsAccessError(unittest.TestCase):
    _SECTION_NAME = 'a section name'

    def test_matches(self):
        cases = [
            NEA('status',
                actual=test_case_processing.new_access_error(AccessErrorType.FILE_ACCESS_ERROR,
                                                             _ERROR_INFO__WITH_DESCRIPTION),
                expected=sut.result_is_access_error(AccessErrorType.FILE_ACCESS_ERROR),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('not an access error',
                actual=test_case_processing.new_executed(_FULL_EXE_RESULT__PASS),
                expected=sut.result_is_access_error(AccessErrorType.PRE_PROCESS_ERROR),
                ),
            NEA('unexpected access error',
                actual=test_case_processing.new_access_error(AccessErrorType.FILE_ACCESS_ERROR,
                                                             _ERROR_INFO__WITH_DESCRIPTION),
                expected=sut.result_is_access_error(AccessErrorType.PRE_PROCESS_ERROR),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)
