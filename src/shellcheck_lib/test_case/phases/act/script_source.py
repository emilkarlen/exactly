import os

from shellcheck_lib.general.line_source import Line


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

    def source_line_header(self, source_line: Line) -> list:
        line_ref = 'Line %d' % source_line.line_number
        line_contents = source_line.text
        return self.comment_lines([line_ref,
                                   line_contents])


class ScriptSourceAccumulator:
    """
    Accumulates statements of a script program.

    Do not have the ability, though, to generates the final source lines
    of the complete script.
    """

    def __init__(self,
                 script_language: ScriptLanguage):
        self._script_language = script_language
        self._source_lines = []

    def comment_line(self, comment: str):
        """
        Appends a comment that stretches a single line.
        """
        self._source_lines.extend(self._script_language.comment_line(comment))

    def comment_lines(self, lines: list) -> list:
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

    def source_line_header(self, source_line: Line):
        line_ref = 'Line %d' % source_line.line_number
        line_contents = source_line.text
        self.comment_lines([line_ref,
                            line_contents])


class ScriptSourceBuilder(ScriptSourceAccumulator):
    """
    An ScriptSourceAccumulator extended with the functionality to
    generates the final source lines of the complete script.
    """

    def __init__(self,
                 script_language: ScriptLanguage):
        super().__init__(script_language)
        self._final_source_code = None

    def build(self) -> str:
        """
        Gives the complete script source after all statements have been accumulated.

        No script statements must be added after this method has been called.

        :rtype List of strings: each string is a single line in the script.
        """
        if not self._final_source_code:
            self._final_source_code = self._final_source_code_string()
        return self._final_source_code

    def _final_source_code_string(self) -> str:
        return os.linesep.join(self._source_lines) + os.linesep

    @property
    def source_lines(self) -> list:
        return self._source_lines
