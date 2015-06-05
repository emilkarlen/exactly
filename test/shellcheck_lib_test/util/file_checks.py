import unittest

import pathlib

from shellcheck_lib_test import test_resources


class FileChecker:
    def __init__(self,
                 put: unittest.TestCase,
                 message_header: str=None):
        self.put = put
        self.message_header = message_header

    def assert_is_existing_empty_dir(self, p: pathlib.Path):
        self.assert_exists_dir_with_given_number_of_files_in_it(p, 0)

    def assert_exists_dir_with_given_number_of_files_in_it(self,
                                                           p: pathlib.Path,
                                                           expected_number_of_files: int):
        self.assert_exists_dir(p)
        self.put.assertEquals(
            expected_number_of_files,
            len(list(p.iterdir())),
            self._msg('The directory "%s" should contain exactly %s files.' % (str(p), expected_number_of_files)))

    def assert_exists_dir(self, p: pathlib.Path):
        self.put.assertTrue(p.exists(), self._msg('"%s" should exist (as a directory)' % p.name))
        self.put.assertTrue(p.is_dir(), self._msg('"%s" should be a directory' % p.name))

    def assert_exists_plain_file(self, p: pathlib.Path):
        self.put.assertTrue(p.exists(), self._msg('"%s" should exist (as a plain file)' % p.name))
        self.put.assertTrue(p.is_file(), self._msg('"%s" should be a plain file' % p.name))

    def _msg(self, message: str) -> str:
        return test_resources.assertion_message(message, self.message_header)
