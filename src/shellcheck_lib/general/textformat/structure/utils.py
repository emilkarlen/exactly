from shellcheck_lib.general.textformat.structure.core import ParagraphItem
from shellcheck_lib.general.textformat.structure.lists import HeaderValueList
from shellcheck_lib.general.textformat.structure.paragraph import Paragraph


class ParagraphItemVisitor:
    def visit(self, item: ParagraphItem):
        if isinstance(item, Paragraph):
            return self.visit_paragraph(item)
        if isinstance(item, HeaderValueList):
            return self.visit_header_value_list(item)
        raise ValueError('Unknown {}: {}'.format(ParagraphItem.__name__, str(type(item))))

    def visit_paragraph(self, paragraph: Paragraph):
        raise NotImplemented()

    def visit_header_value_list(self, header_value_list: HeaderValueList):
        raise NotImplemented()
