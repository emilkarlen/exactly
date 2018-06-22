import pathlib
import unittest
from contextlib import contextmanager

from exactly_lib.test_case_utils import file_properties as sut
from exactly_lib.test_case_utils.file_properties import FileType, CheckResult, PropertiesWithNegation, \
    new_properties_for_existence
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_file, empty_dir, sym_link
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir, tmp_dir_with


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestNegationOf))
    ret_val.addTest(unittest.makeSuite(TestMustExistWhenFollowSymLinks))
    ret_val.addTest(unittest.makeSuite(TestMustExistWhenDoNotFollowSymLinks))
    ret_val.addTest(unittest.makeSuite(TestMustExistAsRegularFileWhenFollowSymLinks))
    ret_val.addTest(unittest.makeSuite(TestMustExistAsDirectoryWhenFollowSymLinks))
    ret_val.addTest(unittest.makeSuite(TestMustExistAsDirectoryWhenDoNotFollowSymLinks))
    ret_val.addTest(unittest.makeSuite(TestMustExistAsSymbolicLinkWhenDoNotFollowSymLinks))
    return ret_val


class FileCheckThatEvaluatesTo(sut.FilePropertiesCheck):
    def __init__(self, constant: bool):
        self.__constant = constant

    def apply(self, path: pathlib.Path) -> CheckResult:
        return CheckResult(self.__constant,
                           PropertiesWithNegation(False,
                                                  new_properties_for_existence(False,
                                                                               self.__constant)))


class TestCaseBase(unittest.TestCase):
    def _assert_not_negated(self,
                            check_result: CheckResult,
                            is_success: bool):
        self.assertEqual(is_success,
                         check_result.is_success, 'is_success')
        self.assertFalse(check_result.cause.is_negated, 'cause.is_negated')

    def _assert_is_negated(self,
                           check_result: CheckResult,
                           is_success: bool):
        self.assertEquals(is_success,
                          check_result.is_success, 'is_success')
        self.assertTrue(check_result.cause.is_negated, 'cause.is_negated')


class TestNegationOf(TestCaseBase):
    def test_evaluate_to_false_when_operand_evaluates_to_true(self):
        property_check = sut.negation_of(FileCheckThatEvaluatesTo(True))
        actual = property_check.apply(pathlib.Path())
        self._assert_is_negated(actual, is_success=False)

    def test_evaluate_to_true_when_operand_evaluates_to_false(self):
        property_check = sut.negation_of(FileCheckThatEvaluatesTo(False))
        self._assert_is_negated(property_check.apply(pathlib.Path()),
                                is_success=True)


class TestMustExistWhenFollowSymLinks(TestCaseBase):
    @staticmethod
    def _the_property_check() -> sut.FilePropertiesCheck:
        return sut.must_exist()

    def test_non_existing_path(self):
        property_check = self._the_property_check()
        with empty_directory() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)

    def test_with_existing_file(self):
        property_check = self._the_property_check()
        with dir_with_file() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=True)

    def test_with_existing_dir(self):
        property_check = self._the_property_check()
        with dir_with_dir() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=True)

    def test_with_symlink_to_existing_file(self):
        property_check = self._the_property_check()
        with dir_with_symlink_to_existing_file() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=True)

    def test_with_symlink_to_non_existing_file(self):
        property_check = self._the_property_check()
        with dir_with_symlink_to_non_existing_file() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)


class TestMustExistWhenDoNotFollowSymLinks(TestCaseBase):
    @staticmethod
    def _the_property_check() -> sut.FilePropertiesCheck:
        return sut.must_exist(False)

    def test_non_existing_path(self):
        property_check = self._the_property_check()
        with empty_directory() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)

    def test_with_existing_file(self):
        property_check = self._the_property_check()
        with dir_with_file() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=True)

    def test_with_existing_dir(self):
        property_check = self._the_property_check()
        with dir_with_dir() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=True)

    def test_with_symlink_to_existing_file(self):
        property_check = self._the_property_check()
        with dir_with_symlink_to_existing_file() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=True)

    def test_with_symlink_to_non_existing_file(self):
        property_check = self._the_property_check()
        with dir_with_symlink_to_non_existing_file() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=True)


class TestMustExistAsRegularFileWhenFollowSymLinks(TestCaseBase):
    def _the_property_check(self) -> sut.FilePropertiesCheck:
        return sut.must_exist_as(FileType.REGULAR)

    def test_non_existing_path(self):
        property_check = self._the_property_check()
        with empty_directory() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)

    def test_with_existing_file(self):
        property_check = self._the_property_check()
        with dir_with_file() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=True)

    def test_with_existing_dir(self):
        property_check = self._the_property_check()
        with dir_with_dir() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)

    def test_with_symlink_to_existing_file(self):
        property_check = self._the_property_check()
        with dir_with_symlink_to_existing_file() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=True)

    def test_with_symlink_to_existing_dir(self):
        property_check = self._the_property_check()
        with dir_with_symlink_to_existing_dir() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)

    def test_with_symlink_to_non_existing_file(self):
        property_check = self._the_property_check()
        with dir_with_symlink_to_non_existing_file() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)


class TestMustExistAsRegularFileWhenDoNotFollowSymLinks(TestCaseBase):
    @staticmethod
    def _the_property_check() -> sut.FilePropertiesCheck:
        return sut.must_exist_as(FileType.REGULAR, False)

    def test_non_existing_path(self):
        property_check = self._the_property_check()
        with empty_directory() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)

    def test_with_existing_file(self):
        property_check = self._the_property_check()
        with dir_with_file() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=True)

    def test_with_existing_dir(self):
        property_check = self._the_property_check()
        with dir_with_dir() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)

    def test_with_symlink_to_existing_file(self):
        property_check = self._the_property_check()
        with dir_with_symlink_to_existing_file() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)

    def test_with_symlink_to_existing_dir(self):
        property_check = self._the_property_check()
        with dir_with_symlink_to_existing_dir() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)

    def test_with_symlink_to_non_existing_file(self):
        property_check = self._the_property_check()
        with dir_with_symlink_to_non_existing_file() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)


class TestMustExistAsDirectoryWhenFollowSymLinks(TestCaseBase):
    @staticmethod
    def _the_property_check() -> sut.FilePropertiesCheck:
        return sut.must_exist_as(FileType.DIRECTORY)

    def test_non_existing_path(self):
        property_check = self._the_property_check()
        with empty_directory() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)

    def test_with_existing_file(self):
        property_check = self._the_property_check()
        with dir_with_file() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)

    def test_with_existing_dir(self):
        property_check = self._the_property_check()
        with dir_with_dir() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=True)

    def test_with_symlink_to_existing_file(self):
        property_check = self._the_property_check()
        with dir_with_symlink_to_existing_file() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)

    def test_with_symlink_to_existing_dir(self):
        property_check = self._the_property_check()
        with dir_with_symlink_to_existing_dir() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=True)

    def test_with_symlink_to_non_existing_file(self):
        property_check = self._the_property_check()
        with dir_with_symlink_to_non_existing_file() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)


class TestMustExistAsDirectoryWhenDoNotFollowSymLinks(TestCaseBase):
    @staticmethod
    def _the_property_check() -> sut.FilePropertiesCheck:
        return sut.must_exist_as(FileType.DIRECTORY, False)

    def test_non_existing_path(self):
        property_check = self._the_property_check()
        with empty_directory() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)

    def test_with_existing_file(self):
        property_check = self._the_property_check()
        with dir_with_file() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)

    def test_with_existing_dir(self):
        property_check = self._the_property_check()
        with dir_with_dir() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=True)

    def test_with_symlink_to_existing_file(self):
        property_check = self._the_property_check()
        with dir_with_symlink_to_existing_file() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)

    def test_with_symlink_to_existing_dir(self):
        property_check = self._the_property_check()
        with dir_with_symlink_to_existing_dir() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)

    def test_with_symlink_to_non_existing_file(self):
        property_check = self._the_property_check()
        with dir_with_symlink_to_non_existing_file() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)


class TestMustExistAsSymbolicLinkWhenDoNotFollowSymLinks(TestCaseBase):
    @staticmethod
    def _the_property_check() -> sut.FilePropertiesCheck:
        return sut.must_exist_as(FileType.SYMLINK, False)

    def test_non_existing_path(self):
        property_check = self._the_property_check()
        with empty_directory() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)

    def test_with_existing_file(self):
        property_check = self._the_property_check()
        with dir_with_file() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)

    def test_with_existing_dir(self):
        property_check = self._the_property_check()
        with dir_with_dir() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=False)

    def test_with_symlink_to_existing_file(self):
        property_check = self._the_property_check()
        with dir_with_symlink_to_existing_file() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=True)

    def test_with_symlink_to_existing_dir(self):
        property_check = self._the_property_check()
        with dir_with_symlink_to_existing_dir() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=True)

    def test_with_symlink_to_non_existing_file(self):
        property_check = self._the_property_check()
        with dir_with_symlink_to_non_existing_file() as file_path:
            self._assert_not_negated(property_check.apply(file_path),
                                     is_success=True)


@contextmanager
def empty_directory() -> pathlib.Path:
    with tmp_dir() as dir_path:
        yield dir_path / 'non-existing-file'


@contextmanager
def dir_with_file() -> pathlib.Path:
    with tmp_dir_with(empty_file('existing-file')) as dir_path:
        yield dir_path / 'existing-file'


@contextmanager
def dir_with_dir() -> pathlib.Path:
    with tmp_dir_with(empty_dir('existing-directory')) as dir_path:
        yield dir_path / 'existing-directory'


@contextmanager
def dir_with_symlink_to_existing_file() -> pathlib.Path:
    with tmp_dir(DirContents([empty_file('existing-file'),
                              sym_link('existing-symlink',
                                       'existing-file')])) as dir_path:
        yield dir_path / 'existing-symlink'


@contextmanager
def dir_with_symlink_to_existing_dir() -> pathlib.Path:
    with tmp_dir(DirContents([empty_dir('existing-dir'),
                              sym_link('existing-symlink',
                                       'existing-dir')])) as dir_path:
        yield dir_path / 'existing-symlink'


@contextmanager
def dir_with_symlink_to_non_existing_file() -> pathlib.Path:
    with tmp_dir_with(sym_link('symlink-to-non-existing-file',
                               'non-existing-file')) as dir_path:
        yield dir_path / 'symlink-to-non-existing-file'


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
