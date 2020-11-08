from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager, Iterator

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.description_tree import custom_details
from exactly_lib.type_val_deps.types.path import primitives
from exactly_lib.type_val_prims.described_path import DescribedPath
from exactly_lib.type_val_prims.path_describer import PathDescriberForPrimitive
from exactly_lib.type_val_prims.string_model import StringModel, StringModelStructureBuilder
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace


def string_model_of_file__poorly_described(file: Path,
                                           tmp_file_space: DirFileSpace) -> StringModel:
    return StringModelOfFile(file, primitives.poor_describer(file), tmp_file_space)


def string_model_of_file__described(path: DescribedPath,
                                    tmp_file_space: DirFileSpace) -> StringModel:
    return StringModelOfFile(path.primitive, path.describer, tmp_file_space)


class StringModelOfFile(StringModel):
    def __init__(self,
                 path: Path,
                 describer: PathDescriberForPrimitive,
                 tmp_file_space: DirFileSpace,
                 ):
        """
        :param path: An existing regular file (that is readable).
        """
        self._path = path
        self._describer = describer
        self.__tmp_file_space = tmp_file_space

    @staticmethod
    def structure_builder_for(path: DetailsRenderer) -> StringModelStructureBuilder:
        return StringModelStructureBuilder.of_details(
            syntax_elements.PATH_SYNTAX_ELEMENT.singular_name,
            (path,),
        )

    def new_structure_builder(self) -> StringModelStructureBuilder:
        return self.structure_builder_for(
            custom_details.path_primitive_details_renderer(self._describer)
        )

    @property
    def may_depend_on_external_resources(self) -> bool:
        return True

    @property
    def as_str(self) -> str:
        with self._path.open() as f:
            return f.read()

    @property
    def as_file(self) -> Path:
        return self._path

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        with self.as_file.open() as lines:
            yield lines

    @property
    def _tmp_file_space(self) -> DirFileSpace:
        return self.__tmp_file_space
