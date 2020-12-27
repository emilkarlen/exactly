from pathlib import Path

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.description_tree import custom_details
from exactly_lib.impls.types.string_source.contents.contents_of_existing_path import \
    StringSourceContentsOfExistingPath
from exactly_lib.type_val_deps.types.path import primitives
from exactly_lib.type_val_prims.described_path import DescribedPath
from exactly_lib.type_val_prims.path_describer import PathDescriberForPrimitive
from exactly_lib.type_val_prims.string_source.contents import StringSourceContents
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace


def string_source_of_file__poorly_described(file: Path,
                                            tmp_file_space: DirFileSpace) -> StringSource:
    return StringSourceOfFile(file, primitives.poor_describer(file), tmp_file_space)


def string_source_of_file__described(path: DescribedPath,
                                     tmp_file_space: DirFileSpace) -> StringSource:
    return StringSourceOfFile(path.primitive, path.describer, tmp_file_space)


class StringSourceOfFile(StringSource):
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
        self._contents = StringSourceContentsOfExistingPath(
            path,
            tmp_file_space,
        )

    @staticmethod
    def structure_builder_for(path: DetailsRenderer) -> StringSourceStructureBuilder:
        return StringSourceStructureBuilder.of_details(
            syntax_elements.PATH_SYNTAX_ELEMENT.singular_name,
            (path,),
        )

    def new_structure_builder(self) -> StringSourceStructureBuilder:
        return self.structure_builder_for(
            custom_details.path_primitive_details_renderer(self._describer)
        )

    def contents(self) -> StringSourceContents:
        return self._contents

    def freeze(self):
        pass
