from typing import Dict

from exactly_lib.help.contents_structure.entity import EntityTypeConfiguration
from exactly_lib.help.program_modes.main_program.contents_structure import MainProgramHelp
from exactly_lib.help.program_modes.test_case.contents_structure.test_case_help import TestCaseHelp
from exactly_lib.help.program_modes.test_suite.contents_structure.test_suite_help import TestSuiteHelp


class ApplicationHelp(tuple):
    def __new__(cls,
                main_program_help: MainProgramHelp,
                test_case_help: TestCaseHelp,
                test_suite_help: TestSuiteHelp,
                entity_type_id_2_entity_type_configuration: Dict[str, EntityTypeConfiguration]):
        return tuple.__new__(cls, (main_program_help,
                                   test_case_help,
                                   test_suite_help,
                                   entity_type_id_2_entity_type_configuration),
                             )

    @property
    def main_program_help(self) -> MainProgramHelp:
        return self[0]

    @property
    def test_case_help(self) -> TestCaseHelp:
        return self[1]

    @property
    def test_suite_help(self) -> TestSuiteHelp:
        return self[2]

    def entity_type_conf_for(self, entity_type_id: str) -> EntityTypeConfiguration:
        return self.entity_type_id_2_entity_type_conf[entity_type_id]

    @property
    def entity_type_id_2_entity_type_conf(self) -> Dict[str, EntityTypeConfiguration]:
        """
        entity-type-identifier -> EntityTypeConfiguration
        """
        return self[3]
