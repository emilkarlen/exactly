from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help_texts.entity import conf_params
from exactly_lib.help_texts.names import formatting
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.section_document.parser_implementations.misc_utils import split_arguments_list_string
from exactly_lib.test_case.execution_mode import ExecutionMode, NAME_2_MODE
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.phases.result import sh


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(InstructionDocumentationWithTextParserBase):
    def __init__(self, name: str):
        super().__init__(name, {
            'MODE': _ARG_NAME,
            'execution_mode_config_param': formatting.conf_param_(conf_params.EXECUTION_MODE_CONF_PARAM_INFO),
            'default_mode': conf_params.EXECUTION_MODE_CONF_PARAM_INFO.default_value_single_line_description,
        })

    def single_line_description(self) -> str:
        return self._format('Sets the {execution_mode_config_param}')

    def main_description_rest(self) -> list:
        return self._paragraphs('The default mode (if not changed by this instruction) is {default_mode}.')

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(_ARG_NAME, []),
        ]

    def syntax_element_descriptions(self) -> list:
        from exactly_lib.help.entities.configuration_parameters.objects.execution_mode import \
            execution_modes_list
        return [
            SyntaxElementDescription(_ARG_NAME,
                                     [execution_modes_list()])
        ]

    def see_also_targets(self) -> list:
        return [conf_params.EXECUTION_MODE_CONF_PARAM_INFO.cross_reference_target]


_ARG_NAME = 'MODE'


class Parser(InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> ConfigurationPhaseInstruction:
        arguments = split_arguments_list_string(rest_of_line)
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

    def main(self, configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        configuration_builder.set_execution_mode(self.mode_to_set)
        return sh.new_sh_success()
