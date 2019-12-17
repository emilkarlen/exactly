from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment
from exactly_lib.util.file_utils import TmpDirFileSpaceThatMustNoBeUsed, TmpDirFileSpace


def application_environment(
        tmp_file_space: TmpDirFileSpace = TmpDirFileSpaceThatMustNoBeUsed()) -> ApplicationEnvironment:
    return ApplicationEnvironment(tmp_file_space)
