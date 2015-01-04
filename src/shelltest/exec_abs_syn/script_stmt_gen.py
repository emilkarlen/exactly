__author__ = 'emil'

from shelltest.exec_abs_syn.config import Configuration

from shelltest.phase_instr.line_source import Line


class ScriptLanguage:
    def base_name_from_stem(self, name):
        raise NotImplementedError()

    def comment_line(self, comment: str) -> list:
        raise NotImplementedError()

    def comment_lines(self, lines: list) -> list:
        raise NotImplementedError()

    def raw_script_statement(self, statement: str) -> list:
        raise NotImplementedError()

    def source_line_info(self, source_line: Line) -> list:
        line_ref = 'Line %d' % source_line.line_number
        line_contents = source_line.text
        return self.comment_lines([line_ref,
                                   line_contents])


class StatementsGenerator:
    """
    Base class for object that can generate commands for a script of a type defined by StatementConstructor.
    """

    def apply(self,
              configuration: Configuration,
              statement_constructor: ScriptLanguage) -> list:
        """
        Generates script source code lines for this command.
        :return List of source code lines, each line is a str.
        """
        raise NotImplementedError()


class StatementsGeneratorForInstruction(StatementsGenerator):
    """
    Base class for StatementsGenerator that generates statements for a single instruction.
    """

    def __init__(self, source_line: Line):
        self.__source_line = source_line

    @property
    def source_line(self) -> Line:
        return self.__source_line

    def apply(self,
              configuration: Configuration,
              statement_constructor: ScriptLanguage) -> list:
        ret_val = []
        ret_val.extend(statement_constructor.source_line_info(self.__source_line))
        ret_val.extend(self.instruction_implementation(configuration, statement_constructor))
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

    def apply(self,
              configuration: Configuration,
              statement_constructor: ScriptLanguage) -> list:
        """
        Generates script source code lines for this command.
        :return List of source code lines, each line is a str.
        """
        ret_val = []
        for generator in self.__instruction_statements_generators:
            ret_val.extend(generator.apply(configuration, statement_constructor))
        return ret_val
