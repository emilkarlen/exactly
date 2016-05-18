from exactly_lib.test_case.phases.act.script_source import ScriptLanguage, ScriptSourceBuilder


class ScriptFileManager:
    """
    Manages generation of a file-name and execution of an existing file.
    """

    def base_name_from_stem(self, stem: str) -> str:
        raise NotImplementedError()

    def command_and_args_for_executing_script_file(self, script_file_name: str) -> list:
        """
        :returns The list of the command and it's arguments for executing the given
        script file (that is a program in the language defined by this object).
        """
        raise NotImplementedError()


class ScriptLanguageSetup:
    def __init__(self,
                 file_manager: ScriptFileManager,
                 language: ScriptLanguage):
        self.__file_manager = file_manager
        self.__language = language

    @property
    def language(self) -> ScriptLanguage:
        return self.__language

    @property
    def file_manager(self) -> ScriptFileManager:
        return self.__file_manager

    def new_builder(self) -> ScriptSourceBuilder:
        return ScriptSourceBuilder(self.__language)

    def base_name_from_stem(self, stem: str) -> str:
        return self.__file_manager.base_name_from_stem(stem)

    def command_and_args_for_executing_script_file(self, file_name: str) -> list:
        return self.__file_manager.command_and_args_for_executing_script_file(file_name)
