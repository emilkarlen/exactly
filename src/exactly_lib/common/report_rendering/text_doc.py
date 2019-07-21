from typing import Sequence

from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock

TextRenderer = Renderer[Sequence[MajorBlock]]

MinorTextRenderer = Renderer[Sequence[MinorBlock]]
