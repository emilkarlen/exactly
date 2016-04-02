from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from shellcheck_lib.execution.execution_mode import ExecutionMode, NAME_2_MODE, NAME_DEFAULT
from shellcheck_lib.help.program_modes.test_case.instruction_documentation import InvokationVariant, \
    InstructionDocumentation
from shellcheck_lib.instructions.utils.parse_utils import split_arguments_list_string
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib.test_case.phases.anonymous import AnonymousPhaseInstruction, ConfigurationBuilder
from shellcheck_lib.test_case.phases.result import sh
from shellcheck_lib.util.textformat.structure.structures import para


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(InstructionDocumentation):
    def __init__(self, name: str):
        super().__init__(name)

    def main_description_rest(self) -> list:
        return [para('The default mode (of not set by this instruction) is %s.' % NAME_DEFAULT)]

    def single_line_description(self) -> str:
        from shellcheck_lib.help.concepts.configuration_parameters.configuration_parameter import EXECUTION_MODE_CONCEPT
        return 'Sets the %s.' % EXECUTION_MODE_CONCEPT.name().singular

    def invokation_variants(self) -> list:
        from shellcheck_lib.help.concepts.configuration_parameters.configuration_parameter import execution_modes_list
        return [
            InvokationVariant(
                'MODE',
                [para('Where MODE is one of:'),
                 execution_modes_list()])
        ]


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> AnonymousPhaseInstruction:
        arguments = split_arguments_list_string(source.instruction_argument)
        if len(arguments) != 1:
            msg = 'Invalid number of arguments (exactly one expected), found {}'.format(str(len(arguments)))
            raise SingleInstructionInvalidArgumentException(msg)
        argument = arguments[0].upper()
        try:
            target = NAME_2_MODE[argument]
        except KeyError:
            raise SingleInstructionInvalidArgumentException('Invalid mode: `%s`' % arguments[0])
        return _Instruction(target)


class _Instruction(AnonymousPhaseInstruction):
    def __init__(self,
                 mode_to_set: ExecutionMode):
        self.mode_to_set = mode_to_set

    def main(self,
             global_environment,
             configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        configuration_builder.set_execution_mode(self.mode_to_set)
        return sh.new_sh_success()
