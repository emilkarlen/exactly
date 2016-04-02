import shlex

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from shellcheck_lib.help.program_modes.test_case.instruction_documentation import InvokationVariant, \
    SyntaxElementDescription, \
    InstructionDocumentation
from shellcheck_lib.instructions.utils import executable_file
from shellcheck_lib.instructions.utils import file_properties
from shellcheck_lib.instructions.utils import parse_file_ref
from shellcheck_lib.instructions.utils import sub_process_execution
from shellcheck_lib.instructions.utils.executable_file import ExecutableFile
from shellcheck_lib.instructions.utils.file_ref import FileRef
from shellcheck_lib.instructions.utils.file_ref_check import FileRefCheckValidator, FileRefCheck
from shellcheck_lib.instructions.utils.parse_file_ref import ALL_REL_OPTIONS
from shellcheck_lib.instructions.utils.parse_utils import TokenStream
from shellcheck_lib.instructions.utils.pre_or_post_validation import PreOrPostEdsValidator, AndValidator
from shellcheck_lib.instructions.utils.sub_process_execution import ResultAndStderr, ExecuteInfo, \
    ExecutorThatStoresResultInFilesInDir, execute_and_read_stderr_if_non_zero_exitcode, result_to_sh, result_to_pfh
from shellcheck_lib.test_case.phases.common import HomeAndEds, TestCaseInstruction, PhaseLoggingPaths
from shellcheck_lib.test_case.phases.result import pfh
from shellcheck_lib.test_case.phases.result import sh
from shellcheck_lib.util.textformat import parse as paragraphs_parse
from shellcheck_lib.util.textformat.structure.structures import para, paras

INTERPRET_OPTION = '--interpret'
SOURCE_OPTION = '--source'


class TheInstructionDocumentation(InstructionDocumentation):
    def __init__(self,
                 name: str,
                 single_line_description: str):
        super().__init__(name)
        self._single_line_description = single_line_description

    def single_line_description(self) -> str:
        return self._single_line_description

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                    'EXECUTABLE [--] ARGUMENT...',
                    paragraphs_parse.normalize_and_parse(
                            """\
                            Executes the given executable with the given command line arguments.
                            The arguments are splitted according to shell syntax.
                            """)),
            InvokationVariant(
                    'EXECUTABLE %s SOURCE-FILE [--] ARGUMENT...' % INTERPRET_OPTION,
                    paragraphs_parse.normalize_and_parse(
                            """\
                            Interprets the given SOURCE-FILE using EXECUTABLE.
                            ARGUMENTS... are splitted according to shell syntax.
                            """)),
            InvokationVariant(
                    'EXECUTABLE %s SOURCE' % SOURCE_OPTION,
                    paragraphs_parse.normalize_and_parse(
                            """\
                            Interprets the given SOURCE using EXECUTABLE.
                            SOURCE is taken literary, and is given as a single argument to EXECUTABLE.
                            """)),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            SyntaxElementDescription(
                    'EXECUTABLE',
                paras('Specifies an executable program.'),
                    [
                        InvokationVariant('ABSOLUTE-PATH', [para('An absolute path.')]),
                        InvokationVariant('[{}] PATH'.format('|'.join(ALL_REL_OPTIONS)),
                                          paragraphs_parse.normalize_and_parse("""\
                                          A path that is relative the given directory
                                          under the Execution Directory Structure.""")),
                        InvokationVariant('( EXECUTABLE ARGUMENT-TO-EXECUTABLE... )',
                                          paragraphs_parse.normalize_and_parse("""\
                                          An executable program with arguments. (Must be inside parentheses.)""")),
                    ]),
            SyntaxElementDescription(
                    'SOURCE-FILE',
                    paragraphs_parse.normalize_and_parse(
                            """\
                            Specifies a plain file.
                            By default, SOURCE-FILE is assumed to be relative the home dir.

                            Other locations can be specified using %s.
                            """ % '|'.join(ALL_REL_OPTIONS)),
                    []),
        ]


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
        (exe_file, arg_tokens) = executable_file.parse(tokens)
        if arg_tokens.is_null:
            return self._execute(source, exe_file, '')
        if arg_tokens.head == INTERPRET_OPTION:
            return self._interpret(source, exe_file, arg_tokens.tail_source_or_empty_string)
        if arg_tokens.head == SOURCE_OPTION:
            return self._source(source, exe_file, arg_tokens.tail_source)
        if arg_tokens.head == '--':
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
