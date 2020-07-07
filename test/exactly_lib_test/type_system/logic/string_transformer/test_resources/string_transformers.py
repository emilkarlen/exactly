import itertools
from typing import Callable, Sequence, Iterator

from exactly_lib.test_case_utils.string_models import transformed_model_from_lines
from exactly_lib.test_case_utils.string_models.transformed_model_from_lines import StringTransFun
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic import line_matcher
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.util.description_tree import renderers


class StringTransformerFromLinesTransformation(StringTransformer):
    def __init__(self,
                 name: str,
                 transformation: StringTransFun,
                 is_identity: bool = False
                 ):
        self._name = name
        self._transformation = transformation
        self._is_identity = is_identity

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_identity_transformer(self) -> bool:
        return self._is_identity

    def transform(self, model: StringModel) -> StringModel:
        return transformed_model_from_lines.TransformedStringModelFromLines(
            self._transformation,
            model
        )

    def structure(self) -> StructureRenderer:
        return renderers.header_only(self._name)


def must_not_be_used() -> StringTransformer:
    return StringTransformerFromLinesTransformation(
        'must-no-be-used',
        _raises_value_error('Must not be used'),
    )


def _raises_value_error(err_msg: str) -> StringTransFun:
    def ret_val(lines: Iterator[str]) -> Iterator[str]:
        raise ValueError(err_msg)

    return ret_val


def of_line_transformer(name: str,
                        line_transformer: Callable[[str], str],
                        ) -> StringTransformer:
    return StringTransformerFromLinesTransformation(
        name,
        lambda lines: map(line_transformer, lines)
    )


def of_line_transformer__w_preserved_line_ending(name: str,
                                                 line_transformer: Callable[[str], str],
                                                 ) -> StringTransformer:
    return of_line_transformer(
        name,
        with_preserved_new_line_ending(line_transformer)
    )


def constant(result: Sequence[str]) -> StringTransformer:
    return StringTransformerFromLinesTransformation(
        'constant-test-impl',
        lambda lines: iter(result)
    )


def identity_test_impl() -> StringTransformer:
    return StringTransformerFromLinesTransformation(
        'identity-test-impl',
        lambda lines: lines,
        is_identity=True
    )


def arbitrary_non_identity() -> StringTransformer:
    return StringTransformerFromLinesTransformation(
        'my-non-identity-transformer',
        lambda lines: map(lambda s: 'not identity', lines)
    )


def arbitrary() -> StringTransformer:
    return arbitrary_non_identity()


def delete_everything() -> StringTransformer:
    return StringTransformerFromLinesTransformation(
        'delete-everything',
        lambda lines: iter([])
    )


def every_line_empty__preserve_line_endings() -> StringTransformer:
    return of_line_transformer__w_preserved_line_ending(
        'every-line-empty',
        lambda x: ''
    )


def every_line_empty() -> StringTransformer:
    return of_line_transformer(
        'every-line-empty',
        lambda x: ''
    )


def to_uppercase() -> StringTransformer:
    return of_line_transformer(
        'to-upper',
        str.upper
    )


def count_num_uppercase_characters() -> StringTransformer:
    return StringTransformerFromLinesTransformation(
        'count-num-uppercase-characters',
        lambda lines: map(get_number_of_uppercase_characters, lines)
    )


def get_number_of_uppercase_characters(line: str) -> str:
    ret_val = 0
    for ch in line:
        if ch.isupper():
            ret_val += 1
    return str(ret_val)


def duplicate_words() -> StringTransformer:
    def do_it(line: str) -> str:
        words = line.split()
        return ' '.join(itertools.chain.from_iterable(map(lambda x: [x, x], words)))

    return StringTransformerFromLinesTransformation(
        'duplicate-words',
        lambda lines: map(with_preserved_new_line_ending(do_it), lines)
    )


def delete_initial_word() -> StringTransformer:
    def do_it(line: str) -> str:
        words = line.split()
        if words:
            del words[0]
        return ' '.join(words)

    return StringTransformerFromLinesTransformation(
        'delete-initial-word',
        lambda lines: map(with_preserved_new_line_ending(do_it), lines)
    )


def keep_single_line(line_num_to_keep: int) -> StringTransformer:
    def transform(lines: Iterator[str]) -> Iterator[str]:
        for line in enumerate(lines, line_matcher.FIRST_LINE_NUMBER):
            if line[0] == line_num_to_keep:
                yield line[1]
                break

    return StringTransformerFromLinesTransformation(
        'keep-single-line',
        transform
    )


def add_line(line_wo_ending_new_line: str) -> StringTransformer:
    def transform(lines: Iterator[str]) -> Iterator[str]:

        all_lines = list(lines)
        if all_lines:
            last_line = all_lines[-1]
            if last_line == '' or last_line[-1] != '\n':
                all_lines[-1] = last_line + '\n'

        all_lines.append(line_wo_ending_new_line + '\n')
        return iter(all_lines)

    return StringTransformerFromLinesTransformation(
        'add-line',
        transform
    )


def with_preserved_new_line_ending(new_line_agnostic_modifier: Callable[[str], str]) -> Callable[[str], str]:
    def ret_val(x: str) -> str:
        has_new_line = len(x) > 0 and x[-1] == '\n'
        if has_new_line:
            return new_line_agnostic_modifier(x[:-1]) + '\n'
        else:
            return new_line_agnostic_modifier(x)

    return ret_val
