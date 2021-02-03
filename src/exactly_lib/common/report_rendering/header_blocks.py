from exactly_lib.impls.text_render import header_rendering
from exactly_lib.util.render import combinators
from exactly_lib.util.render.renderer import SequenceRenderer, Renderer
from exactly_lib.util.simple_textstruct.rendering import component_renderers as comp_rend
from exactly_lib.util.simple_textstruct.structure import MinorBlock, MajorBlock


def w_details(header: str, details: SequenceRenderer[MinorBlock]) -> Renderer[MajorBlock]:
    return comp_rend.MajorBlockR(
        combinators.PrependR(
            header_rendering.SimpleHeaderMinorBlockRenderer(header),
            combinators.Indented(details)
        )
    )
