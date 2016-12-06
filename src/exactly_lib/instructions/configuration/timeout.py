from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help.concepts.configuration_parameters.timeout import TIMEOUT_CONFIGURATION_PARAMETER, \
    WHAT_THE_TIMEOUT_APPLIES_TO
from exactly_lib.help.utils.phase_names import phase_name_dictionary
from exactly_lib.instructions.utils.arg_parse.parse_utils import split_arguments_list_string
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.phases.result import sh
from exactly_lib.util.cli_syntax.elements import argument as a


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    _INTEGER_ARG_NAME = a.Named('INTEGER')

    def __init__(self, name: str):
        super().__init__(name, {
            'default_value_str': TIMEOUT_CONFIGURATION_PARAMETER.default_value_str(),
            'phase': phase_name_dictionary(),
        })

    def single_line_description(self) -> str:
        return self._format('Sets a timeout for the execution of instructions and the {phase[act]} phase')

    def main_description_rest(self) -> list:
        return self._paragraphs(_MAIN_DESCRIPTION_REST)

    def invokation_variants(self) -> list:
        integer_arg = a.Single(a.Multiplicity.MANDATORY,
                               self._INTEGER_ARG_NAME)
        return [
            InvokationVariant(self._cl_syntax_for_args([integer_arg])),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            SyntaxElementDescription(self._INTEGER_ARG_NAME.name,
                                     self._paragraphs('Timeout in seconds.'))
        ]

    def see_also(self) -> list:
        return [TIMEOUT_CONFIGURATION_PARAMETER.cross_reference_target()]


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> ConfigurationPhaseInstruction:
        arguments = split_arguments_list_string(source.instruction_argument)
        if len(arguments) != 1:
            msg = 'Invalid number of arguments (exactly one expected), found {}'.format(str(len(arguments)))
            raise SingleInstructionInvalidArgumentException(msg)
        argument = arguments[0]
        try:
            value = int(argument)
        except ValueError:
            raise SingleInstructionInvalidArgumentException('Not an integer: `%s`' % argument)
        if value < 0:
            raise SingleInstructionInvalidArgumentException('Timeout cannot be negative: `%s`' % argument)
        return _Instruction(value)


class _Instruction(ConfigurationPhaseInstruction):
    def __init__(self,
                 timeout: int):
        self.timeout = timeout

    def main(self, configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        configuration_builder.set_timeout_in_seconds(self.timeout)
        return sh.new_sh_success()


_MAIN_DESCRIPTION_REST = """\
Default: {default_value_str}


""" + WHAT_THE_TIMEOUT_APPLIES_TO
