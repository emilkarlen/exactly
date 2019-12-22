from exactly_lib.type_system.logic.program.process_execution.command import ProgramAndArguments


class SourceFileManager:
    """
    Manages generation of a file-name and execution of an existing file.
    """

    def base_name_from_stem(self, stem: str) -> str:
        raise NotImplementedError()

    def command_and_args_for_executing_script_file(self, script_file_name: str) -> ProgramAndArguments:
        """
        :returns The list of the command and it's arguments for executing the given
        script file (that is a program in the language defined by this object).
        """
        raise NotImplementedError()


class SourceInterpreterSetup:
    def __init__(self, file_manager: SourceFileManager):
        self.__file_manager = file_manager

    def base_name_from_stem(self, stem: str) -> str:
        return self.__file_manager.base_name_from_stem(stem)

    def command_and_args_for_executing_script_file(self, file_name: str) -> ProgramAndArguments:
        return self.__file_manager.command_and_args_for_executing_script_file(file_name)


class StandardSourceFileManager(SourceFileManager):
    def __init__(self,
                 extension_after_dot: str,
                 interpreter: str,
                 command_line_options_before_file_argument: list):
        self.extension_after_dot = extension_after_dot
        self.interpreter = interpreter
        self.command_line_options_before_file_argument = command_line_options_before_file_argument

    def base_name_from_stem(self, stem: str) -> str:
        return stem + '.' + self.extension_after_dot

    def command_and_args_for_executing_script_file(self, script_file_name: str) -> ProgramAndArguments:
        return ProgramAndArguments(self.interpreter,
                                   self.command_line_options_before_file_argument + [script_file_name])
