from pathlib import Path

from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer


class Constant(Renderer[str]):
    def __init__(self, path: Path):
        self._path = path

    def render(self) -> str:
        return str(self._path)
