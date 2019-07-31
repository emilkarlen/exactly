import unittest

from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib_test.test_case.result.test_resources import failure_details_assertions as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIsFailureMessageMatching),
        unittest.makeSuite(TestIsFailureMessageOf),
        unittest.makeSuite(TestIsException),
        unittest.makeSuite(TestIsExceptionMatching),
    ])


class TestIsFailureMessageMatching(unittest.TestCase):
    def test_matches(self):
        message_str = 'message'
        cases = [
            NEA('equals',
                expected=
                sut.is_failure_message_matching(asrt.equals(message_str)),
                actual=
                FailureDetails.new_constant_message(message_str),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('not a ' + str(FailureDetails),
                expected=
                sut.is_failure_message_matching(asrt.anything_goes()),
                actual=
                'not a ' + str(FailureDetails),
                ),
            NEA('message is absent',
                expected=
                sut.is_failure_message_matching(asrt.anything_goes()),
                actual=
                FailureDetails.new_exception(ValueError('an exception')),
                ),
            NEA('unexpected message',
                expected=
                sut.is_failure_message_matching(asrt.equals('expected')),
                actual=
                FailureDetails.new_constant_message('actual'),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestIsFailureMessageOf(unittest.TestCase):
    def test_matches(self):
        message_str = 'message'
        cases = [
            NEA('equals',
                expected=
                sut.is_failure_message_of(message_str),
                actual=
                FailureDetails.new_constant_message(message_str),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('not a ' + str(FailureDetails),
                expected=
                sut.is_failure_message_of(''),
                actual=
                'not a ' + str(FailureDetails),
                ),
            NEA('message is absent',
                expected=
                sut.is_failure_message_of(''),
                actual=
                FailureDetails.new_exception(ValueError('an exception')),
                ),
            NEA('unexpected message',
                expected=
                sut.is_failure_message_of('expected'),
                actual=
                FailureDetails.new_constant_message('actual'),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestIsException(unittest.TestCase):
    def test_matches(self):
        cases = [
            NEA('expected type of exception',
                expected=
                sut.is_exception_of_type(ValueError),
                actual=
                FailureDetails.new_exception(ValueError('an exception')),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('not a ' + str(FailureDetails),
                expected=
                sut.is_exception_of_type(ValueError),
                actual=
                'not a ' + str(FailureDetails),
                ),
            NEA('unexpected type of exception',
                expected=
                sut.is_exception_of_type(ValueError),
                actual=
                FailureDetails.new_exception(NotImplementedError('an exception')),
                ),
            NEA('exception is absent',
                expected=
                sut.is_exception_of_type(ValueError),
                actual=
                FailureDetails.new_constant_message('just a message'),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestIsExceptionMatching(unittest.TestCase):
    def test_matches(self):
        ex = ValueError('an exception')
        cases = [
            NEA('expected type of exception',
                expected=
                sut.matches_exception(asrt.is_(ex)),
                actual=
                FailureDetails.new_exception(ex),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('not a ' + str(FailureDetails),
                expected=
                sut.matches_exception(asrt.anything_goes()),
                actual=
                'not a ' + str(FailureDetails),
                ),
            NEA('unexpected type of exception',
                expected=
                sut.matches_exception(asrt.is_instance(ValueError)),
                actual=
                FailureDetails.new_exception(NotImplementedError('an exception')),
                ),
            NEA('exception is absent',
                expected=
                sut.matches_exception(asrt.is_not_none),
                actual=
                FailureDetails.new_constant_message('just a message'),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)
