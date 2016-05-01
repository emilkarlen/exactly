from exactly_lib.common.instruction_documentation import InvokationVariant, \
    InstructionDocumentation
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.execution.execution_mode import ExecutionMode, NAME_2_MODE, NAME_DEFAULT
from exactly_lib.instructions.utils.parse_utils import split_arguments_list_string
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.phases.result import sh
from exactly_lib.util.textformat.structure.structures import para


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
        from exactly_lib.help.concepts.configuration_parameters.execution_mode import \
            EXECUTION_MODE_CONFIGURATION_PARAMETER
        return 'Sets the %s.' % EXECUTION_MODE_CONFIGURATION_PARAMETER.name().singular

    def invokation_variants(self) -> list:
        from exactly_lib.help.concepts.configuration_parameters.execution_mode import execution_modes_list
        return [
            InvokationVariant(
                'MODE',
                [para('Where MODE is one of:'),
                 execution_modes_list()])
        ]

    def see_also(self) -> list:
        from exactly_lib.help.concepts.configuration_parameters.execution_mode import \
            EXECUTION_MODE_CONFIGURATION_PARAMETER
        return [EXECUTION_MODE_CONFIGURATION_PARAMETER.cross_reference_target()]


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> ConfigurationPhaseInstruction:
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


class _Instruction(ConfigurationPhaseInstruction):
    def __init__(self,
                 mode_to_set: ExecutionMode):
        self.mode_to_set = mode_to_set

    def main(self,
             global_environment,
             configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        configuration_builder.set_execution_mode(self.mode_to_set)
        return sh.new_sh_success()
