import pathlib
import unittest

from exactly_lib.instructions.assert_.utils.file_contents.parts import contents_checkers as sut
from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import PfhHardErrorException
from exactly_lib.named_element.named_element_usage import NamedElementReference
from exactly_lib.named_element.resolver_structure import LinesTransformerResolver
from exactly_lib.named_element.restriction import ValueTypeRestriction
from exactly_lib.test_case import os_services as oss
from exactly_lib.test_case_utils.lines_transformer.resolvers import LinesTransformerConstant
from exactly_lib.test_case_utils.lines_transformer.transformers import IdentityLinesTransformer
from exactly_lib.type_system.logic.lines_transformer import LinesTransformer
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.named_element.test_resources import resolver_structure_assertions as asrt_rs
from exactly_lib_test.named_element.test_resources.restrictions_assertions import is_value_type_restriction
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

        ref_1 = NamedElementReference(ref_1_info.name,
                                      ValueTypeRestriction(ref_1_info.value))

        expected_references = asrt.matches_sequence([
            asrt_rs.matches_reference(asrt.equals(ref_1_info.name),
                                      is_value_type_restriction(ref_1_info.value)),
        ])

        lt_with_references = LinesTransformerResolverWithReferences([ref_1])
        assertion_part = sut.FileTransformerAsAssertionPart(lt_with_references)

        # ACT #
        actual = assertion_part.references
        # ASSERT #
        expected_references.apply_without_message(self, actual)

    def test_PfhHardError_SHOULD_be_raised_WHEN_file_does_not_exist(self):
        # ARRANGE #
        transformer_resolver = LinesTransformerConstant(IdentityLinesTransformer())
        assertion_part = sut.FileTransformerAsAssertionPart(transformer_resolver)
        # ACT & ASSERT #
        with self.assertRaises(PfhHardErrorException):
            assertion_part.check(self.environment, self.the_os_services,
                                 pathlib.Path('a file that does not exist'))

    def test_PfhHardError_SHOULD_be_raised_WHEN_file_does_exist_but_is_not_a_regular_file(self):
        # ARRANGE #
        transformer_resolver = LinesTransformerConstant(IdentityLinesTransformer())
        assertion_part = sut.FileTransformerAsAssertionPart(transformer_resolver)
        # ACT & ASSERT #
        with tmp_dir() as path_of_existing_directory:
            with self.assertRaises(PfhHardErrorException):
                assertion_part.check(self.environment, self.the_os_services,
                                     path_of_existing_directory)


class LinesTransformerResolverWithReferences(LinesTransformerResolver):
    def __init__(self, references: list):
        self._references = references

    def resolve(self, named_elements: SymbolTable) -> LinesTransformer:
        raise NotImplementedError('should not be used in these tests')

    @property
    def references(self) -> list:
        return self._references
