from abc import ABC

from exactly_lib.util.simple_textstruct.structure import Document


class TraceDocRender(ABC):
    """Functionality to render itself as a :class:Document"""

    def render(self) -> Document:
        pass
