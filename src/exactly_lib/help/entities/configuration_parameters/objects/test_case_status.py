from exactly_lib.definitions import doc_format
from exactly_lib.definitions.entity.conf_params import TEST_CASE_STATUS_CONF_PARAM_INFO
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.execution.full_execution.result import FullExeResultStatus
from exactly_lib.help.entities.configuration_parameters.contents_structure import ConfigurationParameterDocumentation
from exactly_lib.processing import exit_values
from exactly_lib.test_case import test_case_status
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem, Text
from exactly_lib.util.textformat.textformat_parser import TextParser


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

_TEXT_PARSER = TextParser({
    'assert_phase': phase_names.ASSERT,
    'full_result_skipped': FullExeResultStatus.SKIPPED.name,

    'ASSERT_PASS': exit_values.EXECUTION__PASS.exit_identifier,
    'ASSERT_FAIL': exit_values.EXECUTION__FAIL.exit_identifier,

    'on_fail': exit_values.EXECUTION__XFAIL.exit_identifier,
    'on_pass': exit_values.EXECUTION__XPASS.exit_identifier,
    'on_skip': exit_values.EXECUTION__SKIPPED.exit_identifier,
})


def execution_modes_list() -> ParagraphItem:
    items = [docs.list_item(doc_format.enum_name_text(x[0]), x[1])
             for x in _mode_name_and_paragraphs_list()]
    return docs.simple_list_with_space_between_elements_and_content(items,
                                                                    lists.ListType.VARIABLE_LIST)


def _mode_name_and_paragraphs_list() -> list:
    return [
        (test_case_status.NAME_PASS, _TEXT_PARSER.fnap(_DESCRIPTION_PASS)),
        (test_case_status.NAME_FAIL, _TEXT_PARSER.fnap(_DESCRIPTION_FAIL)),
        (test_case_status.NAME_SKIP, _TEXT_PARSER.fnap(_DESCRIPTION_SKIP)),
    ]


_DESCRIPTION_PASS = """\
The test case is executed and the {assert_phase} phase is expected to {ASSERT_PASS}.
"""

_DESCRIPTION_FAIL = """\
The test case is executed and the {assert_phase} phase is expected to {ASSERT_FAIL}.


Outcome of the test case is {on_fail}, if {assert_phase:syntax} {ASSERT_FAIL}s.

If {assert_phase:syntax} {ASSERT_PASS}, the result is {on_pass}.
"""

_DESCRIPTION_SKIP = """\
The test case is not executed.


Outcome of the test case is {on_skip}.
"""
