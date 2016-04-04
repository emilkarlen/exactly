from shellcheck_lib.util.textformat.structure.core import ParagraphItem


class Target:
    pass


class CrossReference(ParagraphItem):
    def __init__(self,
                 title: str,
                 target: Target):
        self._title = title
        self._target = target

    @property
    def title(self) -> str:
        return self._title

    @property
    def target(self) -> Target:
        return self._target
