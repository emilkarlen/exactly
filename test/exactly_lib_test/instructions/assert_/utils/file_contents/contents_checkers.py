import pathlib
import unittest
from typing import Sequence

from exactly_lib.instructions.assert_.utils.file_contents.parts import contents_checkers as sut
from exactly_lib.symbol.logic.string_transformer import StringTransformerResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case import os_services as oss
from exactly_lib.test_case_utils.err_msg.property_description import property_descriptor_with_just_a_constant_name
from exactly_lib.test_case_utils.pfh_exception import PfhFailException
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.impl.path import described_path_ddv
from exactly_lib.type_system.err_msg import prop_descr
from exactly_lib.type_system.err_msg.prop_descr import PropertyDescriptor
from exactly_lib.type_system.logic.string_transformer import StringTransformerValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_case.test_resources.instruction_environment import fake_post_sds_environment
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_case_utils.err_msg.test_resources import described_path
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_file
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestIsExistingRegularFileAssertionPart)


class TestIsExistingRegularFileAssertionPart(unittest.TestCase):
    the_os_services = oss.new_default()
    environment = fake_post_sds_environment()

    def test_model_is_returned_WHEN_file_is_existing_regular_file(self):
        # ARRANGE #

        assertion_part = sut.IsExistingRegularFileAssertionPart()

        existing_regular_file = empty_file('regular.txt')

        with tmp_dir(DirContents([existing_regular_file])) as path_of_existing_directory:
            path_of_existing_regular_file = path_of_existing_directory / existing_regular_file.name
            path_value = file_refs.absolute_path(path_of_existing_regular_file)
            described_path = (
                described_path_ddv.of(path_value)
                    .value_of_any_dependency(fake_tcds())
            )
            model = sut.ComparisonActualFile(described_path,
                                             FilePropertyDescriptorConstructorTestImpl(),
                                             True)
            # ACT #

            actual = assertion_part.check(self.environment, self.the_os_services,
                                          'custom environment',
                                          model)
            # ASSERT #

            self.assertIs(model, actual)

    def test_PfhFail_SHOULD_be_raised_WHEN_file_does_not_exist(self):
        # ARRANGE #
        assertion_part = sut.IsExistingRegularFileAssertionPart()
        # ACT & ASSERT #
        with self.assertRaises(PfhFailException):
            path = pathlib.Path('a file that does not exist')
            assertion_part.check(self.environment, self.the_os_services,
                                 'custom environment',
                                 sut.ComparisonActualFile(
                                     described_path.new_primitive(path),
                                     FilePropertyDescriptorConstructorTestImpl(),
                                     True,
                                 ))

    def test_PfhFail_SHOULD_be_raised_WHEN_file_does_exist_but_is_not_a_regular_file(self):
        # ARRANGE #
        assertion_part = sut.IsExistingRegularFileAssertionPart()
        # ACT & ASSERT #
        with tmp_dir() as path_of_existing_directory:
            with self.assertRaises(PfhFailException):
                assertion_part.check(self.environment, self.the_os_services,
                                     'custom environment',
                                     sut.ComparisonActualFile(
                                         described_path.new_primitive(path_of_existing_directory),
                                         FilePropertyDescriptorConstructorTestImpl(),
                                         True,
                                     )
                                     )

    def test_no_exception_SHOULD_be_not_raised_WHEN_file_does_not_exist_but_file_does_not_need_to_be_verified(self):
        # ARRANGE #
        assertion_part = sut.IsExistingRegularFileAssertionPart()
        # ACT & ASSERT #
        path = pathlib.Path('a file that does not exist')
        assertion_part.check(self.environment, self.the_os_services,
                             'custom environment',
                             sut.ComparisonActualFile(
                                 described_path.new_primitive(path),
                                 FilePropertyDescriptorConstructorTestImpl(),
                                 False,
                             ))


class StringTransformerResolverWithReferences(StringTransformerResolver):
    def __init__(self, references: Sequence[SymbolReference]):
        self._references = references

    def resolve(self, symbols: SymbolTable) -> StringTransformerValue:
        raise NotImplementedError('should not be used in these tests')

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references


class FilePropertyDescriptorConstructorTestImpl(prop_descr.FilePropertyDescriptorConstructor):
    def __init__(self):
        pass

    def construct_for_contents_attribute(self, contents_attribute: str) -> PropertyDescriptor:
        return property_descriptor_with_just_a_constant_name('constant property name')
