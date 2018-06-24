from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.definitions.entity import conf_params
from exactly_lib.instructions.configuration.utils.hds_dir import DirConfParamInstructionDocumentationBase, \
    Parser
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.test_case_file_structure.path_relativity import RelHomeOptionType


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        parser(),
        TheInstructionDocumentation(instruction_name))


def parser() -> InstructionParser:
    return Parser(RelHomeOptionType.REL_HOME_ACT)


class TheInstructionDocumentation(DirConfParamInstructionDocumentationBase):
    def __init__(self, name: str):
        super().__init__(name, conf_params.HOME_ACT_DIRECTORY_CONF_PARAM_INFO)
