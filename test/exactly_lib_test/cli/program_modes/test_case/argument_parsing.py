import unittest

from exactly_lib.cli.program_modes import main_program_argument_parsing as sut
from exactly_lib_test.cli.test_resources.test_case_handling_setup import test_case_handling_setup
from exactly_lib_test.test_resources.file_utils import tmp_file_containing


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestCase)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TestCase(unittest.TestCase):
    def test_resolve_home_directory(self):
        # ARRANGE #
        with tmp_file_containing('') as file_path:
            argv = [str(file_path)]
            expected_home_path = file_path.parent.resolve()
            # ACT #
            result = sut.parse(test_case_handling_setup(),
                               argv, {})
        # ASSERT #
        self.assertEqual(expected_home_path,
                         result.initial_home_dir_path,
                         'Initial Home Directory')
