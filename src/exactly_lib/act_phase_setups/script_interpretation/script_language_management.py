from exactly_lib.test_case.phases.act.program_source import ActSourceBuilderForPlainStringsBase


class ScriptLanguage:
    def comment_line(self, comment: str) -> list:
        raise NotImplementedError()

    def comment_lines(self, lines: list) -> list:
        ret_val = []
        for l in lines:
            ret_val.extend(self.comment_line(l))
        return ret_val

    def raw_script_statement(self, statement: str) -> list:
        raise NotImplementedError()

    def raw_script_statements(self, statements: iter) -> list:
        ret_val = []
        for statement in statements:
            ret_val.extend(self.raw_script_statement(statement))
        return ret_val


class ActSourceBuilderForScriptLanguage(ActSourceBuilderForPlainStringsBase):
    def __init__(self,
                 script_language: ScriptLanguage):
        super().__init__()
        self._script_language = script_language

    def comment_line(self, comment: str):
        """
        Appends a comment that stretches a single line.
        """
        self._source_lines.extend(self._script_language.comment_line(comment))

    def comment_lines(self, lines: list):
        """
        Appends a comment that stretches multiple lines.
        """
        self._source_lines.extend(self._script_language.comment_lines(lines))

    def raw_script_statement(self, statement: str):
        """
        Appends a statement in the script language.

        The statement will be terminated by a new-line.
        """
        self._source_lines.extend(self._script_language.raw_script_statement(statement))

    def raw_script_statements(self, statements: iter):
        """
        Appends multiple statements in the script script.

        Each statement will be terminated by a new-line.
        """
        self._source_lines.extend(self._script_language.raw_script_statements(statements))


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
    def file_manager(self) -> ScriptFileManager:
        return self.__file_manager

    def base_name_from_stem(self, stem: str) -> str:
        return self.__file_manager.base_name_from_stem(stem)

    def command_and_args_for_executing_script_file(self, file_name: str) -> list:
        return self.__file_manager.command_and_args_for_executing_script_file(file_name)


class StandardScriptFileManager(ScriptFileManager):
    def __init__(self,
                 extension_after_dot: str,
                 interpreter: str,
                 command_line_options_before_file_argument: list):
        self.extension_after_dot = extension_after_dot
        self.interpreter = interpreter
        self.command_line_options_before_file_argument = command_line_options_before_file_argument

    def base_name_from_stem(self, stem: str) -> str:
        return stem + '.' + self.extension_after_dot

    def command_and_args_for_executing_script_file(self, script_file_name: str) -> list:
        return [self.interpreter] + self.command_line_options_before_file_argument + [script_file_name]
