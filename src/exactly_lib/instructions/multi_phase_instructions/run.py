from typing import Tuple

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription, \
    invokation_variant_from_args
from exactly_lib.help_texts import instruction_arguments, formatting
from exactly_lib.help_texts.argument_rendering.path_syntax import the_path_of
from exactly_lib.help_texts.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.help_texts.entity import concepts, syntax_elements
from exactly_lib.instructions.multi_phase_instructions.utils import \
    instruction_from_parts_for_executing_sub_process as spe_parts
from exactly_lib.instructions.multi_phase_instructions.utils.assert_phase_info import \
    IsBothAssertionAndHelperIfInAssertPhase
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_part_utils import PartsParserFromEmbryoParser
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_parts import \
    InstructionPartsParser
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.program_info import PYTHON_INTERPRETER_WHICH_CAN_RUN_THIS_PROGRAM
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_ref_check import FileRefCheckValidator, FileRefCheck
from exactly_lib.test_case_utils.parse import parse_list, parse_executable_file
from exactly_lib.test_case_utils.parse import parse_string, parse_file_ref
from exactly_lib.test_case_utils.parse.parse_executable_file import PARSE_FILE_REF_CONFIGURATION, \
    PYTHON_EXECUTABLE_OPTION_NAME
from exactly_lib.test_case_utils.pre_or_post_validation import AndValidator, PreOrPostSdsValidator
from exactly_lib.test_case_utils.sub_proc.command_resolvers import CommandResolverForExecutableFile, \
    command_resolver_for_interpret, command_resolver_for_source_as_command_line_argument
from exactly_lib.test_case_utils.sub_proc.executable_file import ExecutableFileWithArgsResolver
from exactly_lib.test_case_utils.sub_proc.execution_setup import ValidationAndSubProcessExecutionSetupParser, \
    ValidationAndSubProcessExecutionSetup
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib.util.textformat.structure import structures as docs


def parts_parser(instruction_name: str) -> InstructionPartsParser:
    return PartsParserFromEmbryoParser(embryo_parser(instruction_name),
                                       spe_parts.ResultAndStderrTranslator())


def embryo_parser(instruction_name: str) -> spe_parts.InstructionEmbryoParser:
    return spe_parts.InstructionEmbryoParser(instruction_name,
                                             SetupParser())


REL_OPTION_ARG_CONF = PARSE_FILE_REF_CONFIGURATION

INTERPRET_OPTION_NAME = a.OptionName(long_name='interpret')
INTERPRET_OPTION = long_option_syntax(INTERPRET_OPTION_NAME.long)

SOURCE_OPTION_NAME = a.OptionName(long_name='source')
SOURCE_OPTION = long_option_syntax(SOURCE_OPTION_NAME.long)

OPTIONS_SEPARATOR_ARGUMENT = '--'

NON_ASSERT_PHASE_DESCRIPTION_REST = """\
It is considered an error if the program exits with a non-zero exit code.
"""

_SOURCE_SYNTAX_ELEMENT_NAME = 'SOURCE'


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

    def invokation_variants(self) -> list:
        return [
            invokation_variant_from_args([
                self.mandatory_executable,
                a.Single(a.Multiplicity.OPTIONAL, a.Constant(OPTIONS_SEPARATOR_ARGUMENT)),
                self.zero_or_more_generic_args],
                self._paragraphs(_EXECUTABLE_FILE)),

            invokation_variant_from_args([
                self.mandatory_executable,
                a.Single(a.Multiplicity.MANDATORY, a.Option(INTERPRET_OPTION_NAME)),
                self.mandatory_path,
                self.zero_or_more_generic_args],
                self._paragraphs(_SOURCE_FILE)),

            invokation_variant_from_args([
                self.mandatory_executable,
                a.Single(a.Multiplicity.MANDATORY, a.Option(SOURCE_OPTION_NAME)),
                a.Single(a.Multiplicity.MANDATORY, a.Named(_SOURCE_SYNTAX_ELEMENT_NAME))],
                self._paragraphs(_SOURCE_STRING)),
        ]

    def syntax_element_descriptions(self) -> list:
        executable_path_arguments = [self.mandatory_path]
        left_parenthesis = a.Single(a.Multiplicity.MANDATORY, a.Constant('('))
        right_parenthesis = a.Single(a.Multiplicity.MANDATORY, a.Constant(')'))
        executable_in_parenthesis_arguments = ([left_parenthesis] +
                                               executable_path_arguments +
                                               [self.zero_or_more_generic_args,
                                                right_parenthesis])
        python_interpreter_argument = a.Single(a.Multiplicity.MANDATORY,
                                               a.Option(PYTHON_EXECUTABLE_OPTION_NAME))
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
                                          REL_OPTION_ARG_CONF.options,
                                          docs.paras(the_path_of('an existing file.')))

    def see_also_targets(self) -> list:
        name_and_cross_ref_list = [
            syntax_elements.PATH_SYNTAX_ELEMENT,
            concepts.SHELL_SYNTAX_CONCEPT_INFO,
        ]
        return cross_reference_id_list(name_and_cross_ref_list)


class SetupParser(ValidationAndSubProcessExecutionSetupParser):
    def parse_from_token_parser(self, parser: TokenParser) -> ValidationAndSubProcessExecutionSetup:
        exe_file = parse_executable_file.parse_from_token_parser(parser)
        (validator, cmd_and_args_resolver) = _ValidatorAndArgsResolverParsing(exe_file).parse(parser)
        return ValidationAndSubProcessExecutionSetup(validator, cmd_and_args_resolver)


class _ValidatorAndArgsResolverParsing:
    def __init__(self, exe_file: ExecutableFileWithArgsResolver):
        self.exe_file = exe_file

    def parse(self, token_parser: TokenParser) -> Tuple[PreOrPostSdsValidator, CommandResolverForExecutableFile]:
        if token_parser.is_at_eol:
            return self.execute(token_parser)

        setup = {
            INTERPRET_OPTION: self.interpret,
            SOURCE_OPTION: self.source,
            OPTIONS_SEPARATOR_ARGUMENT: self.execute,
        }

        option = token_parser.consume_optional_constant_string_that_must_be_unquoted_and_equal(setup.keys())
        if option is not None:
            return setup[option](token_parser)
        else:
            return self.execute(token_parser)

    def execute(self, token_parser: TokenParser) -> Tuple[PreOrPostSdsValidator, CommandResolverForExecutableFile]:
        arguments = parse_list.parse_list_from_token_parser(token_parser)
        cmd_resolver = CommandResolverForExecutableFile(self.exe_file, arguments)
        return self.exe_file.validator, cmd_resolver

    def interpret(self, token_parser: TokenParser) -> Tuple[PreOrPostSdsValidator, CommandResolverForExecutableFile]:
        file_to_interpret = parse_file_ref.parse_file_ref_from_token_parser(parse_file_ref.ALL_REL_OPTIONS_CONFIG,
                                                                            token_parser)
        file_to_interpret_check = FileRefCheck(file_to_interpret,
                                               file_properties.must_exist_as(file_properties.FileType.REGULAR))
        validator = AndValidator((self.exe_file.validator,
                                  FileRefCheckValidator(file_to_interpret_check)))
        remaining_arguments = parse_list.parse_list_from_token_parser(token_parser)
        cmd_resolver = command_resolver_for_interpret(self.exe_file, file_to_interpret, remaining_arguments)
        return validator, cmd_resolver

    def source(self, token_parser: TokenParser) -> Tuple[PreOrPostSdsValidator, CommandResolverForExecutableFile]:
        if token_parser.is_at_eol:
            msg = 'Missing {SOURCE} argument for option {option}'.format(SOURCE=_SOURCE_SYNTAX_ELEMENT_NAME,
                                                                         option=SOURCE_OPTION)
            raise SingleInstructionInvalidArgumentException(msg)
        remaining_arguments_str = token_parser.consume_current_line_as_plain_string()
        source_resolver = parse_string.string_resolver_from_string(remaining_arguments_str.strip())
        cmd_resolver = command_resolver_for_source_as_command_line_argument(self.exe_file, source_resolver)
        return self.exe_file.validator, cmd_resolver


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
