from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager, Iterator, Sequence, List

from exactly_lib.test_case_utils.string_models.model_from_lines import StringModelFromLinesBase
from exactly_lib.type_system.logic.string_model import TmpFilePathGenerator, StringModel


class StringModelFromLines(StringModelFromLinesBase):
    def __init__(self,
                 value: Sequence[str],
                 tmp_file_path_generator: TmpFilePathGenerator,
                 ):
        super().__init__()
        self._value = value
        self._tmp_file_path_generator = tmp_file_path_generator

    @property
    def _path_generator(self) -> TmpFilePathGenerator:
        return self._tmp_file_path_generator

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        yield iter(self._value)


class TmpFilePathGeneratorThatMustNotBeUsed(TmpFilePathGenerator):
    def new_path(self) -> Path:
        raise ValueError('unsupported')


def of_lines(
        lines: Sequence[str],
        tmp_file_path_generator: TmpFilePathGenerator = TmpFilePathGeneratorThatMustNotBeUsed(),
) -> StringModel:
    return StringModelFromLines(
        lines,
        tmp_file_path_generator,
    )


def of_string(
        contents: str,
        tmp_file_path_generator: TmpFilePathGenerator = TmpFilePathGeneratorThatMustNotBeUsed(),
) -> StringModel:
    return StringModelFromLines(
        contents.splitlines(keepends=True),
        tmp_file_path_generator,
    )


def as_lines_list(model: StringModel) -> List[str]:
    with model.as_lines as lines:
        return list(lines)


def as_string(model: StringModel) -> str:
    with model.as_lines as lines:
        return ''.join(lines)
