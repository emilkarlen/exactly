from shellcheck_lib.util.textformat.structure import document as doc


class SectionContentsRenderer:
    def apply(self) -> doc.SectionContents:
        raise NotImplementedError()
