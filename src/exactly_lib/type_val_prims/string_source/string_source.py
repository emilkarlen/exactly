from abc import ABC, abstractmethod
from typing import Tuple

from exactly_lib.type_val_prims.description.tree_structured import WithNodeDescription, StructureRenderer
from exactly_lib.type_val_prims.string_source.contents import StringSourceContents
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Node
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

        The method can be invoked arbitrary number of times.  But usually only the first invocation
        should have any effect.
        """
        pass

    @abstractmethod
    def contents(self) -> StringSourceContents:
        """Gives the contents that this object represents.

        The returned object may change over time - especially before
        and after freezing.
        Thus the returned object must not be stored as
        a constant representation of the StringSource's contents.

        Invoking this method should not take part in generating the actual
        contents (accessed via the returned object's methods).
        Especially should no Hard Error exceptions occur.
        This allows this method to be used while cheaply constructing variants
        of the contents, before it is known whether the actual contents
        will ever be used or not.
        """
        pass


class _StructureRendererOfStringSource(NodeRenderer[None]):
    def __init__(self, string_source: StringSource):
        self._string_source = string_source

    def render(self) -> Node[None]:
        return self._string_source.new_structure_builder().build().render()


def read_lines_as_str__w_minimum_num_chars(min_num_chars_to_read: int,
                                           source: StringSourceContents) -> Tuple[str, bool]:
    """
    :return: string read, source-may-have-more-contents
    """
    with source.as_lines as lines:
        return read_lines.read_lines_as_str__w_minimum_num_chars(min_num_chars_to_read, lines)
