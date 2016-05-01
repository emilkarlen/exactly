from exactly_lib.execution import execution_mode
from exactly_lib.execution.result import FullResultStatus
from exactly_lib.help.concepts.contents_structure import ConfigurationParameterDocumentation, Name
from exactly_lib.help.utils import phase_names
from exactly_lib.help.utils.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.help.utils.phase_names import phase_name_dictionary
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.structures import text


class _ExecutionModeConfigurationParameter(ConfigurationParameterDocumentation):
    def __init__(self):
        super().__init__(Name('execution mode', 'execution modes'))

    def purpose(self) -> DescriptionWithSubSections:
        return from_simple_description(
            Description(text(_EXECUTION_MODE_SINGLE_LINE_DESCRIPTION
                             .format(phase=phase_name_dictionary())),
                        [execution_modes_list()]))

    def default_value_str(self) -> str:
        return execution_mode.NAME_DEFAULT


EXECUTION_MODE_CONFIGURATION_PARAMETER = _ExecutionModeConfigurationParameter()
_EXECUTION_MODE_SINGLE_LINE_DESCRIPTION = """\
Determines how the outcome of the {phase[assert]} phase should be interpreted,
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
The test case is executed and the {0} phase is expected to PASS.""".format(phase_names.ASSERT_PHASE_NAME))),
        (execution_mode.NAME_SKIP,
         normalize_and_parse("""\
The test case is not executed.


Result of the test case is %s.""" % FullResultStatus.SKIPPED.name)),
        (execution_mode.NAME_XFAIL,
         normalize_and_parse("""\
The test case is executed and the {assert_} phase is expected to FAIL.


Result of the test case is {on_fail}, if {assert_:syntax} FAILs.

If it PASS, the result is {on_pass}.""".format(
             assert_=phase_names.ASSERT_PHASE_NAME,
             on_fail=FullResultStatus.XFAIL.name,
             on_pass=FullResultStatus.XPASS.name)
         )),
    ]
