from typing import List

from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def model_lines_lists_matches(expected: ValueAssertion[List[str]]) -> ValueAssertion[StringModel]:
    return asrt.and_([
        asrt.sub_component(
            'as_lines',
            _line_list_from_as_lines,
            expected,
        ),
        asrt.sub_component(
            'as_file',
            _line_list_from_as_file,
            expected,
        ),
    ])


def _line_list_from_as_lines(model: StringModel) -> List[str]:
    with model.as_lines as lines:
        return list(lines)


def _line_list_from_as_file(model: StringModel) -> List[str]:
    with model.as_file.open() as f:
        return list(f.readlines())
