from exactly_lib.execution.result import FullResultStatus
from exactly_lib.help.entities.configuration_parameters.contents_structure import ConfigurationParameterDocumentation
from exactly_lib.help_texts.doc_format import syntax_text
from exactly_lib.help_texts.entity.conf_params import EXECUTION_MODE_CONF_PARAM_INFO
from exactly_lib.help_texts.test_case import phase_names
from exactly_lib.test_case import execution_mode
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem


class _ExecutionModeConfigurationParameter(ConfigurationParameterDocumentation):
    def __init__(self):
        super().__init__(EXECUTION_MODE_CONF_PARAM_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        return from_simple_description(
            Description(self.single_line_description(),
                        [execution_modes_list()]))


DOCUMENTATION = _ExecutionModeConfigurationParameter()


def execution_modes_list() -> ParagraphItem:
    items = [docs.list_item(syntax_text(x[0]), x[1])
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
