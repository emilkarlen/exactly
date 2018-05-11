import pathlib
import unittest
from typing import Sequence

from exactly_lib.instructions.assert_.utils.file_contents.parts import contents_checkers as sut
from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import PfhHardErrorException
from exactly_lib.symbol.resolver_structure import StringTransformerResolver
from exactly_lib.symbol.restriction import ValueTypeRestriction
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case import os_services as oss
from exactly_lib.test_case_utils.err_msg.property_description import PropertyDescriptor, \
    property_descriptor_with_just_a_constant_name
from exactly_lib.test_case_utils.string_transformer.resolvers import StringTransformerConstant
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.logic.lines_transformer import StringTransformerValue, IdentityStringTransformer
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.test_case.test_resources.instruction_environment import fake_post_sds_environment
from exactly_lib_test.test_resources.execution.tmp_dir import tmp_dir
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestFileTransformerAsAssertionPart)


class TestFileTransformerAsAssertionPart(unittest.TestCase):
    the_os_services = oss.new_default()
    environment = fake_post_sds_environment()

    def test_references_of_transformer_resolver_SHOULD_be_reported(self):
        # ARRANGE #
        ref_1_info = NameAndValue('ref 1', ValueType.FILE_MATCHER)

        ref_1 = SymbolReference(ref_1_info.name,
                                ValueTypeRestriction(ref_1_info.value))

        expected_references = asrt.matches_sequence([
            asrt_sym_usage.matches_reference(asrt.equals(ref_1_info.name),
                                             is_value_type_restriction(ref_1_info.value)),
        ])

        lt_with_references = StringTransformerResolverWithReferences([ref_1])
        assertion_part = sut.FileTransformerAsAssertionPart(lt_with_references)

        # ACT #
        actual = assertion_part.references
        # ASSERT #
        expected_references.apply_without_message(self, actual)

    def test_PfhHardError_SHOULD_be_raised_WHEN_file_does_not_exist(self):
        # ARRANGE #
        transformer_resolver = StringTransformerConstant(IdentityStringTransformer())
        assertion_part = sut.FileTransformerAsAssertionPart(transformer_resolver)
        # ACT & ASSERT #
        with self.assertRaises(PfhHardErrorException):
            file_name = 'a file that does not exist'
            assertion_part.check(self.environment, self.the_os_services,
                                 'custom environment',
                                 sut.ResolvedComparisonActualFile(
                                     pathlib.Path(file_name),
                                     file_refs.rel_cwd(file_refs.constant_path_part(file_name)),
                                     FilePropertyDescriptorConstructorTestImpl(),
                                 ))

    def test_PfhHardError_SHOULD_be_raised_WHEN_file_does_exist_but_is_not_a_regular_file(self):
        # ARRANGE #
        transformer_resolver = StringTransformerConstant(IdentityStringTransformer())
        assertion_part = sut.FileTransformerAsAssertionPart(transformer_resolver)
        # ACT & ASSERT #
        with tmp_dir() as path_of_existing_directory:
            with self.assertRaises(PfhHardErrorException):
                assertion_part.check(self.environment, self.the_os_services,
                                     'custom environment',
                                     sut.ResolvedComparisonActualFile(
                                         path_of_existing_directory,
                                         file_refs.absolute_file_name(str(path_of_existing_directory)),
                                         FilePropertyDescriptorConstructorTestImpl(),
                                     )
                                     )


class StringTransformerResolverWithReferences(StringTransformerResolver):
    def __init__(self, references: Sequence[SymbolReference]):
        self._references = references

    def resolve(self, named_elements: SymbolTable) -> StringTransformerValue:
        raise NotImplementedError('should not be used in these tests')

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references


class FilePropertyDescriptorConstructorTestImpl(sut.FilePropertyDescriptorConstructor):
    def __init__(self):
        pass

    def construct_for_contents_attribute(self, contents_attribute: str) -> PropertyDescriptor:
        return property_descriptor_with_just_a_constant_name('constant property name')
