import unittest

from shellcheck_lib.cli.program_modes import main_program_argument_parsing as sut
from shellcheck_lib_test.test_resources.file_utils import tmp_file_containing


class TestCase(unittest.TestCase):
    def test_resolve_home_directory(self):
        # ARRANGE #
        with tmp_file_containing('') as file_path:
            argv = [str(file_path)]
            expected_home_path = file_path.parent.resolve()
            # ACT #
            result = sut.parse(argv, {})
        # ASSERT #
        self.assertEqual(expected_home_path,
                         result.initial_home_dir_path,
                         'Initial Home Directory')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCase))
    return ret_val


if __name__ == '__main__':
    unittest.main()
