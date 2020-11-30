from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Callable, ContextManager, IO

from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.impls import transformed_string_models
from exactly_lib.type_val_prims.impls.transformed_string_models import TransformedStringModelBase
from exactly_lib.type_val_prims.string_model.string_model import StringModel
from exactly_lib.type_val_prims.string_model.structure_builder import StringModelStructureBuilder
from exactly_lib.type_val_prims.string_transformer import StringTransformer


class StringTransformerFromLinesTransformer(StringTransformer, ABC):
    @abstractmethod
    def _transform(self, lines: Iterator[str]) -> Iterator[str]:
        pass

    @abstractmethod
    def _transformation_may_depend_on_external_resources(self) -> bool:
        pass

    def transform(self, model: StringModel) -> StringModel:
        return transformed_string_models.TransformedStringModelFromLines(
            self._transform,
            model,
            self._transformation_may_depend_on_external_resources(),
            self.structure,
        )


class TransformedStringModelFromWriter(TransformedStringModelBase):
    def __init__(self,
                 write: Callable[[StringModel, IO], None],
                 transformed: StringModel,
                 get_transformer_structure: Callable[[], StructureRenderer],
                 ):
        super().__init__(transformed)
        self._write = write
        self._file_created_on_demand = None
        self._get_transformer_structure = get_transformer_structure

    def new_structure_builder(self) -> StringModelStructureBuilder:
        return self._transformed.new_structure_builder().with_transformed_by(self._get_transformer_structure())

    @property
    def may_depend_on_external_resources(self) -> bool:
        return True

    @property
    def as_file(self) -> Path:
        if self._file_created_on_demand is None:
            self._file_created_on_demand = self._mk_file()

        return self._file_created_on_demand

    @property
    def as_str(self) -> str:
        with self.as_file.open() as f:
            return f.read()

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        with self.as_file.open() as lines:
            yield lines

    def write_to(self, output: IO):
        if self._file_created_on_demand is None:
            self._write(self._transformed, output)
        else:
            with self._file_created_on_demand.open() as f:
                output.writelines(f.readlines())

    def _mk_file(self) -> Path:
        ret_val = self._tmp_file_space.new_path('transformed')
        with ret_val.open('x') as f:
            self.write_to(f)

        return ret_val
