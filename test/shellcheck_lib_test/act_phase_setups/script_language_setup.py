import unittest

from shellcheck_lib.act_phase_setups import script_language_setup as sut
from shellcheck_lib.test_case.sections.act.script_source import ScriptSourceBuilder
from shellcheck_lib.script_language import python3
from shellcheck_lib_test.test_case.test_resources.act_program_executor import ActProgramExecutorTestSetup, Tests


class TestCases(unittest.TestCase):
    def __init__(self, method_name='runTest'):
        super().__init__(methodName=method_name)
        self.tests = Tests(self, TestSetup())

    def test_stdout_is_connected_to_program(self):
        self.tests.test_stdout_is_connected_to_program()

    def test_stderr_is_connected_to_program(self):
        self.tests.test_stderr_is_connected_to_program()


class TestSetup(ActProgramExecutorTestSetup):
    def __init__(self):
        self.language = python3.language()
        self.language_setup = python3.script_language_setup()
        super().__init__(sut.ActProgramExecutorForScriptLanguage(self.language_setup))

    def program_that_copes_stdin_to_stdout(self) -> ScriptSourceBuilder:
        raise NotImplementedError()

    def program_that_prints_to_stderr(self, string_to_print: str) -> ScriptSourceBuilder:
        source_builder = ScriptSourceBuilder(self.language)
        source_builder.raw_script_statements([
            'import sys',
            "sys.stderr.write('{}')".format(string_to_print)
        ])
        return source_builder

    def program_that_prints_to_stdout(self, string_to_print: str) -> ScriptSourceBuilder:
        source_builder = ScriptSourceBuilder(self.language)
        source_builder.raw_script_statements([
            'import sys',
            "sys.stdout.write('{}')".format(string_to_print)
        ])
        return source_builder


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCases))
    return ret_val


if __name__ == '__main__':
    unittest.main()
