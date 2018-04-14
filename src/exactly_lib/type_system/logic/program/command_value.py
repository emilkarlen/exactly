from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue, DirDependentValue
from exactly_lib.util.process_execution.command import Command, CommandDriver


class CommandDriverValue(DirDependentValue[CommandDriver]):
    pass


class CommandValue(MultiDirDependentValue[Command]):
    pass
