from typing import List, Sequence

from exactly_lib.processing.instruction_setup import TestCaseParsingSetup
from exactly_lib.processing.parse import instruction_section_element_parser as isep
from exactly_lib.processing.test_case_handling_setup import TestCaseTransformer
from exactly_lib.section_document.document_parser import SectionElementParser
from exactly_lib.section_document.element_builder import SectionContentElementBuilder
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.model import SectionContentElement, ElementType, SectionContents, \
    Instruction
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction
from exactly_lib.test_case.test_case_doc import TestCase
from exactly_lib.test_suite.instruction_set.instruction import TestSuiteInstruction
from exactly_lib.util.line_source import SourceLocation


class CaseSetupPhaseInstruction(TestSuiteInstruction):
    def __init__(self, the_instruction: Instruction):
        assert isinstance(the_instruction, SetupPhaseInstruction)
        self._the_instruction = the_instruction

    def make_case_instruction(self) -> SetupPhaseInstruction:
        return self._the_instruction


class CaseSetupPhaseInstructionParser(InstructionParser):
    def __init__(self, case_instruction_parser: InstructionParser):
        self._case_instruction_parser = case_instruction_parser

    def parse(self, source: ParseSource) -> CaseSetupPhaseInstruction:
        return CaseSetupPhaseInstruction(self._case_instruction_parser.parse(source))


class TestCaseSectionContentElementFactory:
    def __init__(self,
                 source_location: SourceLocation,
                 instruction_factory: CaseSetupPhaseInstruction,
                 description: str = None):
        self._source_location = source_location
        self._description = description
        self._instruction_factory = instruction_factory

    def make(self) -> SectionContentElement:
        element_builder = SectionContentElementBuilder(self._source_location.file_path)
        return element_builder.new_instruction(self._source_location.source,
                                               self._instruction_factory.make_case_instruction(),
                                               self._description)


class TestSuiteInstructionsForCaseSetup(TestCaseTransformer):
    def __init__(self, setup_section_instruction_elements: SectionContents):
        self.setup_section_instruction_elements = setup_section_instruction_elements
        self._setup_phase_element_factories = self._element_factories_for(setup_section_instruction_elements.elements)

    @staticmethod
    def _element_factories_for(setup_section_instruction_elements: Sequence[SectionContentElement]
                               ) -> List[TestCaseSectionContentElementFactory]:
        def factory(instruction_element: SectionContentElement) -> TestCaseSectionContentElementFactory:
            inst_factory = instruction_element.instruction_info.instruction
            assert isinstance(inst_factory, CaseSetupPhaseInstruction)

            return TestCaseSectionContentElementFactory(instruction_element.location,
                                                        inst_factory,
                                                        instruction_element.instruction_info.description)

        return [factory(instruction_element)
                for instruction_element in setup_section_instruction_elements
                if instruction_element.element_type is ElementType.INSTRUCTION
                ]

    def transform(self, test_case: TestCase) -> TestCase:
        return TestCase(
            configuration_phase=test_case.configuration_phase,
            setup_phase=self._new_setup_phase(test_case.setup_phase),
            act_phase=test_case.act_phase,
            before_assert_phase=test_case.before_assert_phase,
            assert_phase=test_case.assert_phase,
            cleanup_phase=test_case.cleanup_phase,
        )

    def _new_setup_phase(self, setup_phase: SectionContents) -> SectionContents:
        elements_from_suite = tuple([
            element_factory.make()
            for element_factory in self._setup_phase_element_factories
        ])
        return SectionContents(elements_from_suite + setup_phase.elements)


def new_setup_phase_parser(test_case_parsing_setup: TestCaseParsingSetup) -> SectionElementParser:
    return isep.section_element_parser_of(
        CaseSetupPhaseInstructionParser(
            isep.instruction_parser(test_case_parsing_setup.instruction_name_extractor_function,
                                    test_case_parsing_setup.instruction_setup.setup_instruction_set)))
