import os
import shutil

from exactly_lib.cli.program_modes.help import arguments_for
from exactly_lib.cli.program_modes.help.request_handling.request_handler import RequestHandler
from exactly_lib.help import cross_reference_id
from exactly_lib.help.contents_structure import ApplicationHelp
from exactly_lib.help.utils.cross_reference import CrossReferenceTextConstructor
from exactly_lib.help.utils.render import SectionContentsRenderer, RenderingEnvironment
from exactly_lib.util.std import StdOutputFiles
from exactly_lib.util.textformat.formatting.text import section, paragraph_item
from exactly_lib.util.textformat.formatting.text import text
from exactly_lib.util.textformat.formatting.text.lists import list_formats_with
from exactly_lib.util.textformat.formatting.text.wrapper import Wrapper
from exactly_lib.util.textformat.structure import core


class ConsoleHelpRequestHandler(RequestHandler):
    def __init__(self,
                 application_help: ApplicationHelp,
                 section_contents_renderer: SectionContentsRenderer):
        self.application_help = application_help
        self.section_contents_renderer = section_contents_renderer

    def handle(self,
               output: StdOutputFiles):
        page_width = shutil.get_terminal_size().columns
        formatter = _formatter(page_width)
        environment = RenderingEnvironment(_cross_ref_text_constructor())
        lines = formatter.format_section_contents(self.section_contents_renderer.apply(environment))
        file = output.out
        for line in lines:
            file.write(line)
            file.write(os.linesep)


def _formatter(page_width):
    text_formatter = text.TextFormatter(HelpCrossReferenceFormatter())
    return section.Formatter(paragraph_item.Formatter(text_formatter,
                                                      Wrapper(page_width=page_width),
                                                      list_formats=list_formats_with(indent_str='  ')),
                             section_content_indent_str='   ')


class HelpCrossReferenceFormatter(text.CrossReferenceFormatter):
    def __init__(self):
        self.command_line_getter = _HelpCommandLineGetterVisitor()

    def apply(self, cross_reference: core.CrossReferenceText) -> str:
        if cross_reference.allow_rendering_of_visible_extra_target_text:
            if not isinstance(cross_reference.target, cross_reference_id.CrossReferenceId):
                raise TypeError('Encountered a cross-reference that is not an instance of ' +
                                str(cross_reference_id.CrossReferenceId))
            command_line = self.command_line_getter.visit(cross_reference.target)
            return cross_reference.title + ' (' + command_line + ')'
        else:
            return cross_reference.title


def rendering_environment() -> RenderingEnvironment:
    return RenderingEnvironment(_cross_ref_text_constructor())


def _cross_ref_text_constructor() -> CrossReferenceTextConstructor:
    return CrossReferenceTextConstructor()


class _HelpCommandLineGetterVisitor(cross_reference_id.CrossReferenceIdVisitor):
    def visit_custom(self, x: cross_reference_id.CustomCrossReferenceId):
        raise ValueError('A Custom Cross Reference IDs cannot be displayed as a command line')

    def visit_concept(self, x: cross_reference_id.ConceptCrossReferenceId):
        return _command_line_display_for_help_arguments(arguments_for.concept_single(x.concept_name))

    def visit_entity(self, x: cross_reference_id.EntityCrossReferenceId):
        return _command_line_display_for_help_arguments(arguments_for.entity_single(x.entity_type_name,
                                                                                    x.entity_name))

    def visit_test_case_phase(self, x: cross_reference_id.TestCasePhaseCrossReference):
        return _command_line_display_for_help_arguments(arguments_for.case_phase_for_name(x.phase_name))

    def visit_test_case_phase_instruction(self, x: cross_reference_id.TestCasePhaseInstructionCrossReference):
        return _command_line_display_for_help_arguments(arguments_for.case_instruction_in_phase(x.phase_name,
                                                                                                x.instruction_name))

    def visit_test_suite_section(self, x: cross_reference_id.TestSuiteSectionCrossReference):
        return _command_line_display_for_help_arguments(arguments_for.suite_section_for_name(x.section_name))

    def visit_test_suite_section_instruction(self, x: cross_reference_id.TestSuiteSectionInstructionCrossReference):
        return _command_line_display_for_help_arguments(arguments_for.suite_instruction_in_section(x.section_name,
                                                                                                   x.instruction_name))


def _command_line_display_for_help_arguments(arguments: list) -> str:
    return '>' + arguments_for.HELP + ' ' + ' '.join(arguments)
