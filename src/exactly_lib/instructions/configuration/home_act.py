import pathlib

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.definitions.entity import conf_params
from exactly_lib.instructions.configuration.utils.hds_dir import DirConfParamInstructionDocumentationBase, \
    InstructionBase, ParserBase
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(DirConfParamInstructionDocumentationBase):
    def __init__(self, name: str):
        super().__init__(name, conf_params.HOME_ACT_DIRECTORY_CONF_PARAM_INFO)


class Parser(ParserBase):
    def _instruction_from(self,
                          relativity_root: pathlib.Path,
                          path_argument: pathlib.Path) -> ConfigurationPhaseInstruction:
        return _Instruction(relativity_root, path_argument)


class _Instruction(InstructionBase):
    def _set_conf_param_dir(self,
                            configuration_builder: ConfigurationBuilder,
                            path: pathlib.Path):
        configuration_builder.set_home_act_dir(path)
