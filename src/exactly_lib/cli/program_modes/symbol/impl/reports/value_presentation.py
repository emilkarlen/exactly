import pathlib
from abc import ABC
from typing import Optional, Sequence

from exactly_lib.cli.program_modes.symbol.impl.report import ReportBlock
from exactly_lib.definitions import file_ref
from exactly_lib.symbol.logic.file_matcher import FileMatcherResolver
from exactly_lib.symbol.resolver_structure import SymbolValueResolver
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.symbol_usage import SymbolDefinition
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.type_system.data import path_description
from exactly_lib.type_system.description.tree_structured import WithTreeStructureDescription
from exactly_lib.util.ansi_terminal_color import ForegroundColor
from exactly_lib.util.description_tree import simple_textstruct_rendering as rendering
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.simple_textstruct import structure  as text_struct
from exactly_lib.util.symbol_table import SymbolTable


class ResolvedValuePresentationBlock(ReportBlock, ABC):
    pass


class PresentationBlockConstructor:
    def __init__(self, all_definitions: Sequence[SymbolDefinition]):
        self._symbol_table = SymbolTable({
            definition.name: definition.resolver_container
            for definition in all_definitions
        })
        self._tcds = HomeAndSds(
            HomeDirectoryStructure(
                pathlib.Path(symbol_reference_syntax_for_name(file_ref.EXACTLY_DIR__REL_HOME_CASE)),
                pathlib.Path(symbol_reference_syntax_for_name(file_ref.EXACTLY_DIR__REL_HOME_CASE)),
            ),
            SandboxDirectoryStructure(path_description.EXACTLY_SANDBOX_ROOT_DIR_NAME)
        )

    def block_for(self, resolver: SymbolValueResolver) -> Optional[ResolvedValuePresentationBlock]:
        if isinstance(resolver, FileMatcherResolver):
            return self._of_file_matcher(resolver)
        else:
            return None

    def _of_file_matcher(self, resolver: FileMatcherResolver) -> ResolvedValuePresentationBlock:
        ddv = resolver.resolve(self._symbol_table)
        return self._of_tree_structured(ddv.value_of_any_dependency(self._tcds))

    @staticmethod
    def _of_tree_structured(x: WithTreeStructureDescription) -> ResolvedValuePresentationBlock:
        return _BlockForTree(x.structure())


class _BlockForTree(ResolvedValuePresentationBlock):
    def __init__(self, tree: Node[None]):
        self._tree = tree

    def render(self) -> text_struct.MajorBlock:
        renderer = rendering.TreeRenderer(_TREE_LAYOUT, self._tree)
        return renderer.render()


_TREE_LAYOUT = rendering.RenderingConfiguration(
    Node.header.fget,
    lambda node_data: _HEADER_PROPERTIES,
    '',
)

_HEADER_PROPERTIES = rendering.ElementProperties(
    text_style=text_struct.TextStyle(color=ForegroundColor.CYAN)
)
