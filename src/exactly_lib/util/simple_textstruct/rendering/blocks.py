from typing import Sequence

from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import Renderer, SequenceRenderer
from exactly_lib.util.simple_textstruct import structure
from exactly_lib.util.simple_textstruct.rendering import component_renderers as comp_rend
from exactly_lib.util.simple_textstruct.rendering.components import LineObjectRenderer
from exactly_lib.util.simple_textstruct.structure import MinorBlock, LineElement, ElementProperties, MajorBlock


class PrependFirstMinorBlockR(SequenceRenderer[MinorBlock]):
    def __init__(self,
                 to_prepend: SequenceRenderer[LineElement],
                 to_prepend_to: SequenceRenderer[MinorBlock],
                 properties_if_to_prepend_to_is_empty: ElementProperties =
                 structure.ELEMENT_PROPERTIES__NEUTRAL,
                 ):
        self.to_prepend = to_prepend
        self.to_prepend_to = to_prepend_to
        self.properties_if_to_prepend_to_is_empty = properties_if_to_prepend_to_is_empty

    def render_sequence(self) -> Sequence[MinorBlock]:
        to_prepend = self.to_prepend.render_sequence()
        to_prepend_to = self.to_prepend_to.render_sequence()

        if len(to_prepend) == 0:
            return to_prepend_to
        else:
            if len(to_prepend_to) == 0:
                return [
                    MinorBlock(to_prepend, self.properties_if_to_prepend_to_is_empty)
                ]
            else:
                to_prepend_to_list = list(to_prepend_to)
                original_first_block = to_prepend_to_list[0]
                line_elements = list(to_prepend)
                line_elements += original_first_block.parts
                to_prepend_to_list[0] = MinorBlock(line_elements,
                                                   original_first_block.properties)

                return to_prepend_to_list


class PrependFirstMinorBlockOfFirstMajorBlockR(SequenceRenderer[MajorBlock]):
    def __init__(self,
                 to_prepend: SequenceRenderer[LineElement],
                 to_prepend_to: SequenceRenderer[MajorBlock],
                 properties_if_to_prepend_to_is_empty: ElementProperties =
                 structure.ELEMENT_PROPERTIES__NEUTRAL,
                 ):
        self.to_prepend = to_prepend
        self.to_prepend_to = to_prepend_to
        self.properties_if_to_prepend_to_is_empty = properties_if_to_prepend_to_is_empty

    def render_sequence(self) -> Sequence[MajorBlock]:
        to_prepend = self.to_prepend.render_sequence()
        to_prepend_to = self.to_prepend_to.render_sequence()

        if len(to_prepend_to) == 0:
            return [
                MajorBlock([MinorBlock(to_prepend, self.properties_if_to_prepend_to_is_empty)])
            ]
        else:
            to_prepend_to_list = list(to_prepend_to)
            to_prepend_to_list[0] = MajorBlock(
                PrependFirstMinorBlockR(self.to_prepend,
                                        rend_comb.ConstantSequenceR(to_prepend_to_list[0].parts),
                                        self.properties_if_to_prepend_to_is_empty).render_sequence()
            )

            return to_prepend_to_list


class MinorBlockOfSingleLineObject(Renderer[MinorBlock]):
    def __init__(self, line_object_renderer: LineObjectRenderer):
        self._line_object_renderer = line_object_renderer

    def render(self) -> MinorBlock:
        renderer = comp_rend.MinorBlockR(
            rend_comb.SingletonSequenceR(
                comp_rend.LineElementR(self._line_object_renderer)
            )
        )
        return renderer.render()


class MinorBlocksOfSingleLineObject(SequenceRenderer[MinorBlock]):
    def __init__(self, line_object_renderer: LineObjectRenderer):
        self._line_object_renderer = line_object_renderer

    def render_sequence(self) -> Sequence[MinorBlock]:
        renderer = rend_comb.SingletonSequenceR(
            MinorBlockOfSingleLineObject(self._line_object_renderer)
        )
        return renderer.render_sequence()


class MinorBlocksOfLineElements(SequenceRenderer[MinorBlock]):
    def __init__(self, line_elements_renderer: SequenceRenderer[LineElement]):
        self._line_elements_renderer = line_elements_renderer

    def render_sequence(self) -> Sequence[MinorBlock]:
        renderer = rend_comb.SingletonSequenceR(
            comp_rend.MinorBlockR(self._line_elements_renderer)
        )
        return renderer.render()


class MajorBlockOfSingleLineObject(Renderer[MajorBlock]):
    def __init__(self, line_object_renderer: LineObjectRenderer):
        self._line_object_renderer = line_object_renderer

    def render(self) -> MajorBlock:
        renderer = comp_rend.MajorBlockR(
            rend_comb.SingletonSequenceR(
                MinorBlockOfSingleLineObject(self._line_object_renderer)
            )
        )
        return renderer.render()


class MajorBlocksOfSingleLineObject(SequenceRenderer[MajorBlock]):
    def __init__(self, line_object_renderer: LineObjectRenderer):
        self._line_object_renderer = line_object_renderer

    def render_sequence(self) -> Sequence[MajorBlock]:
        renderer = rend_comb.SingletonSequenceR(
            MajorBlockOfSingleLineObject(self._line_object_renderer)
        )
        return renderer.render_sequence()


class MajorBlocksOfLineElements(SequenceRenderer[MajorBlock]):
    def __init__(self, line_elements_renderer: SequenceRenderer[LineElement]):
        self._line_elements_renderer = line_elements_renderer

    def render_sequence(self) -> Sequence[MajorBlock]:
        renderer = rend_comb.SingletonSequenceR(
            comp_rend.MajorBlockR(MinorBlocksOfLineElements(self._line_elements_renderer))
        )
        return renderer.render()
