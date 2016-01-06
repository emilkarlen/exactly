import pathlib

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from shellcheck_lib.execution import environment_variables
from shellcheck_lib.general.textformat import parse as text_parse
from shellcheck_lib.general.textformat.structure.paragraph import single_para
from shellcheck_lib.instructions.assert_phase.utils.contents_utils import ActualFileTransformer, \
    WITH_REPLACED_ENV_VARS_OPTION, EMPTY_ARGUMENT
from shellcheck_lib.instructions.utils.parse_utils import split_arguments_list_string
from shellcheck_lib.instructions.utils.relative_path_options import REL_HOME_OPTION, REL_CWD_OPTION
from shellcheck_lib.instructions.utils.relative_path_options import REL_TMP_OPTION
from shellcheck_lib.test_case.instruction_description import InvokationVariant, Description
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from .utils import contents_utils


class TheDescription(Description):
    def __init__(self, name: str,
                 file: str):
        super().__init__(name)
        self.file = file

    def single_line_description(self) -> str:
        return 'Test the contents of {}.'.format(self.file)

    def main_description_rest(self) -> list:
        text = """\
            {} replaces all occurrences of any of the shellcheck environment variables to the name of the variable.
            (Variable values are replaced with variable names.)

            These environment variables are:

            {}.
            """.format(WITH_REPLACED_ENV_VARS_OPTION,
                       ', '.join(environment_variables.ALL_ENV_VARS))
        return text_parse.normalize_and_parse(text)

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                    '{}'.format(EMPTY_ARGUMENT),
                    single_para('%s is empty' % self.file)),
            InvokationVariant(
                    '! {}'.format(EMPTY_ARGUMENT),
                    single_para('%s is not empty' % self.file)),
            InvokationVariant(
                    '[{}] {} FILENAME'.format(WITH_REPLACED_ENV_VARS_OPTION, REL_HOME_OPTION),
                    single_para('Expects the contents of %s to equal the contents of FILE'
                                '(which is a path relative home)' % self.file)),
            InvokationVariant(
                    '[{}] {} FILENAME'.format(WITH_REPLACED_ENV_VARS_OPTION, REL_TMP_OPTION),
                    single_para('Expects the contents of %s to equal the contents of FILE'
                                '(which is a path relative the shellcheck tmp directory)' % self.file)),
            InvokationVariant(
                    '[{}] {} FILENAME'.format(WITH_REPLACED_ENV_VARS_OPTION, REL_CWD_OPTION),
                    single_para('Expects the contents of %s to equal the contents of FILE'
                                '(which is a path relative current working directory)' % self.file)),
        ]


_WITH_REPLACED_ENV_VARS_STEM_SUFFIX = '-with-replaced-env-vars.txt'


class ParserForContentsForActualValue(SingleInstructionParser):
    def __init__(self,
                 comparison_actual_value: contents_utils.ComparisonActualFile,
                 actual_value_transformer: ActualFileTransformer):
        self.comparison_actual_value = comparison_actual_value
        self.target_transformer = actual_value_transformer

    def apply(self, source: SingleInstructionParserSource) -> AssertPhaseInstruction:
        arguments = split_arguments_list_string(source.instruction_argument)
        content_instruction = contents_utils.try_parse_content(self.comparison_actual_value,
                                                               self.target_transformer,
                                                               arguments,
                                                               source)
        if content_instruction is None:
            raise SingleInstructionInvalidArgumentException(str(arguments))
        return content_instruction


class ParserForContentsForStdout(ParserForContentsForActualValue):
    def __init__(self):
        super().__init__(contents_utils.StdoutComparisonTarget(),
                         _StdXActualFileTransformerBase())


class ParserForContentsForStderr(ParserForContentsForActualValue):
    def __init__(self):
        super().__init__(contents_utils.StderrComparisonTarget(),
                         _StdXActualFileTransformerBase())


class _StdXActualFileTransformerBase(ActualFileTransformer):
    def _dst_file_path(self,
                       environment: GlobalEnvironmentForPostEdsPhase,
                       src_file_path: pathlib.Path) -> pathlib.Path:
        src_stem_name = src_file_path.stem
        directory = src_file_path.parent
        dst_base_name = src_stem_name + _WITH_REPLACED_ENV_VARS_STEM_SUFFIX
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
