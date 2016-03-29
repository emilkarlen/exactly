from shellcheck_lib.cli.cli_environment import exit_values
from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from shellcheck_lib.util.textformat.structure.core import ParagraphItem
from shellcheck_lib.util.textformat.structure.structures import first_column_is_header_table, para


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


def singe_exit_value_display(exit_value_on_error) -> ParagraphItem:
    return first_column_is_header_table([
        [[para('Exit code')], [para(str(exit_value_on_error.exit_code))]],
        [[para('Exit identifier')], [para(exit_value_on_error.exit_identifier)]],
    ])


def post_setup_validation_step_name(setup: Setup) -> str:
    return 'post {phase[setup]:syntax} validation'.format(phase=setup.phase_names)


def step_with_single_exit_value(purpose_paragraphs: list,
                                failure_condition: ParagraphItem,
                                exit_value_on_error: exit_values.ExitValue) -> list:
    outcome_on_error = singe_exit_value_display(exit_value_on_error)
    return purpose_paragraphs + [failure_condition, outcome_on_error]
