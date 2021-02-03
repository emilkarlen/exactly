from exactly_lib.common.report_rendering import header_blocks
from exactly_lib.impls.types.path import path_rendering
from exactly_lib.type_val_prims.described_path import DescribedPath
from exactly_lib.util.render import combinators
from exactly_lib.util.render.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock


def header_and_path_block(header: str, described_path: DescribedPath) -> Renderer[MajorBlock]:
    return header_blocks.w_details(
        header,
        combinators.SingletonSequenceR(
            path_rendering.minor_block_renderer_of_primitive(described_path.describer)
        )
    )
