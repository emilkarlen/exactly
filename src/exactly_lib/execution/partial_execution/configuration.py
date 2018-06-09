from typing import Dict

from exactly_lib.section_document.model import SectionContents
from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value


class Configuration(tuple):
    def __new__(cls,
                act_phase_os_process_executor: ActPhaseOsProcessExecutor,
                hds: HomeDirectoryStructure,
                environ: Dict[str, str],
                timeout_in_seconds: int = None,
                predefined_symbols: SymbolTable = None):
        """
        :param timeout_in_seconds: None if no timeout
        """
        return tuple.__new__(cls, (hds,
                                   timeout_in_seconds,
                                   environ,
                                   act_phase_os_process_executor,
                                   symbol_table_from_none_or_value(predefined_symbols)))

    @property
    def act_phase_os_process_executor(self) -> ActPhaseOsProcessExecutor:
        return self[3]

    @property
    def hds(self) -> HomeDirectoryStructure:
        return self[0]

    @property
    def timeout_in_seconds(self) -> int:
        return self[1]

    @property
    def environ(self) -> Dict[str, str]:
        """
        The set of environment variables available to instructions.
        These may be both read and written.
        """
        return self[2]

    @property
    def predefined_symbols(self) -> SymbolTable:
        """
        Symbols that should be available in all steps.

        Should probably not be updated.
        """
        return self[4]


class TestCase(tuple):
    def __new__(cls,
                setup_phase: SectionContents,
                act_phase: SectionContents,
                before_assert_phase: SectionContents,
                assert_phase: SectionContents,
                cleanup_phase: SectionContents):
        return tuple.__new__(cls, (setup_phase,
                                   act_phase,
                                   before_assert_phase,
                                   assert_phase,
                                   cleanup_phase))

    @property
    def setup_phase(self) -> SectionContents:
        return self[0]

    @property
    def act_phase(self) -> SectionContents:
        return self[1]

    @property
    def before_assert_phase(self) -> SectionContents:
        return self[2]

    @property
    def assert_phase(self) -> SectionContents:
        return self[3]

    @property
    def cleanup_phase(self) -> SectionContents:
        return self[4]
