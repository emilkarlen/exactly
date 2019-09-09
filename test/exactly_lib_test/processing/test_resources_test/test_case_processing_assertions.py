import pathlib
import unittest

from exactly_lib.test_case import error_description
from exactly_lib.util.simple_textstruct.rendering import renderer_combinators as rend_comb
from exactly_lib_test.processing.test_resources import test_case_processing_assertions as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsTestCaseReference),
        unittest.makeSuite(TestAccessorErrorMatches),
    ])


_ERROR_DESCRIPTION_OF_EMPTY_MESSAGE = error_description.of_message(rend_comb.ConstantSequenceR([]))

_ARBITRARY_FILE_REF = sut.TestCaseFileReference(
    pathlib.Path('the path'),
    pathlib.Path('the relativity root dir')
)


class TestEqualsTestCaseReference(unittest.TestCase):
    def test_matches(self):
        cases = [
            NEA('equal',
                actual=_ARBITRARY_FILE_REF,
                expected=sut.equals_test_case_reference(
                    sut.TestCaseFileReference(
                        _ARBITRARY_FILE_REF.file_path,
                        _ARBITRARY_FILE_REF.file_reference_relativity_root_dir
                    )
                ),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('default assertion/object of unexpected type',
                actual='not an ' + str(sut.TestCaseFileReference),
                expected=sut.equals_test_case_reference(_ARBITRARY_FILE_REF),
                ),
            NEA('unexpected file_path',
                actual=sut.TestCaseFileReference(
                    _ARBITRARY_FILE_REF.file_path / 'unexpected',
                    _ARBITRARY_FILE_REF.file_reference_relativity_root_dir
                )
                ,
                expected=sut.equals_test_case_reference(_ARBITRARY_FILE_REF),
                ),
            NEA('unexpected relativity root dir',
                actual=sut.TestCaseFileReference(
                    _ARBITRARY_FILE_REF.file_path,
                    _ARBITRARY_FILE_REF.file_reference_relativity_root_dir / 'unexpected'
                )
                ,
                expected=sut.equals_test_case_reference(_ARBITRARY_FILE_REF),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestAccessorErrorMatches(unittest.TestCase):
    _ERROR_INFO_WITH_DESCRIPTION = sut.ErrorInfo(error_description.of_message(rend_comb.ConstantSequenceR([])))

    def test_matches(self):
        accessor_error = sut.AccessorError(
            sut.AccessErrorType.PRE_PROCESS_ERROR,
            self._ERROR_INFO_WITH_DESCRIPTION
        )

        cases = [
            NEA('default',
                actual=accessor_error,
                expected=sut.accessor_error_matches(),
                ),
            NEA('error',
                actual=accessor_error,
                expected=sut.accessor_error_matches(error=asrt.is_(accessor_error.error)),
                ),
            NEA('error_info',
                actual=accessor_error,
                expected=sut.accessor_error_matches(error_info=asrt.is_(accessor_error.error_info)),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('default assertion/object of unexpected type',
                actual='not an ' + str(sut.AccessorError),
                expected=sut.accessor_error_matches(),
                ),
            NEA('error',
                actual=sut.AccessorError(
                    sut.AccessErrorType.PRE_PROCESS_ERROR,
                    self._ERROR_INFO_WITH_DESCRIPTION
                ),
                expected=sut.accessor_error_matches(error=asrt.equals(sut.AccessErrorType.FILE_ACCESS_ERROR)),
                ),
            NEA('error_info',
                actual=sut.AccessorError(
                    sut.AccessErrorType.PRE_PROCESS_ERROR,
                    self._ERROR_INFO_WITH_DESCRIPTION
                ),
                expected=sut.accessor_error_matches(error_info=asrt.is_none),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)
