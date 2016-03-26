from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCaseHelp


class Setup(tuple):
    def __new__(cls,
                test_case_help: TestCaseHelp):
        phase_names = {}
        for phase in test_case_help.phase_helps_in_order_of_execution:
            phase_names[phase.name.plain] = phase.name
        return tuple.__new__(cls, (test_case_help, phase_names))

    @property
    def test_case_help(self) -> TestCaseHelp:
        return self[0]

    @property
    def phase_names(self) -> dict:
        return self[1]
