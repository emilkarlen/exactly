from abc import ABC, abstractmethod
from pathlib import Path
from typing import ContextManager, Iterator, IO, Tuple, Sequence

from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.type_val_prims.description.tree_structured import WithTreeStructureDescription, StructureRenderer
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import DetailsRenderer, NodeRenderer
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.str_ import read_lines


class StringModelStructureBuilder:
    def __init__(self,
                 header: str,
                 details: Sequence[DetailsRenderer],
                 children: Sequence[StructureRenderer] = (),
                 ):
        self._header = header
        self._details = details
        self._children = children

    @staticmethod
    def of_details(header: str,
                   details: Sequence[DetailsRenderer],
                   ) -> 'StringModelStructureBuilder':
        return StringModelStructureBuilder(header, details, ())

    def build(self) -> StructureRenderer:
        return renderers.NodeRendererFromParts(self._header, None, self._details, self._children)

    def with_transformed_by(self, transformer: StructureRenderer) -> 'StringModelStructureBuilder':
        transformation_renderer = renderers.NodeRendererFromParts(
            string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION,
            None,
            (),
            (transformer,),
        )
        return StringModelStructureBuilder(
            self._header,
            self._details,
            tuple(self._children) + (transformation_renderer,),
        )


class StringModel(WithTreeStructureDescription, ABC):
    """Access to a string in various forms.

    The string is backed by a constant "string source".
    The string is constant, unless the "string source" may give different result
    at different times - e.g. an external program.

    The public methods are just different kind of access to the same string.

    Maybe a "freeze" method should be added to store the string in a file (if needed),
    to guarantee that the string is constant, even over time.
    """

    @abstractmethod
    def new_structure_builder(self) -> StringModelStructureBuilder:
        """"Gives a new object, for each invokation"""
        pass

    def structure(self) -> StructureRenderer:
        """Should (probably) not be overloaded."""
        return _StructureRendererOfStringModel(self)

    @property
    @abstractmethod
    def may_depend_on_external_resources(self) -> bool:
        """
        Tells if the model probably depends on (heavy) resources such as
         - files
         - program execution

        If this method gives False - it should be relatively cheap to
        access it using func:`as_str`, for example.

        The return value is allowed to vary over time - model may become
        independent on external resources by caching, e.g.

        The name is intentionally vague, so that an implementation
        can give True, even if it cannot guarantee that there are
        such dependencies.
        The idea is that an implementation should give False iff
        it can guarantee that there are no (heavy) external resources.
        """
        pass

    @property
    def as_str(self) -> str:
        """
        See also :func:`may_depend_on_external_resources`

        :raises HardErrorException: Detected error
        """
        with self.as_lines as lines:
            return ''.join(lines)

    @property
    @abstractmethod
    def as_file(self) -> Path:
        """
        Gives a path to a file with contents that has been transformed using the transformer.

        The path must not be modified on disk, neither its name nor its contents
        (unless the user is sure the file is not used in other contexts).

        The path may be read-only.

        :raises HardErrorException: Detected error
        """
        pass

    @property
    @abstractmethod
    def as_lines(self) -> ContextManager[Iterator[str]]:
        """
        The string as a sequence of lines.

        New-line characters are included.

        :raises HardErrorException: Detected error
        """
        pass

    def write_to(self, output: IO):
        """
        Writes the string to a file.

        :raises HardErrorException: Detected error
        """
        with self.as_lines as lines:
            output.writelines(lines)

    @property
    @abstractmethod
    def _tmp_file_space(self) -> DirFileSpace:
        """Protected method - accessible by sub classes."""
        pass


class _StructureRendererOfStringModel(NodeRenderer[None]):
    def __init__(self, string_model: StringModel):
        self._string_model = string_model

    def render(self) -> Node[None]:
        return self._string_model.new_structure_builder().build().render()


def read_lines_as_str__w_minimum_num_chars(min_num_chars_to_read: int, model: StringModel) -> Tuple[str, bool]:
    """
    :return: string read, source-may-have-more-contents
    """
    with model.as_lines as lines:
        return read_lines.read_lines_as_str__w_minimum_num_chars(min_num_chars_to_read, lines)
