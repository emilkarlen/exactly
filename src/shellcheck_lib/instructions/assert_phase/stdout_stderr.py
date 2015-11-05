import pathlib
import shlex

from shellcheck_lib.default.execution_mode.test_case.instruction_setup import Description, InvokationVariant
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from shellcheck_lib.execution import environment_variables
from shellcheck_lib.instructions.assert_phase.utils.contents_utils import TargetTransformer, SOURCE_REL_HOME_OPTION, \
    WITH_REPLACED_ENV_VARS_OPTION, SOURCE_REL_CWD_OPTION, EMPTY_ARGUMENT
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from .utils import contents_utils


def description(file: str) -> Description:
    return Description(
        'Test the contents of {}'.format(file),
        """
        {} replaces all occurrences of any of the shellcheck environment variables to the name of the variable.
        (Variable values are replaced with variable names.)
        These environment variables are:

        {}.
        """.format(WITH_REPLACED_ENV_VARS_OPTION,
                   ', '.join(environment_variables.ALL_ENV_VARS)),
        [
            InvokationVariant(
                '{}'.format(EMPTY_ARGUMENT),
                '%s is empty' % file),
            InvokationVariant(
                '! {}'.format(EMPTY_ARGUMENT),
                '%s is not empty' % file),
            InvokationVariant(
                '[{}] {} FILENAME'.format(WITH_REPLACED_ENV_VARS_OPTION, SOURCE_REL_HOME_OPTION),
                """Expects the contents of %s to equal the contents of FILE
                (which is a path relative home)""" % file),
            InvokationVariant(
                '[{}] {} FILENAME'.format(WITH_REPLACED_ENV_VARS_OPTION, SOURCE_REL_CWD_OPTION),
                """Expects the contents of %s to equal the contents of FILE
                (which is a path relative current working directory)""" % file),
        ])


WITH_REPLACED_ENV_VARS_STEM_SUFFIX = '-with-replaced-env-vars.txt'


class ParserForContentsForTarget(SingleInstructionParser):
    def __init__(self,
                 comparison_target: contents_utils.ComparisonTarget,
                 target_transformer: TargetTransformer):
        self.comparison_target = comparison_target
        self.target_transformer = target_transformer

    def apply(self, source: SingleInstructionParserSource) -> AssertPhaseInstruction:
        arguments = shlex.split(source.instruction_argument)
        content_instruction = contents_utils.try_parse_content(self.comparison_target,
                                                               self.target_transformer,
                                                               arguments)
        if content_instruction is None:
            raise SingleInstructionInvalidArgumentException(str(arguments))
        return content_instruction


class ParserForContentsForStdout(ParserForContentsForTarget):
    def __init__(self):
        super().__init__(contents_utils.StdoutComparisonTarget(),
                         TargetTransformerForStdOut())


class ParserForContentsForStderr(ParserForContentsForTarget):
    def __init__(self):
        super().__init__(contents_utils.StderrComparisonTarget(),
                         TargetTransformerForStdErr())


class StdXTargetTransformerBase(TargetTransformer):
    def replace_env_vars(self,
                         environment: GlobalEnvironmentForPostEdsPhase,
                         os_services: OsServices,
                         target_file_path: pathlib.Path) -> pathlib.Path:
        src_file_path = self._get_src_file_path(environment)
        dst_file_path = self._dst_file_path(environment, src_file_path)
        if dst_file_path.exists():
            return dst_file_path
        env_vars_to_replace = environment_variables.all_environment_variables(environment.home_directory,
                                                                              environment.eds)
        self._replace_env_vars_and_write_result_to_dst(env_vars_to_replace,
                                                       src_file_path,
                                                       dst_file_path)
        return dst_file_path

    def _get_src_file_path(self, environment: GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        raise NotImplementedError()

    def _dst_file_path(self,
                       environment: GlobalEnvironmentForPostEdsPhase,
                       src_file_path: pathlib.Path) -> pathlib.Path:
        src_stem_name = src_file_path.stem
        directory = src_file_path.parent
        dst_base_name = src_stem_name + WITH_REPLACED_ENV_VARS_STEM_SUFFIX
        return directory / dst_base_name

    @staticmethod
    def _replace_env_vars_and_write_result_to_dst(env_vars_to_replace: dict,
                                                  src_file_path: pathlib.Path,
                                                  dst_file_path: pathlib.Path):
        with src_file_path.open() as src_file:
            # TODO Handle reading/replacing in chunks, if file is too large to be read in one chunk
            contents = src_file.read()
        for var_name, var_value in env_vars_to_replace.items():
            contents = contents.replace(var_value, var_name)
        with open(str(dst_file_path), 'w') as dst_file:
            dst_file.write(contents)


class TargetTransformerForStdOut(StdXTargetTransformerBase):
    def _get_src_file_path(self, environment: GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        return environment.eds.result.stdout_file


class TargetTransformerForStdErr(StdXTargetTransformerBase):
    def _get_src_file_path(self, environment: GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        return environment.eds.result.stderr_file
