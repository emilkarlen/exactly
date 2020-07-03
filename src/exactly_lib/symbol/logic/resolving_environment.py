from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.util.symbol_table import SymbolTable


class FullResolvingEnvironment(tuple):
    """
    Everything needed to resolve the applicator of a logic type,
    from a parsed object.
    """

    def __new__(cls,
                symbols: SymbolTable,
                tcds: Tcds,
                application_environment: ApplicationEnvironment,
                ):
        return tuple.__new__(cls, (symbols, tcds, application_environment))

    @property
    def symbols(self) -> SymbolTable:
        return self[0]

    @property
    def tcds(self) -> Tcds:
        return self[1]

    @property
    def application_environment(self) -> ApplicationEnvironment:
        return self[2]
