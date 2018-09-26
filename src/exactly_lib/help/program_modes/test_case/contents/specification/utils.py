from typing import List, Dict, Tuple

from exactly_lib.common.exit_value import ExitValue
from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.doc_format import exit_value_text
from exactly_lib.definitions.formatting import SectionName
from exactly_lib.definitions.test_case.phase_names import PHASE_NAME_DICTIONARY
from exactly_lib.help.program_modes.test_case.contents_structure.test_case_help import TestCaseHelp
from exactly_lib.util.textformat.constructor.section import \
    SectionContentsConstructor
from exactly_lib.util.textformat.structure import structures as docs
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
    def phase_names(self) -> Dict[str, SectionName]:
        return self[1]


def singe_exit_value_display(exit_value: ExitValue) -> ParagraphItem:
    return first_column_is_header_table([
        [
            cell([para(misc_texts.EXIT_CODE_TITLE)]),
            cell([para(str(exit_value.exit_code))]),
        ],
        [
            cell([para(misc_texts.EXIT_IDENTIFIER_TITLE)]),
            cell([para(exit_value_text(exit_value))]),
        ],
    ])


def post_setup_validation_step_name(setup: Setup) -> str:
    return 'post {phase[setup]:syntax} validation'.format(phase=setup.phase_names)


def step_with_single_exit_value(purpose_paragraphs: List[ParagraphItem],
                                failure_condition: ParagraphItem,
                                exit_value_on_error: ExitValue) -> List[ParagraphItem]:
    return step_with_single_exit_value2(purpose_paragraphs, [failure_condition], exit_value_on_error)


def step_with_multiple_exit_values(purpose_paragraphs: List[ParagraphItem],
                                   failure_condition: List[ParagraphItem],
                                   exit_value_on_errors: List[Tuple[str, ExitValue]]) -> List[ParagraphItem]:
    def failure_item(header__exit_value: Tuple[str, ExitValue]) -> docs.lists.HeaderContentListItem:
        return docs.list_item(header__exit_value[0],
                              [singe_exit_value_display(header__exit_value[1])])

    outcome_on_error = docs.simple_list(map(failure_item, exit_value_on_errors),
                                        docs.lists.ListType.ITEMIZED_LIST)
    return purpose_paragraphs + failure_condition + [outcome_on_error]


def step_with_single_exit_value2(purpose_paragraphs: List[ParagraphItem],
                                 failure_condition: List[ParagraphItem],
                                 exit_value_on_error: ExitValue) -> List[ParagraphItem]:
    outcome_on_error = singe_exit_value_display(exit_value_on_error)
    return purpose_paragraphs + failure_condition + [outcome_on_error]
