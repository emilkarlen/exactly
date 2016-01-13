import shlex

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from shellcheck_lib.general.textformat import parse as paragraphs_parse
from shellcheck_lib.general.textformat.structure.paragraph import single_para
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
from shellcheck_lib.instructions.utils.sub_process_execution import ResultAndStderr, read_stderr_if_non_zero_exitcode, \
    failure_message_for_nonzero_status
from shellcheck_lib.test_case.instruction_description import InvokationVariant, SyntaxElementDescription, \
    Description
from shellcheck_lib.test_case.sections.common import HomeAndEds, TestCaseInstruction
from shellcheck_lib.test_case.sections.result import sh

INTERPRET_OPTION = '--interpret'
SOURCE_OPTION = '--source'


class TheDescription(Description):
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
                    single_para('Specifies an executable program.'),
                    [
                        InvokationVariant('ABSOLUTE-PATH', []),
                        InvokationVariant('[{}] PATH'.format('|'.join(ALL_REL_OPTIONS)),
                                          []),
                        InvokationVariant('( EXECUTABLE ARGUMENT-TO-EXECUTABLE... )',
                                          []),
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
        self._executable = executable

    @property
    def executable(self) -> ExecutableFile:
        return self._executable

    def execute(self, home_and_eds: HomeAndEds) -> sub_process_execution.Result:
        cmd_and_args = [self.executable.path_string(home_and_eds)] + \
                       self.executable.arguments + \
                       self._arguments(home_and_eds)
        executor = sub_process_execution.ExecutorThatLogsResultUnderPhaseDir(is_shell=False)
        return executor.apply(self.instruction_source_info,
                              home_and_eds.eds,
                              cmd_and_args)

    def _arguments(self, home_and_eds: HomeAndEds) -> list:
        raise NotImplementedError()

    @property
    def validator(self) -> PreOrPostEdsValidator:
        return self.executable.validator


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


def execute_setup_and_read_stderr_if_non_zero_exitcode(setup: SetupForExecutableWithArguments,
                                                       home_and_eds: HomeAndEds) -> ResultAndStderr:
    result = setup.execute(home_and_eds)
    return read_stderr_if_non_zero_exitcode(result)


def execute_and_return_sh(setup: SetupForExecutableWithArguments, home_and_eds: HomeAndEds) -> sh.SuccessOrHardError:
    result_and_err = execute_setup_and_read_stderr_if_non_zero_exitcode(setup,
                                                                        home_and_eds)
    result = result_and_err.result
    if not result.is_success:
        return sh.new_sh_hard_error(result.error_message)
    if result.exit_code != 0:
        return sh.new_sh_hard_error(failure_message_for_nonzero_status(result_and_err))
    return sh.new_sh_success()


class SetupParser:
    def __init__(self,
                 instruction_meta_info: sub_process_execution.InstructionMetaInfo):
        self.instruction_meta_info = instruction_meta_info

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
                sub_process_execution.InstructionSourceInfo(self.instruction_meta_info,
                                                            source.line_sequence.first_line.line_number),
                exe_file,
                shlex.split(remaining_arguments_str))

    def _interpret(self,
                   source: SingleInstructionParserSource,
                   exe_file: ExecutableFile,
                   remaining_arguments_str: str) -> SetupForExecutableWithArguments:
        remaining_arguments = shlex.split(remaining_arguments_str)
        (file_to_interpret, remaining_arguments) = parse_file_ref.parse_file_ref__list(remaining_arguments)
        return SetupForInterpret(
                sub_process_execution.InstructionSourceInfo(self.instruction_meta_info,
                                                            source.line_sequence.first_line.line_number),
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
                sub_process_execution.InstructionSourceInfo(self.instruction_meta_info,
                                                            source.line_sequence.first_line.line_number),
                exe_file,
                remaining_arguments_str)


class InstructionParser(SingleInstructionParser):
    def __init__(self,
                 instruction_meta_info: sub_process_execution.InstructionMetaInfo,
                 setup2instruction_function):
        self._setup2instruction_function = setup2instruction_function
        self.setup_parser = SetupParser(instruction_meta_info)

    def apply(self, source: SingleInstructionParserSource) -> TestCaseInstruction:
        setup = self.setup_parser.apply(source)
        return self._setup2instruction_function(setup)
