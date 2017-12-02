from exactly_lib.common.exit_value import ExitValue
from exactly_lib.help import texts
from exactly_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from exactly_lib.help_texts.doc_format import exit_value_text
from exactly_lib.help_texts.test_case.phase_names import PHASE_NAME_DICTIONARY
from exactly_lib.util.textformat.construction.section_contents_constructor import SectionContentsConstructor
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.structures import first_column_is_header_table, para, cell


class TestCaseHelpConstructorBase(SectionContentsConstructor):
    def __init__(self, test_case_help: TestCaseHelp):
        self.test_case_help = test_case_help


class Setup(tuple):
    def __new__(cls,
                test_case_help: TestCaseHelp):
        return tuple.__new__(cls, (test_case_help, PHASE_NAME_DICTIONARY))

    @property
    def test_case_help(self) -> TestCaseHelp:
        return self[0]

    @property
    def phase_names(self) -> dict:
        return self[1]


def singe_exit_value_display(exit_value_on_error) -> ParagraphItem:
    return first_column_is_header_table([
        [
            cell([para(texts.EXIT_CODE_TITLE)]),
            cell([para(str(exit_value_on_error.exit_code))]),
        ],
        [
            cell([para(texts.EXIT_IDENTIFIER_TITLE)]),
            cell([para(exit_value_text(exit_value_on_error))]),
        ],
    ])


def post_setup_validation_step_name(setup: Setup) -> str:
    return 'post {phase[setup]:syntax} validation'.format(phase=setup.phase_names)


def step_with_single_exit_value(purpose_paragraphs: list,
                                failure_condition: ParagraphItem,
                                exit_value_on_error: ExitValue) -> list:
    outcome_on_error = singe_exit_value_display(exit_value_on_error)
    return purpose_paragraphs + [failure_condition, outcome_on_error]
