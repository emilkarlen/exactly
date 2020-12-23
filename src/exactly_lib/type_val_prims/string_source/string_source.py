from abc import ABC, abstractmethod
from pathlib import Path
from typing import ContextManager, Iterator, IO, Tuple

from exactly_lib.type_val_prims.description.tree_structured import WithNodeDescription, StructureRenderer
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.str_ import read_lines


class StringSource(WithNodeDescription, ABC):
    """Access to a string in various forms.

    The string is backed by a constant "string source".
    The string is constant, unless the "string source" may give different result
    at different times - e.g. an external program.

    The public methods are just different kind of access to the same string.

    Maybe a "freeze" method should be added to store the string in a file (if needed),
    to guarantee that the string is constant, even over time.
    """

    @abstractmethod
    def new_structure_builder(self) -> StringSourceStructureBuilder:
        """"Gives a new object, for each invokation"""
        pass

    def structure(self) -> StructureRenderer:
        """Should (probably) not be overloaded."""
        return _StructureRendererOfStringSource(self)

    @abstractmethod
    def freeze(self):
        """Freezes the contents of the model, to the contents generated
        the first invocations of any of the contents getters.

        For example, freezing an object guarantees that external processes (influencing the contents)
        will only be invoked once after the call to this method.

        The method should not generate contents by itself - to avoid generating
        contents that is not needed.  The freezing just assures that the contents
        will be generated once, and then "shared" by all of the contents getters.

        The implementation should not involve any "external" resources (such as files and processes).

        This method is an opportunity for optimizations, since it signals that
        the object will be used multiple times.

        The method can be invoked arbitrary number of times.
        """
        pass

    @property
    @abstractmethod
    def may_depend_on_external_resources(self) -> bool:
        """
        Tells if the model probably depends on (heavy) resources such as
         - files
         - program execution

        If this method gives False - it should be relatively cheap to
        access it using func:`as_str`, for example.

        The return value is allowed to vary over time - the source may become
        independent on external resources by freezing, caching, e.g.

        The name is intentionally vague, so that an implementation
        can give True, even if it cannot guarantee that there are
        such dependencies.
        The idea is that an implementation should give False iff
        it can guarantee that there are no (heavy) external resources.

        :raises HardErrorException: Detected error
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


class _StructureRendererOfStringSource(NodeRenderer[None]):
    def __init__(self, string_source: StringSource):
        self._string_source = string_source

    def render(self) -> Node[None]:
        return self._string_source.new_structure_builder().build().render()


def read_lines_as_str__w_minimum_num_chars(min_num_chars_to_read: int, source: StringSource) -> Tuple[str, bool]:
    """
    :return: string read, source-may-have-more-contents
    """
    with source.as_lines as lines:
        return read_lines.read_lines_as_str__w_minimum_num_chars(min_num_chars_to_read, lines)
