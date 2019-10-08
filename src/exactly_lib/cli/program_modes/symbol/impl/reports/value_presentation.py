import pathlib
from abc import ABC
from typing import Sequence, List

from exactly_lib.cli.program_modes.symbol.impl.report import ReportBlock
from exactly_lib.definitions import file_ref, type_system
from exactly_lib.definitions.entity import types
from exactly_lib.definitions.entity.types import TypeNameAndCrossReferenceId
from exactly_lib.symbol.data.data_value_resolver import DataValueResolver
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.impl.path import described_path_resolvers
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.data.visitor import DataValueResolverPseudoVisitor
from exactly_lib.symbol.logic.file_matcher import FileMatcherResolver
from exactly_lib.symbol.logic.files_matcher import FilesMatcherResolver
from exactly_lib.symbol.logic.line_matcher import LineMatcherResolver
from exactly_lib.symbol.logic.logic_value_resolver import LogicValueResolver
from exactly_lib.symbol.logic.program.program_resolver import ProgramResolver
from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.symbol.logic.string_transformer import StringTransformerResolver
from exactly_lib.symbol.logic.visitor import LogicValueResolverPseudoVisitor
from exactly_lib.symbol.resolver_structure import SymbolValueResolver
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.symbol_usage import SymbolDefinition
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.type_system.data import path_description
from exactly_lib.type_system.description.tree_structured import WithTreeStructureDescription
from exactly_lib.type_system.logic.program.program_value import Program
from exactly_lib.util.ansi_terminal_color import ForegroundColor
from exactly_lib.util.description_tree import simple_textstruct_rendering as rendering
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.file_utils import TmpDirFileSpaceThatMustNoBeUsed
from exactly_lib.util.name import NumberOfItemsString
from exactly_lib.util.simple_textstruct import structure as text_struct
from exactly_lib.util.simple_textstruct.rendering import blocks, line_objects
from exactly_lib.util.simple_textstruct.rendering.components import MajorBlockRenderer, LineObjectRenderer
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock
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

    def block_for(self, resolver: SymbolValueResolver) -> ResolvedValuePresentationBlock:
        if isinstance(resolver, LogicValueResolver):
            constructor = _LogicTypeBlockConstructor(self._symbol_table, self._tcds)
            return constructor.visit(resolver)
        elif isinstance(resolver, DataValueResolver):
            constructor = _DataTypeBlockConstructor(self._symbol_table, self._tcds)
            return constructor.visit(resolver)
        else:
            raise TypeError('Unknown resolver type: ' + str(resolver))


class _DataTypeBlockConstructor(DataValueResolverPseudoVisitor[ResolvedValuePresentationBlock]):
    def __init__(self,
                 symbols: SymbolTable,
                 tcds: HomeAndSds,
                 ):
        self.symbols = symbols
        self.tcds = tcds

    def visit_string(self, value: StringResolver) -> ResolvedValuePresentationBlock:
        string = value.resolve(self.symbols).value_of_any_dependency(self.tcds)
        return _BlockForCustomRenderer(_StringRenderer(string))

    def visit_file_ref(self, value: FileRefResolver) -> ResolvedValuePresentationBlock:
        describer = described_path_resolvers.of(value).resolve__with_unknown_cd(self.symbols).describer
        return _of_single_line_object(line_objects.StringLineObject(describer.value.render()))

    def visit_list(self, value: ListResolver) -> ResolvedValuePresentationBlock:
        the_list = value.resolve(self.symbols).value_of_any_dependency(self.tcds)
        return _BlockForCustomRenderer(_ListRenderer(the_list))


class _LogicTypeBlockConstructor(LogicValueResolverPseudoVisitor[ResolvedValuePresentationBlock]):
    def __init__(self,
                 symbols: SymbolTable,
                 tcds: HomeAndSds,
                 ):
        self.symbols = symbols
        self.tcds = tcds

    def visit_file_matcher(self, value: FileMatcherResolver) -> ResolvedValuePresentationBlock:
        return self._of_tree_structured(value.resolve(self.symbols).value_of_any_dependency(self.tcds))

    def visit_files_matcher(self, value: FilesMatcherResolver) -> ResolvedValuePresentationBlock:
        matcher_constructor = value.resolve(self.symbols).value_of_any_dependency(self.tcds)
        matcher = matcher_constructor.construct(TmpDirFileSpaceThatMustNoBeUsed())
        return self._of_tree_structured(matcher)

    def visit_line_matcher(self, value: LineMatcherResolver) -> ResolvedValuePresentationBlock:
        return self._of_tree_structured(value.resolve(self.symbols).value_of_any_dependency(self.tcds))

    def visit_string_matcher(self, value: StringMatcherResolver) -> ResolvedValuePresentationBlock:
        return self._of_tree_structured(value.resolve(self.symbols).value_of_any_dependency(self.tcds))

    def visit_string_transformer(self, value: StringTransformerResolver) -> ResolvedValuePresentationBlock:
        return self._of_tree_structured(value.resolve(self.symbols).value_of_any_dependency(self.tcds))

    def visit_program(self, value: ProgramResolver) -> ResolvedValuePresentationBlock:
        program = value.resolve(self.symbols).value_of_any_dependency(self.tcds)
        return _BlockForCustomRenderer(_ProgramRenderer(program))

    @staticmethod
    def _of_tree_structured(x: WithTreeStructureDescription) -> ResolvedValuePresentationBlock:
        return _BlockForTree(x.structure())


class _BlockForTree(ResolvedValuePresentationBlock):
    HEADER_PROPERTIES = rendering.ElementProperties(
        text_style=text_struct.TextStyle(color=ForegroundColor.CYAN)
    )

    TREE_LAYOUT = rendering.RenderingConfiguration(
        Node.header.fget,
        lambda node_data: _BlockForTree.HEADER_PROPERTIES,
        '',
    )

    def __init__(self, tree: Node[None]):
        self._tree = tree

    def render(self) -> text_struct.MajorBlock:
        renderer = rendering.TreeRenderer(self.TREE_LAYOUT, self._tree)
        return renderer.render()


class _BlockForCustomRenderer(ResolvedValuePresentationBlock):
    def __init__(self, renderer: Renderer[MajorBlock]):
        self._renderer = renderer

    def render(self) -> text_struct.MajorBlock:
        return self._renderer.render()


def _of_single_line_object(line_renderer: LineObjectRenderer) -> ResolvedValuePresentationBlock:
    return _BlockForCustomRenderer(
        blocks.MajorBlockOfSingleLineObject(
            line_renderer
        )
    )


class _StringRenderer(MajorBlockRenderer):
    def __init__(self, x: str):
        self._x = x

    def render(self) -> MajorBlock:
        header = _type_of_x_elements_header(len(self._x),
                                            types.STRING_TYPE_INFO,
                                            type_system.NUMBER_OF_STRING_CHARACTERS)

        if len(self._x) == 0:
            return _header_only(header)
        else:
            return _header_and_value(
                header,
                [text_struct.LineElement(
                    text_struct.PreFormattedStringLineObject(self._x, False)
                )
                ],
                text_struct.ELEMENT_PROPERTIES__NEUTRAL,
            )


class _ListRenderer(MajorBlockRenderer):
    def __init__(self, the_list: List[str]):
        self._list = the_list

    def render(self) -> MajorBlock:
        header = _type_of_x_elements_header(len(self._list),
                                            types.LIST_TYPE_INFO,
                                            type_system.NUMBER_OF_LIST_ELEMENTS)
        if len(self._list) == 0:
            return _header_only(header)

        num_formatter = (
            self._format_lt_10
            if len(self._list) < 10
            else
            self._format_gte_10
        )

        value_list = [
            text_struct.LineElement(
                text_struct.StringLineObject(
                    '  '.join([num_formatter(n), elem, ]))
            )
            for n, elem in enumerate(self._list, 1)
        ]

        return _header_and_value(
            header,
            value_list,
            text_struct.ELEMENT_PROPERTIES__INDENTED,
        )

    @staticmethod
    def _format_lt_10(n: int) -> str:
        return str(n)

    @staticmethod
    def _format_gte_10(n: int) -> str:
        return '{: >2d}'.format(n)


class _ProgramRenderer(MajorBlockRenderer):
    def __init__(self, program: Program):
        self._program = program

    def render(self) -> MajorBlock:
        return text_struct.MajorBlock([
            text_struct.MinorBlock([
                text_struct.LineElement(
                    text_struct.StringLineObject('program')
                )
            ])
        ])


def _type_of_x_elements_header(num_elements: int,
                               type_name: TypeNameAndCrossReferenceId,
                               element_name: NumberOfItemsString) -> str:
    return ' '.join([
        type_name.singular_name.capitalize(),
        'of',
        element_name.of(num_elements),
    ])


def _header_and_value(header: str,
                      value: Sequence[text_struct.LineElement],
                      value_block_properties: text_struct.ElementProperties,
                      ) -> text_struct.MajorBlock:
    return text_struct.MajorBlock([
        text_struct.MinorBlock([
            text_struct.LineElement(
                text_struct.StringLineObject(header)
            )
        ]),
        text_struct.MinorBlock(
            value,
            value_block_properties,
        ),
    ])


def _header_only(header: str) -> text_struct.MajorBlock:
    return text_struct.MajorBlock([
        text_struct.MinorBlock([
            text_struct.LineElement(
                text_struct.StringLineObject(header)
            )
        ]),
    ])
