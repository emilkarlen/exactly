import itertools
import tempfile
import unittest
from typing import Callable, Sequence, List

from exactly_lib.type_val_prims.string_source.contents import StringSourceContents
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.name_and_value import NameAndValue

ContentsAsStrGetter = Callable[[StringSourceContents], str]
ContentsAsLinesGetter = Callable[[StringSourceContents], Sequence[str]]


def get_structure(model: StringSource) -> NodeRenderer:
    return model.structure()


def get_may_depend_on_external_resources(model: StringSourceContents) -> bool:
    return model.may_depend_on_external_resources


def get_string_source_contents(x: StringSource) -> StringSourceContents:
    return x.contents()


class GetContentsFromLinesWIteratorCheck:
    def __init__(self, put: unittest.TestCase):
        self._put = put

    def get_contents(self, model: StringSourceContents) -> str:
        with model.as_lines as lines_iterator:
            lines = list(lines_iterator)

            lines_after_first_iteration = list(lines_iterator)
            self._put.assertEqual([], lines_after_first_iteration,
                                  'as_lines: lines after first iteration should be empty')
            return ''.join(lines)


def get_contents_from_file(model: StringSourceContents) -> str:
    with model.as_file.open() as model_file:
        return model_file.read()


def get_contents_from_str(model: StringSourceContents) -> str:
    return model.as_str


def get_contents_via_write_to(model: StringSourceContents) -> str:
    with tempfile.SpooledTemporaryFile(max_size=2 ** 10, mode='r+') as output_file:
        model.write_to(output_file)
        output_file.seek(0)
        return output_file.read()


def get_contents_from_as_lines__str(model: StringSourceContents) -> str:
    with model.as_lines as lines:
        return ''.join(lines)


def get_contents_from_as_lines(model: StringSourceContents) -> List[str]:
    with model.as_lines as lines:
        return list(lines)


def case__from_lines() -> NameAndValue[Callable[[StringSourceContents], str]]:
    return NameAndValue('as_lines', get_contents_from_as_lines__str)


def case__from_str() -> NameAndValue[Callable[[StringSourceContents], str]]:
    return NameAndValue('as_str', get_contents_from_str)


def case__from_file() -> NameAndValue[Callable[[StringSourceContents], str]]:
    return NameAndValue('as_file', get_contents_from_file)


def case__from_write_to() -> NameAndValue[Callable[[StringSourceContents], str]]:
    return NameAndValue('write_to', get_contents_via_write_to)


_NON_LINES_CASES = [
    case__from_str(),
    case__from_write_to(),
    case__from_file(),
]

ALL_CASES__WO_LINES_ITER_CHECK = [case__from_lines()] + _NON_LINES_CASES


def contents_cases__str() -> Sequence[NameAndValue[ContentsAsStrGetter]]:
    return [case__from_lines()] + _NON_LINES_CASES


def contents_cases__lines_sequence() -> Sequence[NameAndValue[ContentsAsLinesGetter]]:
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


def contents_cases__first_access_is_not_write_to() -> List[NameAndValue[List[NameAndValue[ContentsAsStrGetter]]]]:
    alternative_str = case__from_str()
    alternative_lines = case__from_lines()
    alternative_file = case__from_file()
    alternative_write_to = case__from_write_to()

    alternatives_after_str = [
        alternative_lines,
        alternative_file,
        alternative_write_to,
    ]

    alternatives_after_lines = [
        alternative_str,
        alternative_file,
        alternative_write_to,
    ]

    alternatives_after_file = [
        alternative_str,
        alternative_lines,
        alternative_write_to,
    ]

    return (
            _sequences_for_alternatives_w_initial(alternative_str, alternatives_after_str) +
            _sequences_for_alternatives_w_initial(alternative_lines, alternatives_after_lines) +
            _sequences_for_alternatives_w_initial(alternative_file, alternatives_after_file)
    )


def contents_cases__all_permutations() -> List[NameAndValue[List[NameAndValue[ContentsAsStrGetter]]]]:
    return _sequences_for_alternatives([
        case__from_str(),
        case__from_lines(),
        case__from_file(),
        case__from_write_to(),
    ])


def contents_cases__2_seq_w_file_first_and_last() -> List[NameAndValue[List[NameAndValue[ContentsAsStrGetter]]]]:
    from_str = case__from_str()
    from_lines = case__from_lines()
    from_file = case__from_file()
    from_write_to = case__from_write_to()

    file_first = [
        from_file,
        from_str,
        from_lines,
        from_write_to,
    ]

    file_last = [
        from_str,
        from_lines,
        from_write_to,
        from_file,
    ]

    return [
        _sequence_from_getters(file_first),
        _sequence_from_getters(file_last),
    ]


def _sequence_from_getters(sequence: List[NameAndValue[ContentsAsStrGetter]],
                           ) -> NameAndValue[List[NameAndValue[ContentsAsStrGetter]]]:
    name = ', '.join([
        nav.name
        for nav in sequence
    ])

    return NameAndValue(
        name,
        sequence,
    )


def _sequences_for_alternatives_w_initial(initial: NameAndValue[ContentsAsStrGetter],
                                          following_alternatives: List[NameAndValue[ContentsAsStrGetter]],
                                          ) -> List[NameAndValue[List[NameAndValue[ContentsAsStrGetter]]]]:
    following_variants = itertools.permutations(following_alternatives)

    variants = [
        [initial] + list(following_variant)
        for following_variant in following_variants
    ]

    return list(map(_sequence_from_getters, variants))


def _sequences_for_alternatives(alternatives: List[NameAndValue[ContentsAsStrGetter]],
                                ) -> List[NameAndValue[List[NameAndValue[ContentsAsStrGetter]]]]:
    variants = itertools.permutations(alternatives)

    return list(map(_sequence_from_getters, variants))
