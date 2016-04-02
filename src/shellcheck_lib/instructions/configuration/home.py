import pathlib

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from shellcheck_lib.help.program_modes.test_case.instruction_documentation import InvokationVariant, \
    InstructionDocumentation
from shellcheck_lib.instructions.utils.parse_utils import split_arguments_list_string
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib.test_case.phases.anonymous import AnonymousPhaseInstruction, ConfigurationBuilder
from shellcheck_lib.test_case.phases.result import sh
from shellcheck_lib.util.textformat.structure.structures import paras


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(InstructionDocumentation):
    def __init__(self, name: str):
        super().__init__(name)

    def single_line_description(self) -> str:
        return 'Changes the Home directory.'

    def main_description_rest(self) -> list:
        return paras('TODO')

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                'PATH',
                paras('A path that is relative the current Home Directory')),
        ]


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> AnonymousPhaseInstruction:
        arguments = split_arguments_list_string(source.instruction_argument)
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
