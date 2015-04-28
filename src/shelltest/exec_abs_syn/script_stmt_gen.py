import os

__author__ = 'emil'

from shelltest.exec_abs_syn.config import Configuration

from shelltest.phase_instr.line_source import Line


class ScriptLanguage:
    def command_and_args_for_executing_script_file(self, script_file_name: str) -> list:
        """
        :returns The list of the command and it's arguments for executing the given
        script file (that is a program in the language defined by this object).
        """
        raise NotImplementedError()

    def base_name_from_stem(self, stem: str):
        raise NotImplementedError()

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


class StatementsGenerator:
    """
    Base class for object that can generate commands for a script of a type defined by ScriptLanguage.
    """

    def apply(self,
              script_language: ScriptLanguage,
              configuration: Configuration) -> list:
        """
        Generates script source code lines for this command.
        :return List of source code lines, each line is a str.
        """
        raise NotImplementedError()


class StatementsGeneratorForInstruction(StatementsGenerator):
    """
    Base class for StatementsGenerator that generates statements for a single instruction.
    """

    def __init__(self):
        pass

    def apply(self, script_language: ScriptLanguage, configuration: Configuration) -> list:
        ret_val = []
        ret_val.extend(self.instruction_implementation(configuration, script_language))
        return ret_val

    def instruction_implementation(self,
                                   configuration: Configuration,
                                   script_language: ScriptLanguage) -> list:
        """
        Generates script source code lines that implement the instruction that this object represents.
        :return List of source code lines, each line is a str.
        """
        raise NotImplementedError()


class StatementsGeneratorForFileContents(StatementsGenerator):
    """
    Object that can generate a shell script.
    """

    def __init__(self,
                 instruction_statements_generators: list):
        """
        :param instruction_statements_generators: List of StatementsGeneratorForInstruction:s.
        """
        self.__instruction_statements_generators = instruction_statements_generators

    @property
    def instruction_statements_generators(self) -> list:
        """
        :returnsList of StatementsGeneratorForInstruction:s.
        """
        return self.__instruction_statements_generators

    def apply(self, script_language: ScriptLanguage, configuration: Configuration) -> list:
        """
        Generates script source code lines for this command.
        :return List of source code lines, each line is a str.
        """
        ret_val = []
        for generator in self.__instruction_statements_generators:
            ret_val.extend(generator.apply(script_language, configuration))
        return ret_val





















# New code related to refactoring


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


class ScriptSourceWriter:
    """
    Accumulates statements of a script program and generates the final source lines
    of the complete script.

    An object must only be used to generate a single script program.
    """

    def __init__(self,
                 script_language: ScriptLanguage):
        self._script_language = script_language
        self._source_lines = []
        self._final_source_code = None

    def final_source_lines(self) -> str:
        """
        Gives the complete script source after all statements have been accumulated.

        No script statements must be added after this method has been called.

        :rtype List of strings: each string is a single line in the script.
        """
        if not self._final_source_code:
            self._final_source_code = self._final_source_code_string()
        return self._final_source_code

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

    def raw_script_statement(self, statement: str) -> list:
        """
        Appends a statement in the script language.

        The statement will be terminated by a new-line.
        """
        self._source_lines.extend(self._script_language.raw_script_statement(statement))

    def raw_script_statements(self, statements: iter) -> list:
        """
        Appends multiple statements in the script script.

        Each statement will be terminated by a new-line.
        """
        self._source_lines.extend(self._script_language.raw_script_statements(statements))

    def source_line_header(self, source_line: Line) -> list:
        line_ref = 'Line %d' % source_line.line_number
        line_contents = source_line.text
        return self.comment_lines([line_ref,
                                   line_contents])

    def _final_source_code_string(self) -> str:
        return os.linesep.join(self._source_lines) + os.linesep


class ScriptGenerator:
    """
    Abstract base class for generating a script file.

    Provides a buffer for accumulating script source.

    Can generate a single script.
    """

    def command_and_args_for_executing_script_file(self, script_file_name: str) -> list:
        """
        :returns The list of the command and it's arguments for executing the given
        script file (that is a program in the language defined by this object).
        """
        raise NotImplementedError()

    def base_name_from_stem(self, stem: str) -> str:
        raise NotImplementedError()

