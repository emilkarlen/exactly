import pathlib
import unittest
from typing import Sequence

from exactly_lib.instructions.assert_.utils.file_contents.parts import contents_checkers as sut
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_utils.os_services import os_services_access as oss
from exactly_lib.test_case_utils.pfh_exception import PfhHardErrorException
from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.type_val_deps.types.string_transformer.ddv import StringTransformerDdv
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.tcfs.test_resources.paths import fake_tcds
from exactly_lib_test.test_case.test_resources.instruction_environment import fake_post_sds_environment
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir
from exactly_lib_test.type_val_deps.types.path.test_resources import described_path


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestIsExistingRegularFileAssertionPart)


class TestIsExistingRegularFileAssertionPart(unittest.TestCase):
    the_os_services = oss.new_for_current_os()
    environment = fake_post_sds_environment()

    def test_model_is_returned_WHEN_file_is_existing_regular_file(self):
        # ARRANGE #

        assertion_part = sut.IsExistingRegularFileAssertionPart()

        existing_regular_file = File.empty('regular.txt')

        with tmp_dir(DirContents([existing_regular_file])) as path_of_existing_directory:
            path_of_existing_regular_file = path_of_existing_directory / existing_regular_file.name
            path_ddv = path_ddvs.absolute_path(path_of_existing_regular_file)
            path = path_ddv.value_of_any_dependency__d(fake_tcds())
            model = sut.ComparisonActualFile(path,
                                             True)
            # ACT #

            actual = assertion_part.check(self.environment, self.the_os_services,
                                          model)
            # ASSERT #

            self.assertIs(model, actual)

    def test_PfhHardError_SHOULD_be_raised_WHEN_file_does_not_exist(self):
        # ARRANGE #
        assertion_part = sut.IsExistingRegularFileAssertionPart()
        # ACT & ASSERT #
        with self.assertRaises(PfhHardErrorException):
            path = pathlib.Path('a file that does not exist')
            assertion_part.check(self.environment, self.the_os_services,
                                 sut.ComparisonActualFile(
                                     described_path.new_primitive(path),
                                     True,
                                 ))

    def test_PfhHardError_SHOULD_be_raised_WHEN_file_does_exist_but_is_not_a_regular_file(self):
        # ARRANGE #
        assertion_part = sut.IsExistingRegularFileAssertionPart()
        # ACT & ASSERT #
        with tmp_dir() as path_of_existing_directory:
            with self.assertRaises(PfhHardErrorException):
                assertion_part.check(self.environment, self.the_os_services,
                                     sut.ComparisonActualFile(
                                         described_path.new_primitive(path_of_existing_directory),
                                         True,
                                     )
                                     )

    def test_no_exception_SHOULD_be_not_raised_WHEN_file_does_not_exist_but_file_does_not_need_to_be_verified(self):
        # ARRANGE #
        assertion_part = sut.IsExistingRegularFileAssertionPart()
        # ACT & ASSERT #
        path = pathlib.Path('a file that does not exist')
        assertion_part.check(self.environment, self.the_os_services,
                             sut.ComparisonActualFile(
                                 described_path.new_primitive(path),
                                 False,
                             ))


class StringTransformerSdvWithReferences(StringTransformerSdv):
    def __init__(self, references: Sequence[SymbolReference]):
        self._references = references

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        raise NotImplementedError('should not be used in these tests')
