__author__ = 'emil'

import os
import pathlib

from shelltest.exec_abs_syn import script_stmt_gen
from shelltest.phases import Phase
from shelltest.exec_abs_syn.config import Configuration
from shelltest.execution.execution_directory_structure import ExecutionDirectoryStructure


def write(script_language: script_stmt_gen.ScriptLanguage,
          execution_directory_structure: ExecutionDirectoryStructure,
          configuration: Configuration,
          phase: Phase,
          statement_generators: list) -> pathlib.Path:
    """
    :type: statement_generators: list[script_stmt_gen.StatementsGeneratorForInstruction]
    :return: Path of the written file.
    """
    base_name = script_language.base_name_from_stem(phase.name)
    file_path = execution_directory_structure.test_case_dir / base_name
    with open(str(file_path), 'w') as f:
        for statement_generator in statement_generators:
            assert isinstance(statement_generator, script_stmt_gen.StatementsGeneratorForInstruction)
            for line in statement_generator.apply(script_language, configuration):
                f.write(line)
                f.write(os.linesep)
    return file_path
