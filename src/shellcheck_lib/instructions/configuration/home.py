import pathlib
import shlex

from shellcheck_lib.default.execution_mode.test_case.instruction_setup import Description, InvokationVariant
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.anonymous import AnonymousPhaseInstruction, ConfigurationBuilder

DESCRIPTION = Description(
    'Changes the Home Directory',
    '',
    [InvokationVariant('PATH',
                       'A path that is relative the current Home Directory'),
     ])


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> AnonymousPhaseInstruction:
        arguments = shlex.split(source.instruction_argument)
        if len(arguments) != 1:
            msg = 'Invalid number of arguments (exactly one expected), found {}'.format(str(len(arguments)))
            raise SingleInstructionInvalidArgumentException(msg)
        return _Instruction(arguments[0])


class _Instruction(AnonymousPhaseInstruction):
    def __init__(self,
                 argument: str):
        self.argument = argument

    def main(self,
             global_environment,
             configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        new_home_dir_path = self._new_home(configuration_builder)
        if not new_home_dir_path.exists():
            return sh.new_sh_hard_error('Directory does not exist: {}'.format(new_home_dir_path))
        if not new_home_dir_path.is_dir():
            return sh.new_sh_hard_error('Not a directory: {}'.format(new_home_dir_path))
        configuration_builder.set_home_dir(new_home_dir_path.resolve())
        return sh.new_sh_success()

    def _new_home(self,
                  configuration_builder: ConfigurationBuilder) -> pathlib.Path:
        delta = pathlib.Path(self.argument)
        if delta.is_absolute():
            return delta
        return configuration_builder.home_dir_path / delta
