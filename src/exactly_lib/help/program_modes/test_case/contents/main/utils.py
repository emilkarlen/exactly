from exactly_lib.common.exit_value import ExitValue
from exactly_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from exactly_lib.help.utils.phase_names import phase_name_dictionary
from exactly_lib.help.utils.section_contents_renderer import SectionContentsRenderer
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.structures import first_column_is_header_table, para


class TestCaseHelpRendererBase(SectionContentsRenderer):
    def __init__(self, test_case_help: TestCaseHelp):
        self.test_case_help = test_case_help


class Setup(tuple):
    def __new__(cls,
                test_case_help: TestCaseHelp):
        return tuple.__new__(cls, (test_case_help, phase_name_dictionary()))

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
                                exit_value_on_error: ExitValue) -> list:
    outcome_on_error = singe_exit_value_display(exit_value_on_error)
    return purpose_paragraphs + [failure_condition, outcome_on_error]
