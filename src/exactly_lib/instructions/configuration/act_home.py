import pathlib

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help_texts.entity import conf_params
from exactly_lib.instructions.configuration.utils.hds_dir import DirConfParamInstructionDocumentationBase, \
    InstructionBase
from exactly_lib.instructions.configuration.utils.single_arg_utils import extract_single_eq_argument_string
from exactly_lib.section_document.element_parsers.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(DirConfParamInstructionDocumentationBase):
    def __init__(self, name: str):
        super().__init__(name, conf_params.HOME_ACT_DIRECTORY_CONF_PARAM_INFO)


class Parser(InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> ConfigurationPhaseInstruction:
        return _Instruction(extract_single_eq_argument_string(rest_of_line))


class _Instruction(InstructionBase):
    def _get_conf_param_dir(self, configuration_builder: ConfigurationBuilder) -> pathlib.Path:
        return configuration_builder.home_act_dir_path

    def _set_conf_param_dir(self,
                            configuration_builder: ConfigurationBuilder,
                            path: pathlib.Path):
        configuration_builder.set_home_act_dir(path)
