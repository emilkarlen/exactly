import tempfile
import unittest
from typing import Callable, Sequence, List

from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.name_and_value import NameAndValue


def get_structure(model: StringSource) -> NodeRenderer:
    return model.structure()


def get_may_depend_on_external_resources(model: StringSource) -> bool:
    return model.may_depend_on_external_resources


class GetContentsFromLinesWIteratorCheck:
    def __init__(self, put: unittest.TestCase):
        self._put = put

    def get_contents(self, model: StringSource) -> str:
        with model.as_lines as lines_iterator:
            lines = list(lines_iterator)

            lines_after_first_iteration = list(lines_iterator)
            self._put.assertEqual([], lines_after_first_iteration,
                                  'as_lines: lines after first iteration should be empty')
            return ''.join(lines)


def get_contents_from_file(model: StringSource) -> str:
    with model.as_file.open() as model_file:
        return model_file.read()


def get_contents_from_str(model: StringSource) -> str:
    return model.as_str


def get_contents_via_write_to(model: StringSource) -> str:
    with tempfile.SpooledTemporaryFile(mode='r+') as output_file:
        model.write_to(output_file)
        output_file.seek(0)
        return output_file.read()


def get_contents_from_as_lines__str(model: StringSource) -> str:
    with model.as_lines as lines:
        return ''.join(lines)


def get_contents_from_as_lines(model: StringSource) -> List[str]:
    with model.as_lines as lines:
        return list(lines)


def case__from_lines__w_iterator_check(put: unittest.TestCase) -> NameAndValue[Callable[[StringSource], str]]:
    return NameAndValue('as_lines', GetContentsFromLinesWIteratorCheck(put).get_contents)


def case__from_lines() -> NameAndValue[Callable[[StringSource], str]]:
    return NameAndValue('as_lines', get_contents_from_as_lines__str)


def case__from_str() -> NameAndValue[Callable[[StringSource], str]]:
    return NameAndValue('as_str', get_contents_from_str)


def case__from_file() -> NameAndValue[Callable[[StringSource], str]]:
    return NameAndValue('as_file', get_contents_from_file)


def case__from_write_to() -> NameAndValue[Callable[[StringSource], str]]:
    return NameAndValue('write_to', get_contents_via_write_to)


_NON_LINES_CASES = [
    case__from_str(),
    case__from_write_to(),
    case__from_file(),
]

ALL_CASES__WO_LINES_ITER_CHECK = [
    case__from_str(),
    case__from_write_to(),
    case__from_lines(),
    case__from_file(),
]


def contents_cases__str() -> Sequence[NameAndValue[Callable[[StringSource], str]]]:
    return [case__from_lines()] + _NON_LINES_CASES


def contents_cases__lines_sequence() -> Sequence[NameAndValue[Callable[[StringSource], Sequence[str]]]]:
    return (
            [NameAndValue('as_lines',
                          get_contents_from_as_lines)
             ] +
            [
                NameAndValue(
                    str_case.name,
                    lambda string_source: str_case.value(string_source).splitlines(keepends=True)
                )
                for str_case in _NON_LINES_CASES
            ]
    )
