from typing import List

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription, \
    invokation_variant_from_args
from exactly_lib.help_texts import instruction_arguments, formatting
from exactly_lib.help_texts.argument_rendering.path_syntax import the_path_of
from exactly_lib.help_texts.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.help_texts.entity import concepts, syntax_elements
from exactly_lib.instructions.multi_phase_instructions.utils import \
    instruction_from_parts_for_executing_program as spe_parts
from exactly_lib.instructions.multi_phase_instructions.utils.assert_phase_info import \
    IsBothAssertionAndHelperIfInAssertPhase
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_part_utils import PartsParserFromEmbryoParser
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_parts import \
    InstructionPartsParser
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.program_info import PYTHON_INTERPRETER_WHICH_CAN_RUN_THIS_PROGRAM
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.program.program_resolver import ProgramResolver
from exactly_lib.test_case_utils.program import syntax_elements as pgm_syntax_elements
from exactly_lib.test_case_utils.program.parse import parse_executable_file
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure import structures as docs


def parts_parser(instruction_name: str) -> InstructionPartsParser:
    return PartsParserFromEmbryoParser(embryo_parser(instruction_name),
                                       spe_parts.ResultAndStderrTranslator())


def embryo_parser(instruction_name: str) -> spe_parts.InstructionEmbryoParser:
    return spe_parts.InstructionEmbryoParser(instruction_name,
                                             program_parser())


def program_parser() -> Parser[ProgramResolver]:
    return parse_executable_file.program_parser()


NON_ASSERT_PHASE_DESCRIPTION_REST = """\
It is considered an error if the program exits with a non-zero exit code.
"""


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase,
                                  IsBothAssertionAndHelperIfInAssertPhase):
    def __init__(self,
                 name: str,
                 single_line_description: str = 'Runs a program',
                 additional_format_map: dict = None,
                 description_rest_text: str = None):
        self.description_rest_text = description_rest_text
        self.executable_arg = a.Named('EXECUTABLE')
        format_map = {
            'EXECUTABLE': self.executable_arg.name,
            'shell_syntax_concept': formatting.concept_(concepts.SHELL_SYNTAX_CONCEPT_INFO),
        }
        if additional_format_map:
            format_map.update(additional_format_map)
        super().__init__(name, format_map)
        self.relativity_arg_path = instruction_arguments.PATH_ARGUMENT
        self.mandatory_path = a.Single(a.Multiplicity.MANDATORY,
                                       instruction_arguments.PATH_ARGUMENT)
        self.optional_relativity = instruction_arguments.OPTIONAL_RELATIVITY_ARGUMENT_USAGE
        self.mandatory_executable = a.Single(a.Multiplicity.MANDATORY,
                                             self.executable_arg)
        self.generic_arg = a.Named('ARGUMENT')
        self.zero_or_more_generic_args = a.Single(a.Multiplicity.ZERO_OR_MORE,
                                                  self.generic_arg)
        self._single_line_description = single_line_description

    def single_line_description(self) -> str:
        return self._single_line_description

    def main_description_rest(self) -> list:
        if self.description_rest_text:
            return self._paragraphs(self.description_rest_text)
        return []

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            invokation_variant_from_args([
                self.mandatory_executable,
                a.Single(a.Multiplicity.OPTIONAL, a.Constant(pgm_syntax_elements.OPTIONS_SEPARATOR_ARGUMENT)),
                self.zero_or_more_generic_args],
                self._paragraphs(_EXECUTABLE_FILE)),

            invokation_variant_from_args([
                self.mandatory_executable,
                a.Single(a.Multiplicity.MANDATORY, a.Option(pgm_syntax_elements.INTERPRET_OPTION_NAME)),
                self.mandatory_path,
                self.zero_or_more_generic_args],
                self._paragraphs(_SOURCE_FILE)),

            invokation_variant_from_args([
                self.mandatory_executable,
                a.Single(a.Multiplicity.MANDATORY, a.Option(pgm_syntax_elements.SOURCE_OPTION_NAME)),
                a.Single(a.Multiplicity.MANDATORY, a.Named(pgm_syntax_elements.SOURCE_SYNTAX_ELEMENT_NAME))],
                self._paragraphs(_SOURCE_STRING)),
        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        executable_path_arguments = [self.mandatory_path]
        left_parenthesis = a.Single(a.Multiplicity.MANDATORY, a.Constant('('))
        right_parenthesis = a.Single(a.Multiplicity.MANDATORY, a.Constant(')'))
        executable_in_parenthesis_arguments = ([left_parenthesis] +
                                               executable_path_arguments +
                                               [self.zero_or_more_generic_args,
                                                right_parenthesis])
        python_interpreter_argument = a.Single(a.Multiplicity.MANDATORY,
                                               a.Option(pgm_syntax_elements.PYTHON_EXECUTABLE_OPTION_NAME))
        python_interpreter_arguments = [python_interpreter_argument]
        python_interpreter_in_parenthesis_arguments = [left_parenthesis,
                                                       python_interpreter_argument,
                                                       self.zero_or_more_generic_args,
                                                       right_parenthesis]
        return [
                   SyntaxElementDescription(
                       self.executable_arg.name,
                       self._paragraphs(_DESCRIPTION_OF_EXECUTABLE_ARG),
                       [
                           InvokationVariant(self._cl_syntax_for_args(executable_path_arguments),
                                             self._paragraphs('An executable program.')),
                           InvokationVariant(self._cl_syntax_for_args(executable_in_parenthesis_arguments),
                                             self._paragraphs('An executable program with arguments. '
                                                              '(Must be inside parentheses.)')),
                           InvokationVariant(self._cl_syntax_for_args(python_interpreter_arguments),
                                             self._paragraphs(PYTHON_INTERPRETER_WHICH_CAN_RUN_THIS_PROGRAM)),
                           InvokationVariant(self._cl_syntax_for_args(python_interpreter_in_parenthesis_arguments),
                                             self._paragraphs(PYTHON_INTERPRETER_WHICH_CAN_RUN_THIS_PROGRAM +
                                                              ' (Must be inside parentheses.)')),
                       ])
               ] + \
               rel_path_doc.path_elements(self.relativity_arg_path.name,
                                          pgm_syntax_elements.REL_OPTION_ARG_CONF.options,
                                          docs.paras(the_path_of('an existing file.')))

    def see_also_targets(self) -> list:
        name_and_cross_ref_list = [
            syntax_elements.PATH_SYNTAX_ELEMENT,
            concepts.SHELL_SYNTAX_CONCEPT_INFO,
        ]
        return cross_reference_id_list(name_and_cross_ref_list)


_DESCRIPTION_OF_EXECUTABLE_ARG = """\
Specifies a program by giving the path to an executable file,
and optionally also arguments to the executable.


Elements uses {shell_syntax_concept}.
"""

_EXECUTABLE_FILE = """\
Executes the given executable with the given command line arguments.

The arguments are splitted according to {shell_syntax_concept}.
"""

_SOURCE_FILE = """\
Interprets the given source file using {EXECUTABLE}.

Arguments are splitted according to {shell_syntax_concept}.
"""

_SOURCE_STRING = """\
Interprets the given source string using {EXECUTABLE}.

SOURCE is taken literary, and is given as a single argument to {EXECUTABLE}.
"""
