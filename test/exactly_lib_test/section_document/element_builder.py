import pathlib
import unittest
from typing import Sequence

from exactly_lib.section_document import element_builder as sut
from exactly_lib.section_document.model import ElementType
from exactly_lib.section_document.parsing_configuration import SourceLocationInfo
from exactly_lib.util.line_source import SourceLocation, single_line_sequence
from exactly_lib_test.section_document.test_resources.element_assertions import matches_section_contents_element, \
    InstructionInSection, equals_instruction_in_section, matches_instruction_info, equals_file_inclusion_chain
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.line_source_assertions import equals_line_sequence


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestBuild)


INSTRUCTION = InstructionInSection('section name')


class TestBuild(unittest.TestCase):
    def test_default_constructor_arguments(self):
        # ARRANGE #
        self._test_all_element_types(sut.SectionContentElementBuilder(SourceLocationInfo(pathlib.Path.cwd())),
                                     assertion_on_file_path=asrt.is_none,
                                     assertion_on_file_inclusion_chain=asrt.matches_sequence([]))

    def test_single_file_path_argument(self):
        # ARRANGE #
        file_path = pathlib.Path('a path')
        self._test_all_element_types(sut.SectionContentElementBuilder(
            SourceLocationInfo(pathlib.Path.cwd(),
                               file_path_rel_referrer=file_path)),
            assertion_on_file_path=asrt.equals(file_path),
            assertion_on_file_inclusion_chain=asrt.matches_sequence([]))

    def test_single_file_inclusion_chain_argument(self):
        # ARRANGE #
        file_inclusion_chain = [SourceLocation(single_line_sequence(2, 'inclusion line'),
                                               pathlib.Path('inclusion file path'))]
        self._test_all_element_types(
            sut.SectionContentElementBuilder(SourceLocationInfo(pathlib.Path.cwd(),
                                                                file_inclusion_chain=file_inclusion_chain)),
            assertion_on_file_path=asrt.is_none,
            assertion_on_file_inclusion_chain=equals_file_inclusion_chain(
                file_inclusion_chain))

    def test_file_path_and__file_inclusion_chain_arguments(self):
        # ARRANGE #
        file_path = pathlib.Path('a path')
        file_inclusion_chain = [SourceLocation(single_line_sequence(2, 'inclusion line'),
                                               pathlib.Path('inclusion file path'))]
        self._test_all_element_types(
            sut.SectionContentElementBuilder(SourceLocationInfo(pathlib.Path.cwd(),
                                                                file_path_rel_referrer=file_path,
                                                                file_inclusion_chain=file_inclusion_chain)),
            assertion_on_file_path=asrt.equals(file_path),
            assertion_on_file_inclusion_chain=equals_file_inclusion_chain(
                file_inclusion_chain))

    def _test_all_element_types(self,
                                builder: sut.SectionContentElementBuilder,
                                assertion_on_file_path: asrt.ValueAssertion[pathlib.Path],
                                assertion_on_file_inclusion_chain: asrt.ValueAssertion[Sequence[SourceLocation]]
                                ):
        # ARRANGE #
        description = 'a description'
        line_sequence = single_line_sequence(10, 'the text')
        cases = [
            NEA('empty',
                expected=matches_section_contents_element(ElementType.EMPTY,
                                                          equals_line_sequence(line_sequence),
                                                          asrt.is_none,
                                                          assertion_on_file_path,
                                                          assertion_on_file_inclusion_chain),
                actual=builder.new_empty(line_sequence)),
            NEA('comment',
                expected=matches_section_contents_element(ElementType.COMMENT,
                                                          equals_line_sequence(line_sequence),
                                                          asrt.is_none,
                                                          assertion_on_file_path,
                                                          assertion_on_file_inclusion_chain),
                actual=builder.new_comment(line_sequence)),
            NEA('instruction without description',
                expected=matches_section_contents_element(ElementType.INSTRUCTION,
                                                          equals_line_sequence(line_sequence),
                                                          matches_instruction_info(
                                                              asrt.is_none,
                                                              equals_instruction_in_section(INSTRUCTION)),
                                                          assertion_on_file_path,
                                                          assertion_on_file_inclusion_chain),
                actual=builder.new_instruction(line_sequence, INSTRUCTION, None)),
            NEA('instruction with description',
                expected=matches_section_contents_element(ElementType.INSTRUCTION,
                                                          equals_line_sequence(line_sequence),
                                                          matches_instruction_info(
                                                              asrt.equals(description),
                                                              equals_instruction_in_section(INSTRUCTION)),
                                                          assertion_on_file_path,
                                                          assertion_on_file_inclusion_chain),
                actual=builder.new_instruction(line_sequence, INSTRUCTION, description)),
        ]
        for nea in cases:
            with self.subTest(nea.name):
                # ASSERT #
                nea.expected.apply_without_message(self, nea.actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
