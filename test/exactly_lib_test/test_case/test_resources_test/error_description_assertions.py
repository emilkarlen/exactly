import unittest

from exactly_lib.test_case import error_description as err_descr
from exactly_lib.test_case.error_description import ExternalProcessError
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib_test.test_case.test_resources import error_description_assertions as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.simple_textstruct.test_resources import renderer_assertions as asrt_renderer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestMatchesMessage),
        unittest.makeSuite(TestMatchesException),
        unittest.makeSuite(TestMatchesExternalProcessError),
        unittest.makeSuite(TestIsAnyErrorDescription),
    ])


class TestMatchesMessage(unittest.TestCase):
    def test_matches(self):
        cases = [
            NEA('default',
                expected=
                sut.matches_message(),
                actual=
                err_descr.of_message(rend_comb.ConstantSequenceR([])),
                ),
            NEA('custom',
                expected=
                sut.matches_message(
                    asrt_renderer.is_renderer_of_minor_blocks(asrt.len_equals(0))
                ),
                actual=
                err_descr.of_message(rend_comb.ConstantSequenceR([])),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('default/not a message',
                expected=
                sut.matches_message(),
                actual=
                err_descr.of_exception(ValueError('an exception')),
                ),
            NEA('custom',
                expected=
                sut.matches_message(
                    message=asrt_renderer.is_renderer_of_minor_blocks(asrt.len_equals(1))
                ),
                actual=
                err_descr.of_message(rend_comb.ConstantSequenceR([])),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestMatchesException(unittest.TestCase):
    def test_matches(self):
        cases = [
            NEA('default',
                expected=
                sut.matches_exception(),
                actual=
                err_descr.of_exception(ValueError('an exception')),
                ),
            NEA('custom',
                expected=
                sut.matches_exception(
                    message=asrt_renderer.is_renderer_of_minor_blocks(asrt.len_equals(0))
                ),
                actual=
                err_descr.of_exception(ValueError('an exception'),
                                       message=rend_comb.ConstantSequenceR([])),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('default/not an exception',
                expected=
                sut.matches_exception(),
                actual=
                err_descr.of_message(rend_comb.ConstantSequenceR([])),
                ),
            NEA('custom/message',
                expected=
                sut.matches_exception(
                    message=asrt_renderer.is_renderer_of_minor_blocks(asrt.len_equals(1))
                ),
                actual=
                err_descr.of_exception(ValueError('an exception'),
                                       message=rend_comb.ConstantSequenceR([])),
                ),
            NEA('custom/exception',
                expected=
                sut.matches_exception(
                    exception=asrt.is_instance(NotImplementedError)
                ),
                actual=
                err_descr.of_exception(ValueError('an exception')),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestMatchesExternalProcessError(unittest.TestCase):
    _EPR = ExternalProcessError(1, 'output on stderr')

    def test_matches(self):
        cases = [
            NEA('default',
                expected=
                sut.matches_external_process(),
                actual=
                err_descr.of_external_process_error2(self._EPR),
                ),
            NEA('custom',
                expected=
                sut.matches_external_process(
                    message=asrt_renderer.is_renderer_of_minor_blocks(asrt.len_equals(0))
                ),
                actual=
                err_descr.of_external_process_error2(self._EPR,
                                                     message=rend_comb.ConstantSequenceR([])),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('default/not an external process error',
                expected=
                sut.matches_external_process(),
                actual=
                err_descr.of_message(rend_comb.ConstantSequenceR([])),
                ),
            NEA('custom/message',
                expected=
                sut.matches_external_process(
                    message=asrt_renderer.is_renderer_of_minor_blocks(asrt.len_equals(1))
                ),
                actual=
                err_descr.of_external_process_error2(self._EPR,
                                                     message=rend_comb.ConstantSequenceR([])),
                ),
            NEA('custom/external-process-error',
                expected=
                sut.matches_external_process(
                    external_process_error=asrt.sub_component(
                        'exit_code',
                        ExternalProcessError.exit_code.fget,
                        asrt.equals(self._EPR.exit_code + 1)
                    )
                ),
                actual=
                err_descr.of_external_process_error2(self._EPR,
                                                     message=rend_comb.ConstantSequenceR([])),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestIsAnyErrorDescription(unittest.TestCase):
    def test_matches(self):
        cases = [
            err_descr.of_message(rend_comb.ConstantSequenceR([])),
            err_descr.of_exception(ValueError('an exception')),
            err_descr.of_external_process_error2(ExternalProcessError(1, 'output on stderr')),
        ]
        for error_description in cases:
            with self.subTest(str(type(error_description))):
                sut.is_any_error_description().apply_without_message(self, error_description)

    def test_not_matches(self):
        cases = [
            NameAndValue('not a sub class of ErrorDescription',
                         'not a ErrorDescription'
                         ),
            NameAndValue('Unknown sub class of ErrorDescription',
                         ErrorDescriptionForTest()
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(sut.is_any_error_description(), case.value)


class ErrorDescriptionForTest(sut.ErrorDescription):
    def __init__(self):
        super().__init__(None)
