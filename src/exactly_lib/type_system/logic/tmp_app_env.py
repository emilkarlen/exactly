from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment
from exactly_lib.util.file_utils import TmpDirFileSpaceThatMustNoBeUsed


def application_environment__transitional() -> ApplicationEnvironment:
    return ApplicationEnvironment(TmpDirFileSpaceThatMustNoBeUsed())
