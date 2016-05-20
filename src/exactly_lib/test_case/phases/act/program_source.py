import os


class ScriptSourceAccumulator:
    """
    Accumulates statements of a script program.

    Do not have the ability, though, to generates the final source lines
    of the complete script.
    """

    def comment_line(self, comment: str):
        """
        Appends a comment that stretches a single line.
        """
        raise NotImplementedError()

    def comment_lines(self, lines: list):
        """
        Appends a comment that stretches multiple lines.
        """
        raise NotImplementedError()

    def raw_script_statement(self, statement: str):
        """
        Appends a statement in the script language.

        The statement will be terminated by a new-line.
        """
        raise NotImplementedError()

    def raw_script_statements(self, statements: iter):
        """
        Appends multiple statements in the script script.

        Each statement will be terminated by a new-line.
        """
        raise NotImplementedError()


class ActSourceBuilder(ScriptSourceAccumulator):
    def build(self) -> str:
        raise NotImplementedError()

    @property
    def source_lines(self) -> list:
        raise NotImplementedError()

    def comment_line(self, comment: str):
        pass

    def comment_lines(self, lines: list):
        pass

    def raw_script_statement(self, statement: str):
        pass

    def raw_script_statements(self, statements: iter):
        pass


class ActSourceBuilderForPlainStringsBase(ActSourceBuilder):
    def __init__(self):
        self._final_source_code = None
        self._source_lines = []

    def build(self) -> str:
        """
        Gives the complete script source after all statements have been accumulated.

        No script statements must be added after this method has been called.

        :rtype List of strings: each string is a single line in the script.
        """
        if not self._final_source_code:
            self._final_source_code = self._final_source_code_string()
        return self._final_source_code

    @property
    def source_lines(self) -> list:
        return self._source_lines

    def _final_source_code_string(self) -> str:
        return os.linesep.join(self._source_lines) + os.linesep


class ActSourceBuilderForStatementLines(ActSourceBuilderForPlainStringsBase):
    """
    Ignores comment lines.
    """

    def __init__(self):
        super().__init__()

    def raw_script_statement(self, statement: str):
        """
        Appends a statement in the script language.

        The statement will be terminated by a new-line.
        """
        self._source_lines.append(statement)

    def raw_script_statements(self, statements: iter):
        """
        Appends multiple statements in the script script.

        Each statement will be terminated by a new-line.
        """
        self._source_lines.extend(statements)
