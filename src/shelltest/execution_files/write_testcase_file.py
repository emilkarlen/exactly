__author__ = 'emil'

import os
import pathlib

from shelltest.exec_abs_syn import script_stmt_gen
from shelltest.phase import Phase
from shelltest.exec_abs_syn.config import Configuration
from shelltest.execution_files import execution_directory_structure


def write(statement_constructor: script_stmt_gen.ScriptLanguage,
          test_root: execution_directory_structure.ExecutionDirectoryStructure,
          configuration: Configuration,
          phase: Phase,
          statement_generators: list) -> pathlib.Path:
    """
    :param statement_generators: List of script_stmt_gen.StatementsGeneratorForInstruction
    :return: Path of the written file.
    """
    base_name = statement_constructor.base_name_from_stem(phase.name)
    # file_path = test_root.test_case.root_dir / base_name
    file_path = test_root.test_case_dir / base_name
    with open(str(file_path), 'w') as f:
        for statement_generator in statement_generators:
            for line in statement_generator.apply(configuration, statement_constructor):
                f.write(line)
                f.write(os.linesep)
    return file_path