import unittest

from exactly_lib_test.test_case_file_structure.test_resources import home_populators
from exactly_lib_test.test_case_file_structure.test_resources.hds_utils import home_directory_structure
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.value_assertions import file_assertions as f_asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestThatPopulatorIsApplied)


class TestThatPopulatorIsApplied(unittest.TestCase):
    def test_that_populator_is_applied(self):
        # ARRANGE #
        expected_dir_contents = fs.DirContents([fs.File('file-name.txt', 'file contents')])
        populator = home_populators.case_home_dir_contents(expected_dir_contents)
        expectation = f_asrt.dir_contains_exactly(expected_dir_contents)

        # ACT #
        with home_directory_structure(contents=populator) as hds:
            # ASSERT #
            expectation.apply_with_message(self, hds.case_dir,
                                           'contents of home/case dir')
