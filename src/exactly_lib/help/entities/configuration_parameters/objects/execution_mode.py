from exactly_lib.execution.result import FullResultStatus
from exactly_lib.help.entities.configuration_parameters.contents_structure import ConfigurationParameterDocumentation
from exactly_lib.help_texts import doc_format
from exactly_lib.help_texts.entity.conf_params import TEST_CASE_STATUS_CONF_PARAM_INFO
from exactly_lib.help_texts.test_case import phase_names
from exactly_lib.test_case import test_case_status
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem, Text


class _ExecutionModeConfigurationParameter(ConfigurationParameterDocumentation):
    def __init__(self):
        super().__init__(TEST_CASE_STATUS_CONF_PARAM_INFO)

    def default_value_text(self) -> Text:
        return doc_format.enum_name_text(self.default_value_str())

    def purpose(self) -> DescriptionWithSubSections:
        return from_simple_description(
            Description(self.single_line_description(),
                        [execution_modes_list()]))


DOCUMENTATION = _ExecutionModeConfigurationParameter()


def execution_modes_list() -> ParagraphItem:
    items = [docs.list_item(doc_format.enum_name_text(x[0]), x[1])
             for x in _mode_name_and_paragraphs_list()]
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.VARIABLE_LIST))


def _mode_name_and_paragraphs_list() -> list:
    return [
        (test_case_status.NAME_PASS,
         normalize_and_parse("""\
The test case is executed and the {0} phase is expected to PASS.""".format(phase_names.ASSERT_PHASE_NAME))),
        (test_case_status.NAME_SKIP,
         normalize_and_parse("""\
The test case is not executed.


Result of the test case is %s.""" % FullResultStatus.SKIPPED.name)),
        (test_case_status.NAME_FAIL,
         normalize_and_parse("""\
The test case is executed and the {assert_} phase is expected to FAIL.


Result of the test case is {on_fail}, if {assert_:syntax} FAILs.

If it PASS, the result is {on_pass}.""".format(
             assert_=phase_names.ASSERT_PHASE_NAME,
             on_fail=FullResultStatus.XFAIL.name,
             on_pass=FullResultStatus.XPASS.name)
         )),
    ]
