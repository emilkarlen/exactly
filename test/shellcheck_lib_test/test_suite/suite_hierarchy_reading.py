import os
import pathlib
import tempfile
import unittest

from shellcheck_lib.test_suite import structure
from shellcheck_lib.test_suite.suite_hierarchy_reading import read
from shellcheck_lib_test.instructions.utils import write_file
from shellcheck_lib_test.util.with_tmp_file import lines_content


class FileSystemElement:
    def write_to(self,
                 parent_dir_path: pathlib.Path):
        raise NotImplementedError()


class File(FileSystemElement):
    def __init__(self,
                 file_name: str,
                 contents: str):
        self.file_name = file_name
        self.contents = contents

    def write_to(self,
                 parent_dir_path: pathlib.Path):
        write_file(parent_dir_path / self.file_name,
                   self.contents)


class Dir(FileSystemElement):
    def __init__(self,
                 file_name: str,
                 file_system_element_contents: list):
        self.file_name = file_name
        self.file_system_element_contents = file_system_element_contents

    def write_to(self,
                 parent_dir_path: pathlib.Path):
        dir_path = parent_dir_path / self.file_name
        dir_path.mkdir(parents=True)
        for file_element in self.file_system_element_contents:
            file_element.write_to(dir_path)


class DirContents:
    def __init__(self,
                 file_system_element_contents: list):
        self.file_system_element_contents = file_system_element_contents

    def write_to(self,
                 dir_path: pathlib.Path):
        for file_element in self.file_system_element_contents:
            file_element.write_to(dir_path)


def write_to(dir_path: pathlib.Path,
             dir_contents: DirContents) -> DirContents:
    dir_contents.write_to(dir_path)
    return dir_contents


class TestRead(unittest.TestCase):
    def test_read_valid_hierarchy(self):
        def expected_at(root_path: pathlib.Path) -> structure.TestSuite:
            return structure.TestSuite(
                [],
                [
                    structure.TestCase(root_path / '1.case'),
                    structure.TestCase(root_path / 'sub' / '2.case')
                ])

        file_structure = DirContents([File('main.suite',
                                           lines_content(['[cases]',
                                                          '1.case',
                                                          os.path.join('sub', '2.case'),
                                                          ])),
                                      File('1.case', ''),
                                      Dir('sub',
                                          [File('2.case', '')])])
        with tempfile.TemporaryDirectory(prefix='shellcheck-test-') as tmp_dir:
            tmp_dir_path = pathlib.Path(tmp_dir)
            write_to(tmp_dir_path, file_structure)
            actual = read(tmp_dir_path / 'main.suite')
            expected = expected_at(tmp_dir_path)

            StructureEqualityChecker(self).check_suite(expected,
                                                       actual)


class StructureEqualityChecker:
    def __init__(self,
                 put: unittest.TestCase):
        self.put = put

    def check_suite(self,
                    expected: structure.TestSuite,
                    actual: structure.TestSuite):
        self.put.assertEqual(len(expected.sub_test_suites),
                             len(actual.sub_test_suites),
                             'Number of sub suites')

        self.put.assertEqual(len(expected.test_cases),
                             len(actual.test_cases),
                             'Number of cases in the suite')

        for expected_case, actual_case in zip(expected.test_cases, actual.test_cases):
            self.check_case(expected_case, actual_case)

        for expected_suite, actual_suite in zip(expected.sub_test_suites, actual.sub_test_suites):
            self.check_suite(expected_suite, actual_suite)

    def check_case(self,
                   expected: structure.TestCase,
                   actual: structure.TestCase):
        self.put.assertEqual(expected.file_path,
                             actual.file_path,
                             'File path of test case')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestRead))
    return ret_val


if __name__ == '__main__':
    unittest.main()
