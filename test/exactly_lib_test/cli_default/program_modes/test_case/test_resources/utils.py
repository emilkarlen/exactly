import pathlib
import shutil
import unittest

from exactly_lib_test.test_resources.process import SubProcessResult


def remove_if_is_directory(actual_sds_directory: str):
    actual_sds_path = pathlib.Path(actual_sds_directory)
    if actual_sds_path.is_dir():
        shutil.rmtree(actual_sds_directory)


def get_printed_sds_or_fail(put: unittest.TestCase, actual: SubProcessResult) -> str:
    printed_lines = actual.stdout.splitlines()
    put.assertEqual(1,
                    len(printed_lines),
                    'Number of printed printed lines should be exactly 1')
    actual_sds_directory = printed_lines[0]
    return actual_sds_directory
