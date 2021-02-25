from abc import ABC
from typing import Sequence

from exactly_lib.cli.program_modes.symbol.impl.report import ReportBlock
from exactly_lib.common.report_rendering.description_tree import rendering__node_wo_data
from exactly_lib.definitions import type_system
from exactly_lib.definitions.entity import types
from exactly_lib.definitions.type_system import TypeNameAndCrossReferenceId
from exactly_lib.symbol.sdv_structure import SymbolDefinition, SymbolDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.full_deps.ddv import FullDepsDdv
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.sdv import FullDepsSdv
from exactly_lib.type_val_deps.dep_variants.sdv.w_str_rend.sdv_type import DataTypeSdv
from exactly_lib.type_val_deps.dep_variants.sdv.w_str_rend.sdv_visitor import WStrRenderingTypeSdvPseudoVisitor
from exactly_lib.type_val_deps.types.list_.list_sdv import ListSdv
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.type_val_prims.description.logic_description import DescriptionVisitor, DetailsDescription, \
    NodeDescription
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.render.renderer import Renderer, SequenceRenderer
from exactly_lib.util.simple_textstruct import structure as text_struct
from exactly_lib.util.simple_textstruct.rendering import blocks, line_objects
from exactly_lib.util.simple_textstruct.rendering.components import MajorBlockRenderer, LineObjectRenderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock
from exactly_lib.util.str_.name import NumberOfItemsString
from exactly_lib.util.symbol_table import SymbolTable


class ResolvedValuePresentationBlock(ReportBlock, ABC):
    pass


class PresentationBlockConstructor:
    def __init__(self,
                 all_definitions: Sequence[SymbolDefinition],
                 builtin_symbols: SymbolTable):
        self._symbol_table = SymbolTable({
            definition.name: definition.symbol_container
            for definition in all_definitions
        })
        self._symbol_table.add_table(builtin_symbols)

    def block_for(self, sdv: SymbolDependentValue) -> ResolvedValuePresentationBlock:
        if isinstance(sdv, FullDepsSdv):
            return _of_full_deps(sdv.resolve(self._symbol_table))
        elif isinstance(sdv, DataTypeSdv):
            constructor = _WStrRenderingTypeBlockConstructor(self._symbol_table)
            return constructor.visit(sdv)
        else:
            raise TypeError('Unknown {} type: {}'.format(str(SymbolDependentValue), str(sdv)))


class _WStrRenderingTypeBlockConstructor(WStrRenderingTypeSdvPseudoVisitor[ResolvedValuePresentationBlock]):
    def __init__(self, symbols: SymbolTable):
        self.symbols = symbols

    def visit_string(self, value: StringSdv) -> ResolvedValuePresentationBlock:
        return _BlockForCustomRenderer(_StringRenderer(value.resolve(self.symbols).describer()))

    def visit_path(self, value: PathSdv) -> ResolvedValuePresentationBlock:
        describer = value.resolve(self.symbols).describer()
        return _of_single_line_object(line_objects.StringLineObject(describer.value.render()))

    def visit_list(self, value: ListSdv) -> ResolvedValuePresentationBlock:
        return _BlockForCustomRenderer(_ListRenderer(value.resolve(self.symbols).describer()))


def _of_full_deps(ddv: FullDepsDdv) -> ResolvedValuePresentationBlock:
    return ddv.description().accept(_LogicValueDescriptionRenderer())


class _LogicValueDescriptionRenderer(DescriptionVisitor[ResolvedValuePresentationBlock]):
    def visit_node(self, description: NodeDescription) -> ResolvedValuePresentationBlock:
        return _BlockForNode(description.structure())

    def visit_details(self, description: DetailsDescription) -> ResolvedValuePresentationBlock:
        return _BlockForDetails(description.details())


class _BlockForNode(ResolvedValuePresentationBlock):
    def __init__(self, tree: StructureRenderer):
        self._tree = tree

    def render(self) -> text_struct.MajorBlock:
        return rendering__node_wo_data.NodeAsMajorBlockRenderer(self._tree).render()


class _BlockForDetails(ResolvedValuePresentationBlock):
    def __init__(self, details: DetailsRenderer):
        self._details = details

    def render(self) -> text_struct.MajorBlock:
        return rendering__node_wo_data.DetailsAsMajorBlockRenderer(self._details).render()


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
    def __init__(self, x: Renderer[str]):
        self._x = x

    def render(self) -> MajorBlock:
        s = self._x.render()
        header = _type_of_x_elements_header(len(s),
                                            types.STRING_TYPE_INFO,
                                            type_system.NUMBER_OF_STRING_CHARACTERS)

        if len(s) == 0:
            return _header_only(header)
        else:
            return _header_and_value(
                header,
                [text_struct.LineElement(
                    text_struct.PreFormattedStringLineObject(s, False)
                )
                ],
                text_struct.ELEMENT_PROPERTIES__NEUTRAL,
            )


class _ListRenderer(MajorBlockRenderer):
    def __init__(self, the_list: SequenceRenderer[str]):
        self._list = the_list

    def render(self) -> MajorBlock:
        the_list = self._list.render_sequence()
        header = _type_of_x_elements_header(len(the_list),
                                            types.LIST_TYPE_INFO,
                                            type_system.NUMBER_OF_LIST_ELEMENTS)
        if len(the_list) == 0:
            return _header_only(header)

        num_formatter = (
            self._format_lt_10
            if len(the_list) < 10
            else
            self._format_gte_10
        )

        value_list = [
            text_struct.LineElement(
                text_struct.StringLineObject(
                    '  '.join([num_formatter(n), elem, ]))
            )
            for n, elem in enumerate(the_list, 1)
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
