from typing import Dict, Callable

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.execution import sandbox_dir_resolving
from exactly_lib.execution.sandbox_dir_resolving import SandboxRootDirNameResolver
from exactly_lib.section_document.section_element_parsing import SectionElementParser


class TestSuiteDefinition(tuple):
    def __new__(cls,
                configuration_section_instructions: Dict[str, SingleInstructionSetup],
                configuration_section_parser: SectionElementParser,
                get_sds_root_name_prefix: Callable[[], str] = lambda: '',
                ):
        return tuple.__new__(cls, (configuration_section_instructions,
                                   configuration_section_parser,
                                   get_sds_root_name_prefix))

    @property
    def configuration_section_instructions(self) -> Dict[str, SingleInstructionSetup]:
        return self[0]

    @property
    def configuration_section_parser(self) -> SectionElementParser:
        return self[1]

    @property
    def sandbox_root_dir_sdv(self) -> SandboxRootDirNameResolver:
        return sandbox_dir_resolving.mk_tmp_dir_with_prefix(self._get_sds_root_name_prefix())

    @property
    def _get_sds_root_name_prefix(self) -> Callable[[], str]:
        return self[2]
