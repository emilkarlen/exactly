from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.help import header_texts
from exactly_lib.help.contents_structure import EntityConfiguration
from exactly_lib.help.html_doc.parts.utils.section_document_renderer_base import \
    HtmlDocGeneratorForSectionDocumentBase
from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation
from exactly_lib.help.program_modes.test_suite.contents import cli_syntax
from exactly_lib.help.program_modes.test_suite.contents.specification import SpecificationHierarchyGenerator
from exactly_lib.help.program_modes.test_suite.contents_structure import TestSuiteHelp
from exactly_lib.help.program_modes.test_suite.section.render import TestSuiteSectionDocumentationRenderer
from exactly_lib.help.utils.rendering import section_hierarchy_rendering
from exactly_lib.help_texts import cross_reference_id as cross_ref
from exactly_lib.help_texts.cross_reference_id import CrossReferenceId


def generator(header: str,
              test_suite_help: TestSuiteHelp,
              suite_reporter_conf: EntityConfiguration,
              ) -> section_hierarchy_rendering.SectionHierarchyGenerator:
    sections_helper = _HtmlDocGeneratorForTestSuiteHelp(test_suite_help)
    return section_hierarchy_rendering.parent(
        header,
        [],
        [
            ('spec',
             SpecificationHierarchyGenerator('Specification of test suite functionality',
                                             test_suite_help)
             ),
            ('sections',
             sections_helper.generator_for_sections('Sections')
             ),
            ('reporters',
             suite_reporter_conf.get_hierarchy_generator('Reporters')
             ),
            ('cli-syntax',
             cli_syntax.generator(header_texts.COMMAND_LINE_SYNTAX)
             ),
            ('instructions',
             sections_helper.generator_for_instructions_per_section('Instructions per section')
             ),
        ]
    )


class _HtmlDocGeneratorForTestSuiteHelp(HtmlDocGeneratorForSectionDocumentBase):
    def __init__(self, test_suite_help: TestSuiteHelp):
        super().__init__(test_suite_help.section_helps,
                         TestSuiteSectionDocumentationRenderer)

    def _section_cross_ref_target(self, section: SectionDocumentation) -> CrossReferenceId:
        return cross_ref.TestSuiteSectionCrossReference(section.name.plain)

    def _instruction_cross_ref_target(self,
                                      instruction: InstructionDocumentation,
                                      section: SectionDocumentation) -> CrossReferenceId:
        return cross_ref.TestSuiteSectionInstructionCrossReference(
            section.name.plain,
            instruction.instruction_name())
