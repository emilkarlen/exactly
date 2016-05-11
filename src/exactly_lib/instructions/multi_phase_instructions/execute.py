import shlex

import exactly_lib.instructions.utils.arg_parse.parse_executable_file
from exactly_lib.common.instruction_documentation import InvokationVariant, \
    SyntaxElementDescription
from exactly_lib.instructions.utils import documentation_text as dt
from exactly_lib.instructions.utils import file_properties
from exactly_lib.instructions.utils import relative_path_options_documentation as rel_path_doc
from exactly_lib.instructions.utils import sub_process_execution
from exactly_lib.instructions.utils.arg_parse import parse_file_ref
from exactly_lib.instructions.utils.arg_parse.parse_executable_file import PARSE_FILE_REF_CONFIGURATION
from exactly_lib.instructions.utils.arg_parse.parse_utils import TokenStream
from exactly_lib.instructions.utils.executable_file import ExecutableFile
from exactly_lib.instructions.utils.file_ref import FileRef
from exactly_lib.instructions.utils.file_ref_check import FileRefCheckValidator, FileRefCheck
from exactly_lib.instructions.utils.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.instructions.utils.pre_or_post_validation import PreOrPostEdsValidator, AndValidator
from exactly_lib.instructions.utils.sub_process_execution import ResultAndStderr, ExecuteInfo, \
    ExecutorThatStoresResultInFilesInDir, execute_and_read_stderr_if_non_zero_exitcode, result_to_sh, result_to_pfh
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.common import HomeAndEds, TestCaseInstruction, PhaseLoggingPaths
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import sh
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.elements.argument import OptionName
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax

INTERPRET_OPTION_NAME = OptionName(long_name='interpret')
INTERPRET_OPTION = long_option_syntax(INTERPRET_OPTION_NAME.long)

SOURCE_OPTION_NAME = OptionName(long_name='source')
SOURCE_OPTION = long_option_syntax(SOURCE_OPTION_NAME.long)

OPTIONS_SEPARATOR_ARGUMENT = '--'


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self,
                 name: str,
                 single_line_description: str = 'Runs a program.'):
        self.executable_arg = a.Named('EXECUTABLE')
        super().__init__(name, {'EXECUTABLE': self.executable_arg.name})
        self.relativity_arg_path = dt.PATH_ARGUMENT
        self.mandatory_path = a.Single(a.Multiplicity.MANDATORY,
                                       dt.PATH_ARGUMENT)
        self.relativity_arg = rel_path_doc.RELATIVITY_ARGUMENT
        self.optional_relativity = a.Single(a.Multiplicity.OPTIONAL,
                                            self.relativity_arg)
        self.mandatory_executable = a.Single(a.Multiplicity.MANDATORY,
                                             self.executable_arg)
        self.generic_arg = a.Named('ARGUMENT')
        self.zero_or_more_generic_args = a.Single(a.Multiplicity.ZERO_OR_MORE,
                                                  self.generic_arg)
        self.optional_arg_sep = a.Single(a.Multiplicity.OPTIONAL,
                                         a.Constant(OPTIONS_SEPARATOR_ARGUMENT))
        self._single_line_description = single_line_description

    def single_line_description(self) -> str:
        return self._single_line_description

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(self._cl_syntax_for_args([
                self.mandatory_executable,
                self.optional_arg_sep,
                self.zero_or_more_generic_args]),
                self._paragraphs(
                    """\
                    Executes the given executable with the given command line arguments.

                    The arguments are splitted according to shell syntax.
                    """)),
            InvokationVariant(self._cl_syntax_for_args([
                self.mandatory_executable,
                a.Single(a.Multiplicity.MANDATORY, a.Option(INTERPRET_OPTION_NAME)),
                self.optional_relativity,
                self.mandatory_path,
                self.optional_arg_sep,
                self.zero_or_more_generic_args]),
                self._paragraphs(
                    """\
                    Interprets the given file using {EXECUTABLE}.

                    Arguments are splitted according to shell syntax.
                    """)),
            InvokationVariant(self._cl_syntax_for_args([
                self.mandatory_executable,
                a.Single(a.Multiplicity.MANDATORY, a.Option(SOURCE_OPTION_NAME)),
                a.Single(a.Multiplicity.MANDATORY, a.Named('SOURCE'))]),
                self._paragraphs(
                    """\
                    Interprets the given SOURCE using {EXECUTABLE}.

                    SOURCE is taken literary, and is given as a single argument to {EXECUTABLE}.
                    """)),
        ]

    def syntax_element_descriptions(self) -> list:
        executable_path_arguments = [self.optional_relativity,
                                     self.mandatory_path]
        executable_in_parenthesis_arguments = ([a.Single(a.Multiplicity.MANDATORY, a.Constant('('))] +
                                               executable_path_arguments +
                                               [self.zero_or_more_generic_args,
                                                a.Single(a.Multiplicity.MANDATORY, a.Constant(')'))])
        default_relativity_desc = rel_path_doc.default_relativity_for_rel_opt_type(
            dt.PATH_ARGUMENT.name,
            PARSE_FILE_REF_CONFIGURATION.default_option)
        return [
            SyntaxElementDescription(
                self.executable_arg.name,
                self._paragraphs('Specifies a program by giving the path to an executable file, '
                                 'and optionally also arguments to the program.'),
                [
                    InvokationVariant(self._cl_syntax_for_args(executable_path_arguments),
                                      default_relativity_desc),
                    InvokationVariant(self._cl_syntax_for_args(executable_in_parenthesis_arguments),
                                      self._paragraphs('An executable program with arguments. '
                                                       '(Must be inside parentheses.)') +
                                      default_relativity_desc),
                ]),
            rel_path_doc.relativity_syntax_element_description(self.relativity_arg_path,
                                                               PARSE_FILE_REF_CONFIGURATION.accepted_options),
        ]

    def see_also(self) -> list:
        concepts = rel_path_doc.see_also_concepts(PARSE_FILE_REF_CONFIGURATION.accepted_options)
        return [concept.cross_reference_target() for concept in concepts]


class SetupForExecutableWithArguments:
    def __init__(self,
                 instruction_source_info: sub_process_execution.InstructionSourceInfo,
                 executable: ExecutableFile):
        self.instruction_source_info = instruction_source_info
        self.__executable = executable

    def _arguments(self, home_and_eds: HomeAndEds) -> list:
        raise NotImplementedError()

    def cmd_and_args(self, home_and_eds: HomeAndEds) -> list:
        return [self.__executable.path_string(home_and_eds)] + \
               self.__executable.arguments + \
               self._arguments(home_and_eds)

    @property
    def validator(self) -> PreOrPostEdsValidator:
        return self.__executable.validator


class SetupForExecute(SetupForExecutableWithArguments):
    def __init__(self,
                 instruction_source_info: sub_process_execution.InstructionSourceInfo,
                 executable: ExecutableFile,
                 argument_list: list):
        super().__init__(instruction_source_info, executable)
        self.argument_list = argument_list

    def _arguments(self, home_and_eds: HomeAndEds) -> list:
        return self.argument_list


class SetupForInterpret(SetupForExecutableWithArguments):
    def __init__(self,
                 instruction_source_info: sub_process_execution.InstructionSourceInfo,
                 executable: ExecutableFile,
                 file_to_interpret: FileRef,
                 argument_list: list):
        super().__init__(instruction_source_info, executable)
        self.file_to_interpret = file_to_interpret
        self.argument_list = argument_list
        file_to_interpret_check = FileRefCheck(file_to_interpret,
                                               file_properties.must_exist_as(file_properties.FileType.REGULAR))
        self._validator = AndValidator((executable.validator,
                                        FileRefCheckValidator(file_to_interpret_check)))

    def _arguments(self, home_and_eds: HomeAndEds) -> list:
        return [str(self.file_to_interpret.file_path_pre_or_post_eds(home_and_eds))] + self.argument_list

    @property
    def validator(self) -> PreOrPostEdsValidator:
        return self._validator


class SetupForSource(SetupForExecutableWithArguments):
    def __init__(self,
                 instruction_source_info: sub_process_execution.InstructionSourceInfo,
                 executable: ExecutableFile,
                 source: str):
        super().__init__(instruction_source_info, executable)
        self.source = source

    def _arguments(self, home_and_eds: HomeAndEds) -> list:
        return [self.source]


def run(setup: SetupForExecutableWithArguments,
        home_and_eds: HomeAndEds,
        phase_logging_paths: PhaseLoggingPaths) -> ResultAndStderr:
    execute_info = ExecuteInfo(setup.instruction_source_info,
                               setup.cmd_and_args(home_and_eds))
    executor = ExecutorThatStoresResultInFilesInDir(is_shell=False)
    return execute_and_read_stderr_if_non_zero_exitcode(execute_info, executor, phase_logging_paths)


def run_and_return_sh(setup: SetupForExecutableWithArguments,
                      home_and_eds: HomeAndEds,
                      phase_logging_paths: PhaseLoggingPaths) -> sh.SuccessOrHardError:
    result = run(setup, home_and_eds, phase_logging_paths)
    return result_to_sh(result)


def run_and_return_pfh(setup: SetupForExecutableWithArguments,
                       home_and_eds: HomeAndEds,
                       phase_logging_paths: PhaseLoggingPaths) -> pfh.PassOrFailOrHardError:
    result = run(setup, home_and_eds, phase_logging_paths)
    return result_to_pfh(result)


class SetupParser:
    def __init__(self,
                 instruction_name: str):
        self.instruction_name = instruction_name

    def apply(self, source: SingleInstructionParserSource) -> SetupForExecutableWithArguments:
        tokens = TokenStream(source.instruction_argument)
        (exe_file, arg_tokens) = exactly_lib.instructions.utils.arg_parse.parse_executable_file.parse(tokens)
        if arg_tokens.is_null:
            return self._execute(source, exe_file, '')
        if arg_tokens.head == INTERPRET_OPTION:
            return self._interpret(source, exe_file, arg_tokens.tail_source_or_empty_string)
        if arg_tokens.head == SOURCE_OPTION:
            return self._source(source, exe_file, arg_tokens.tail_source)
        if arg_tokens.head == OPTIONS_SEPARATOR_ARGUMENT:
            return self._execute(source, exe_file, arg_tokens.tail.source)
        return self._execute(source, exe_file, arg_tokens.source)

    def _execute(self,
                 source: SingleInstructionParserSource,
                 exe_file: ExecutableFile,
                 remaining_arguments_str: str) -> SetupForExecutableWithArguments:
        return SetupForExecute(
            sub_process_execution.InstructionSourceInfo(source.line_sequence.first_line.line_number,
                                                        self.instruction_name),
            exe_file,
            shlex.split(remaining_arguments_str))

    def _interpret(self,
                   source: SingleInstructionParserSource,
                   exe_file: ExecutableFile,
                   remaining_arguments_str: str) -> SetupForExecutableWithArguments:
        remaining_arguments = shlex.split(remaining_arguments_str)
        (file_to_interpret, remaining_arguments) = parse_file_ref.parse_file_ref__list(remaining_arguments)
        return SetupForInterpret(
            sub_process_execution.InstructionSourceInfo(source.line_sequence.first_line.line_number,
                                                        self.instruction_name),
            exe_file,
            file_to_interpret,
            remaining_arguments)

    def _source(self,
                source: SingleInstructionParserSource,
                exe_file: ExecutableFile,
                remaining_arguments_str: str) -> SetupForExecutableWithArguments:
        if not remaining_arguments_str:
            raise SingleInstructionInvalidArgumentException('Missing SOURCE argument for option %s' % SOURCE_OPTION)
        return SetupForSource(
            sub_process_execution.InstructionSourceInfo(source.line_sequence.first_line.line_number,
                                                        self.instruction_name),
            exe_file,
            remaining_arguments_str)


class InstructionParser(SingleInstructionParser):
    def __init__(self,
                 instruction_name: str,
                 setup2instruction_function):
        self._setup2instruction_function = setup2instruction_function
        self.setup_parser = SetupParser(instruction_name)

    def apply(self, source: SingleInstructionParserSource) -> TestCaseInstruction:
        setup = self.setup_parser.apply(source)
        return self._setup2instruction_function(setup)
