from pathlib import Path

from exactly_lib.util.render.renderer import Renderer


class Constant(Renderer[str]):
    def __init__(self, path: Path):
        self._path = path

    def render(self) -> str:
        return str(self._path)
