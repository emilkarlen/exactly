from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.help import texts
from exactly_lib.help.html_doc.parts.utils.entities_list_renderer import HtmlDocGeneratorForEntitiesHelp
from exactly_lib.help.html_doc.parts.utils.section_document_renderer_base import \
    HtmlDocGeneratorForSectionDocumentBase
from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation
from exactly_lib.help.program_modes.test_suite.contents import cli_syntax
from exactly_lib.help.program_modes.test_suite.contents.specification import SpecificationGenerator
from exactly_lib.help.program_modes.test_suite.contents_structure import TestSuiteHelp
from exactly_lib.help.suite_reporters.render import IndividualSuiteReporterRenderer
from exactly_lib.help.suite_reporters.suite_reporter.all_suite_reporters import ALL_SUITE_REPORTERS
from exactly_lib.help.utils.rendering import section_hierarchy_rendering
from exactly_lib.help_texts import cross_reference_id as cross_ref
from exactly_lib.help_texts.cross_reference_id import CrossReferenceId


def generator(header: str,
              test_suite_help: TestSuiteHelp) -> section_hierarchy_rendering.SectionGenerator:
    sections_helper = _HtmlDocGeneratorForTestSuiteHelp(test_suite_help)
    return section_hierarchy_rendering.parent(
        header,
        [],
        [
            ('spec',
             SpecificationGenerator('Specification of test suite functionality',
                                    test_suite_help)
             ),
            ('sections',
             sections_helper.generator_for_sections('Sections')
             ),
            ('reporters',
             HtmlDocGeneratorForEntitiesHelp('Reporters',
                                             IndividualSuiteReporterRenderer,
                                             ALL_SUITE_REPORTERS)
             ),
            ('cli-syntax',
             cli_syntax.generator(texts.COMMAND_LINE_SYNTAX)
             ),
            ('instructions',
             sections_helper.generator_for_instructions_per_section('Instructions per section')
             ),
        ]
    )


class _HtmlDocGeneratorForTestSuiteHelp(HtmlDocGeneratorForSectionDocumentBase):
    def __init__(self, test_suite_help: TestSuiteHelp):
        super().__init__(test_suite_help.section_helps)

    def _section_cross_ref_target(self, section: SectionDocumentation) -> CrossReferenceId:
        return cross_ref.TestSuiteSectionCrossReference(section.name.plain)

    def _instruction_cross_ref_target(self,
                                      instruction: InstructionDocumentation,
                                      section: SectionDocumentation) -> CrossReferenceId:
        return cross_ref.TestSuiteSectionInstructionCrossReference(
            section.name.plain,
            instruction.instruction_name())
