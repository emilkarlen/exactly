from shellcheck_lib.cli.execution_mode.help.mode.main_program.contents_structure import MainProgramHelp
from shellcheck_lib.cli.execution_mode.help.mode.test_case.contents_structure import TestCaseHelp
from shellcheck_lib.cli.execution_mode.help.mode.test_suite.contents_structure import TestSuiteHelp


class ApplicationHelp(tuple):
    def __new__(cls,
                main_program_help: MainProgramHelp,
                test_case_help: TestCaseHelp,
                test_suite_help: TestSuiteHelp):
        return tuple.__new__(cls, (main_program_help,
                                   test_case_help,
                                   test_suite_help))

    @property
    def main_program_help(self) -> MainProgramHelp:
        return self[0]

    @property
    def test_case_help(self) -> TestCaseHelp:
        return self[1]

    @property
    def test_suite_help(self) -> TestSuiteHelp:
        return self[2]
