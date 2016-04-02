from shellcheck_lib.execution import execution_mode
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.help.utils.description import Description
from shellcheck_lib.help.utils.phase_names import ASSERT_PHASE_NAME
from shellcheck_lib.util.textformat.parse import normalize_and_parse
from shellcheck_lib.util.textformat.structure import lists
from shellcheck_lib.util.textformat.structure.core import ParagraphItem
from shellcheck_lib.util.textformat.structure.structures import para, text


class Name(tuple):
    def __new__(cls,
                singular: str):
        return tuple.__new__(cls, (singular,))

    @property
    def singular(self) -> str:
        return self[0]


class ConfigurationParameterDocumentation:
    def __init__(self,
                 name: Name):
        self._name = name

    def name(self) -> Name:
        return self._name

    def purpose(self) -> Description:
        raise NotImplementedError()

    def default_value_str(self) -> str:
        """
        :rtype: [ParagraphItem]
        """
        raise NotImplementedError()

    def default_value_para(self) -> ParagraphItem:
        return para(self.default_value_str())


class _ExecutionModeConcept(ConfigurationParameterDocumentation):
    def __init__(self):
        super().__init__(Name('execution mode'))

    def purpose(self) -> Description:
        return Description(text(_EXECUTION_MODE_SINGLE_LINE_DESCRIPTION),
                           [execution_modes_list()])

    def default_value_str(self) -> str:
        return execution_mode.NAME_DEFAULT


EXECUTION_MODE_CONCEPT = _ExecutionModeConcept()

_EXECUTION_MODE_SINGLE_LINE_DESCRIPTION = """\
Determines how the outcome of the {assert_phase} phase should be interpreted,
or if the test case should be skipped."""


def execution_modes_list() -> ParagraphItem:
    items = [lists.HeaderContentListItem(text(x[0]), x[1])
             for x in _mode_name_and_paragraphs_list()]
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.VARIABLE_LIST))


def _mode_name_and_paragraphs_list() -> list:
    return [
        (execution_mode.NAME_NORMAL,
         normalize_and_parse("""\
The test case is executed and the {0} phase is expected to PASS.""".format(ASSERT_PHASE_NAME))),
        (execution_mode.NAME_SKIP,
         normalize_and_parse("""\
The test case is not executed.


Result of the test case is %s.""" % FullResultStatus.SKIPPED.name)),
        (execution_mode.NAME_XFAIL,
         normalize_and_parse("""\
The test case is executed and the {assert_} phase is expected to FAIL.


Result of the test case is {on_fail}, if {assert_:syntax} FAILs.

If it PASS, the result is {on_pass}.""".format(
             assert_=ASSERT_PHASE_NAME,
             on_fail=FullResultStatus.XFAIL.name,
             on_pass=FullResultStatus.XPASS.name)
         )),
    ]
