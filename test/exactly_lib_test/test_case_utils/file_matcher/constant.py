import pathlib
import unittest

from exactly_lib.test_case_utils.file_matcher import file_matchers as sut
from exactly_lib_test.test_case_utils.file_matcher.test_resources.file_matcher_models import \
    with_dir_space_that_must_not_be_used
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestConstant)


class TestConstant(unittest.TestCase):
    def runTest(self):
        cases = [
            NameAndValue('constant true should match any file (even if it does not exist)',
                         (
                             True,
                             pathlib.Path('file'),
                             True,
                         )),
            NameAndValue('constant false should not match any file (even if it does not exist)',
                         (
                             False,
                             pathlib.Path('file'),
                             False,
                         )),
        ]
        for case in cases:
            constant_result, path, expected_result = case.value
            with self.subTest(case_name=case.name):
                matcher = sut.FileMatcherConstant(constant_result)
                # ACT #
                actual_result_constant = matcher.result_constant

                actual_result = matcher.matches(with_dir_space_that_must_not_be_used(path))

                # ASSERT #

                self.assertIsInstance(matcher.option_description,
                                      str,
                                      'option_description')

                self.assertEqual(constant_result,
                                 actual_result_constant,
                                 'result constant')

                self.assertEqual(expected_result,
                                 actual_result,
                                 'result')
