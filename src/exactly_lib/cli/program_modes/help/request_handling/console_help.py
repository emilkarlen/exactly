import os
import shutil
from typing import Sequence

from exactly_lib.cli.definitions.program_modes.help import arguments_for
from exactly_lib.cli.definitions.program_modes.help import command_line_options as clo
from exactly_lib.cli.program_modes.help.request_handling.request_handler import RequestHandler
from exactly_lib.definitions.cross_ref import concrete_cross_refs
from exactly_lib.definitions.cross_ref.concrete_cross_refs import PredefinedHelpContentsPartReference
from exactly_lib.help.contents_structure.application import ApplicationHelp
from exactly_lib.help.render.cross_reference import CrossReferenceTextConstructor
from exactly_lib.util.file_utils.std import StdOutputFiles
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.section import \
    SectionContentsConstructor
from exactly_lib.util.textformat.rendering.text import section, paragraph_item
from exactly_lib.util.textformat.rendering.text import text
from exactly_lib.util.textformat.rendering.text.lists import list_formats_with
from exactly_lib.util.textformat.rendering.text.wrapper import Wrapper
from exactly_lib.util.textformat.structure import core
from exactly_lib.util.textformat.structure.core import UrlCrossReferenceTarget


class ConsoleHelpRequestHandler(RequestHandler):
    def __init__(self,
                 application_help: ApplicationHelp,
                 section_contents_constructor: SectionContentsConstructor):
        self.application_help = application_help
        self.section_contents_constructor = section_contents_constructor

    def handle(self, output: StdOutputFiles):
        page_width = shutil.get_terminal_size().columns
        formatter = _formatter(page_width)
        environment = ConstructionEnvironment(_cross_ref_text_constructor(),
                                              construct_simple_header_value_lists_as_tables=True)
        lines = formatter.format_section_contents(self.section_contents_constructor.apply(environment))
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
        title = cross_reference.title_text.value
        if cross_reference.allow_rendering_of_visible_extra_target_text:
            command_line = self.command_line_getter.visit(cross_reference.target)
            return title + ' (' + command_line + ')'
        else:
            return title


def construction_environment() -> ConstructionEnvironment:
    return ConstructionEnvironment(_cross_ref_text_constructor())


def _cross_ref_text_constructor() -> CrossReferenceTextConstructor:
    return CrossReferenceTextConstructor()


class _HelpCommandLineGetterVisitor(concrete_cross_refs.CrossReferenceIdVisitor):
    def visit_custom(self, x: concrete_cross_refs.CustomCrossReferenceId):
        raise ValueError('A Custom Cross Reference IDs cannot be displayed as a command line')

    def visit_url(self, x: UrlCrossReferenceTarget):
        return x.url

    def visit_entity(self, x: concrete_cross_refs.EntityCrossReferenceId):
        return _command_line_display_for_help_arguments(arguments_for.entity_single(x.entity_type_identifier,
                                                                                    x.entity_name))

    def visit_test_case_phase(self, x: concrete_cross_refs.TestCasePhaseCrossReference):
        return _command_line_display_for_help_arguments(arguments_for.case_phase_for_name(x.phase_name))

    def visit_test_case_phase_instruction(self, x: concrete_cross_refs.TestCasePhaseInstructionCrossReference):
        return _command_line_display_for_help_arguments(arguments_for.case_instruction_in_phase(x.phase_name,
                                                                                                x.instruction_name))

    def visit_test_suite_section(self, x: concrete_cross_refs.TestSuiteSectionCrossReference):
        return _command_line_display_for_help_arguments(arguments_for.suite_section_for_name(x.section_name))

    def visit_test_suite_section_instruction(self, x: concrete_cross_refs.TestSuiteSectionInstructionCrossReference):
        return _command_line_display_for_help_arguments(arguments_for.suite_instruction_in_section(x.section_name,
                                                                                                   x.instruction_name))

    def visit_predefined_part(self, x: PredefinedHelpContentsPartReference):
        return _command_line_display_for_help_arguments(arguments_for.ARGUMENTS_FOR_PART[x.part]())


def _command_line_display_for_help_arguments(arguments: Sequence[str]) -> str:
    return '>' + clo.HELP + ' ' + ' '.join(arguments)
