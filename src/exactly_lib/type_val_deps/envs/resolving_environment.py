from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.util.symbol_table import SymbolTable


class FullResolvingEnvironment(tuple):
    """
    Everything needed to resolve the applicator of a logic type,
    from a parsed object.
    """

    def __new__(cls,
                symbols: SymbolTable,
                tcds: TestCaseDs,
                application_environment: ApplicationEnvironment,
                ):
        return tuple.__new__(cls, (symbols, tcds, application_environment))

    @property
    def symbols(self) -> SymbolTable:
        return self[0]

    @property
    def tcds(self) -> TestCaseDs:
        return self[1]

    @property
    def application_environment(self) -> ApplicationEnvironment:
        return self[2]
