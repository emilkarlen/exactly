__author__ = 'emil'

import os
import pathlib
import unittest

from shelltest import phases
from shelltest.exec_abs_syn import abs_syn_gen, py_cmd_gen, script_stmt_gen, config, instructions
from shelltest.phase_instr import line_source
from shelltest_test.execution.util import python_code_gen as py
from shelltest_test.execution.util.py_unit_test_case_with_file_output import \
    UnitTestCaseForPyLanguageThatWritesAFileToTestRootForEachPhase, \
    PyCommandThatWritesToStandardPhaseFile, \
    StatementsGeneratorThatWritesToStandardPhaseFile, \
    ModulesAndStatements
from shelltest_test.execution.util.utils import un_lines


class TestCase(UnitTestCaseForPyLanguageThatWritesAFileToTestRootForEachPhase):
    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False):
        super().__init__(unittest_case, dbg_do_not_delete_dir_structure)

    def _phase_env_for_py_cmd_phase(self, phase: phases.Phase) -> abs_syn_gen.PhaseEnvironmentForPythonCommands:
        return \
            abs_syn_gen.PhaseEnvironmentForPythonCommands([
                PyCommandThatWritesCurrentWorkingDirectory(
                    phase),
                PyCommandThatChangesCwdToHomeDir()
            ])

    def _phase_env_act(self) -> instructions.PhaseEnvironmentForScriptGeneration:
        import_statements_generator = StatementsGeneratorForImportStatements()
        return \
            instructions.PhaseEnvironmentForScriptGeneration([
                import_statements_generator,
                StatementsGeneratorThatWritesCurrentWorkingDirectory(
                    phases.ACT,
                    import_statements_generator),
                StatementsGeneratorThatChangesCwdToHomeDir(import_statements_generator)
            ])

    def _expected_content_for(self, phase: phases.Phase) -> str:
        return un_lines([str(self.eds.test_root_dir)])


class PyCommandThatWritesCurrentWorkingDirectory(PyCommandThatWritesToStandardPhaseFile):
    def __init__(self,
                 phase: phases.Phase):
        super().__init__(phase)

    def file_lines(self, configuration) -> list:
        cwd_path = pathlib.Path().resolve()
        return [str(cwd_path)]


class PyCommandThatChangesCwdToHomeDir(py_cmd_gen.PythonCommand):
    def __init__(self):
        super().__init__()

    def apply(self, configuration: config.Configuration):
        os.chdir(str(configuration.home_dir))
        # print(os.getcwd())


class StatementsGeneratorForImportStatements(script_stmt_gen.StatementsGeneratorForInstruction):
    """
    Pseudo-instruction for outputting Python import statements at the top of the program.

    Later instructions add their used modules to an object of this class.
    """

    def __init__(self):
        super().__init__()
        self.__modules = set()

    def append_module(self, module_name: str):
        self.__modules.add(module_name)

    def instruction_implementation(self,
                                   configuration: config.Configuration,
                                   script_language: script_stmt_gen.ScriptLanguage) -> list:
        import_statements = ['import %s' % module_name
                             for module_name in self.__modules]
        return script_language.raw_script_statements(import_statements)


class StatementsGeneratorThatWritesCurrentWorkingDirectory(StatementsGeneratorThatWritesToStandardPhaseFile):
    def __init__(self,
                 phase: phases.Phase,
                 module_container: StatementsGeneratorForImportStatements):
        super().__init__(phase)
        self.__phase = phase
        module_container.append_module('pathlib')

    def code_using_file_opened_for_writing(self,
                                           file_variable: str) -> ModulesAndStatements:
        print_statements = [py.print_value('pathlib.Path().resolve()',
                                           file_variable)]
        return ModulesAndStatements(set(),
                                    print_statements)


class StatementsGeneratorThatChangesCwdToHomeDir(script_stmt_gen.StatementsGeneratorForInstruction):
    def __init__(self,
                 module_container: StatementsGeneratorForImportStatements):
        super().__init__()
        module_container.append_module('os')

    def instruction_implementation(self,
                                   configuration: config.Configuration,
                                   script_language: script_stmt_gen.ScriptLanguage) -> list:
        statements = [
            'os.chdir(%s)' % py.string_expr(str(configuration.home_dir)),
            #'print(os.getcwd())'
        ]
        return script_language.raw_script_statements(statements)
