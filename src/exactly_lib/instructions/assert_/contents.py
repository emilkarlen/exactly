import pathlib

from exactly_lib.common.instruction_documentation import InvokationVariant, \
    InstructionDocumentation
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.execution.execution_directory_structure import \
    root_dir_for_non_stdout_or_stderr_files_with_replaced_env_vars, SUB_DIR_FOR_REPLACEMENT_SOURCES_UNDER_ACT_DIR, \
    SUB_DIR_FOR_REPLACEMENT_SOURCES_NOT_UNDER_ACT_DIR, PATH__TMP_USER
from exactly_lib.instructions.assert_.utils.contents_utils import ActualFileTransformer, EMPTY_ARGUMENT, \
    WITH_REPLACED_ENV_VARS_OPTION, parse_actual_file_argument, with_replaced_env_vars_help
from exactly_lib.instructions.utils.arg_parse.parse_utils import split_arguments_list_string
from exactly_lib.instructions.utils.arg_parse.relative_path_options import REL_HOME_OPTION, REL_TMP_OPTION, \
    REL_CWD_OPTION
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase
from exactly_lib.util.textformat.structure.structures import paras
from .utils import contents_utils


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(Parser(),
                                  TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(InstructionDocumentation):
    def __init__(self, name: str):
        super().__init__(name)

    def single_line_description(self) -> str:
        return 'Tests the contents of a file.'

    def main_description_rest(self) -> list:
        return with_replaced_env_vars_help()

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                'FILENAME {}'.format(EMPTY_ARGUMENT),
                paras('File exists, is a regular file, and is empty')),
            InvokationVariant(
                'FILENAME ! {}'.format(EMPTY_ARGUMENT),
                paras('File exists, is a regular file, and is not empty')),
            InvokationVariant(
                'FILENAME {} {} FILE'.format(WITH_REPLACED_ENV_VARS_OPTION,
                                             REL_HOME_OPTION),
                paras('Compares contents of FILENAME to contents of FILE '
                      '(which is a path relative home)')),
            InvokationVariant(
                'FILENAME {} {} FILE'.format(WITH_REPLACED_ENV_VARS_OPTION,
                                             REL_TMP_OPTION),
                paras('Compares contents of FILENAME to contents of FILE '
                      '(which is a path relative the {user_tmp_dir} directory inside of the sandbox)'
                      .format(user_tmp_dir=PATH__TMP_USER))),
            InvokationVariant(
                'FILENAME {} {} FILE'.format(WITH_REPLACED_ENV_VARS_OPTION,
                                             REL_CWD_OPTION),
                paras('Compares contents of FILENAME to contents of FILE '
                      '(which is a path relative current working directory)')),
        ]


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> AssertPhaseInstruction:
        arguments = split_arguments_list_string(source.instruction_argument)
        if not arguments:
            raise SingleInstructionInvalidArgumentException('At least one argument expected (FILE)')
        (comparison_target, remaining_arguments) = parse_actual_file_argument(arguments)
        instruction = contents_utils.try_parse_content(comparison_target,
                                                       _ActualFileTransformer(),
                                                       remaining_arguments,
                                                       source)
        return instruction


class _ActualFileTransformer(ActualFileTransformer):
    def _dst_file_path(self,
                       environment: GlobalEnvironmentForPostEdsPhase,
                       src_file_path: pathlib.Path) -> pathlib.Path:
        root_dir_path = root_dir_for_non_stdout_or_stderr_files_with_replaced_env_vars(environment.eds)
        if not src_file_path.is_absolute():
            src_file_path = pathlib.Path.cwd().resolve() / src_file_path
        src_file_path = src_file_path.resolve()
        return self._dst_file_path_for_absolute_src_path(environment,
                                                         root_dir_path,
                                                         src_file_path)

    @staticmethod
    def _dst_file_path_for_absolute_src_path(environment: GlobalEnvironmentForPostEdsPhase,
                                             root_dir_path: pathlib.Path,
                                             absolute_src_file_path: pathlib.Path) -> pathlib.Path:
        try:
            relative_act_dir = absolute_src_file_path.relative_to(environment.eds.act_dir)
            # path DOES reside under act_dir
            return root_dir_path / SUB_DIR_FOR_REPLACEMENT_SOURCES_UNDER_ACT_DIR / relative_act_dir
        except ValueError:
            # path DOES NOT reside under act_dir
            return (root_dir_path / SUB_DIR_FOR_REPLACEMENT_SOURCES_NOT_UNDER_ACT_DIR).joinpath(
                *absolute_src_file_path.parts[1:])
