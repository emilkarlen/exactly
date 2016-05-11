from exactly_lib.common.instruction_documentation import SyntaxElementDescription, InvokationVariant
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.execution.execution_mode import ExecutionMode, NAME_2_MODE, NAME_DEFAULT
from exactly_lib.help.concepts.configuration_parameters.execution_mode import EXECUTION_MODE_CONFIGURATION_PARAMETER
from exactly_lib.help.utils import formatting
from exactly_lib.instructions.utils.arg_parse.parse_utils import split_arguments_list_string
from exactly_lib.instructions.utils.instruction_documentation_with_text_parser import InstructionDocumentationWithTextParserBase
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.phases.result import sh
from exactly_lib.util.description import Description


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(InstructionDocumentationWithTextParserBase):
    def __init__(self, name: str):
        super().__init__(name, {
            'MODE': _ARG_NAME,
            'execution_mode_config_param': formatting.concept(EXECUTION_MODE_CONFIGURATION_PARAMETER.name().singular),
            'default_mode': NAME_DEFAULT,
        })

    def description(self) -> Description:
        return Description(self._text('Sets the {execution_mode_config_param}'),
                           self._paragraphs('The default mode (if not changed by this instruction) is {default_mode}.'))

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(_ARG_NAME, []),
        ]

    def syntax_element_descriptions(self) -> list:
        from exactly_lib.help.concepts.configuration_parameters.execution_mode import execution_modes_list
        return [
            SyntaxElementDescription(_ARG_NAME,
                                     [execution_modes_list()])
        ]

    def see_also(self) -> list:
        return [EXECUTION_MODE_CONFIGURATION_PARAMETER.cross_reference_target()]


_ARG_NAME = 'MODE'


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
