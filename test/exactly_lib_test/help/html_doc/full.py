import io
import unittest
from typing import List, Sequence, Dict

from exactly_lib.cli_default.program_modes import test_suite as test_suite_default_setup
from exactly_lib.cli_default.program_modes.test_case import default_instructions_setup
from exactly_lib.help.html_doc import main as sut
from exactly_lib.help.html_doc.cross_ref_target_renderer import HtmlTargetRenderer
from exactly_lib.help.the_application_help import new_application_help
from exactly_lib.util.textformat.rendering.html.document import DOCTYPE_XHTML1_0
from exactly_lib.util.textformat.structure import core
from exactly_lib.util.textformat.structure.core import CrossReferenceTarget, ParagraphItem, UrlCrossReferenceTarget
from exactly_lib.util.textformat.structure.document import SectionContents, SectionItemVisitor, Article, Section, \
    SectionItem
from exactly_lib.util.textformat.structure.lists import HeaderContentList
from exactly_lib.util.textformat.structure.literal_layout import LiteralLayout
from exactly_lib.util.textformat.structure.paragraph import Paragraph
from exactly_lib.util.textformat.structure.table import Table
from exactly_lib.util.textformat.structure.utils import ParagraphItemVisitor
from exactly_lib_test.processing.test_resources.instruction_set import instruction_set
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion_str import begins_with
from exactly_lib_test.test_suite.test_resources.configuration_section_instructions import \
    CONFIGURATION_SECTION_INSTRUCTIONS
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestHtmlDoc)


class TestHtmlDoc(unittest.TestCase):
    TEST_CASE_INSTRUCTION_SET = instruction_set()
    TEST_SUITE_CONFIGURATION_SECTION_INSTRUCTIONS = CONFIGURATION_SECTION_INSTRUCTIONS

    def test_that_html_doc_renderer_returns_valid_section_contents(self):
        # ARRANGE #
        application_help = new_application_help(self.TEST_CASE_INSTRUCTION_SET,
                                                self.TEST_SUITE_CONFIGURATION_SECTION_INSTRUCTIONS)
        # ACT #
        actual = sut.section_contents(application_help)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)

    def test_generate_and_output_SHOULD_output_xhtml(self):
        # ARRANGE #
        application_help = new_application_help(self.TEST_CASE_INSTRUCTION_SET,
                                                self.TEST_SUITE_CONFIGURATION_SECTION_INSTRUCTIONS)
        output_file = io.StringIO()
        # ACT #
        sut.generate_and_output(output_file, application_help)
        # ASSERT #
        actual_output = output_file.getvalue()
        begins_with(DOCTYPE_XHTML1_0).apply(self, actual_output, asrt.MessageBuilder('file output'))

    def test_anchors_and_references(self):
        # ARRANGE #

        application_help = new_application_help(default_instructions_setup.INSTRUCTIONS_SETUP,
                                                test_suite_default_setup.CONFIGURATION_SECTION_INSTRUCTIONS)
        # ACT #
        actual_section_contents = sut.section_contents(application_help)
        # ASSERT #
        collector = _SectionItemAnchorsCollector([], [])

        collector.handle_section_contents(actual_section_contents)

        target_renderer = HtmlTargetRenderer()

        anchors = [target_renderer.visit(t)
                   for t in collector.anchors
                   if _is_internal_target(t)
                   ]
        references = [
            target_renderer.visit(t)
            for t in collector.references
            if _is_internal_target(t)
        ]

        anchor_2_num_defs = count_elements(anchors)

        # Every anchor must be used only once
        for t, n in anchor_2_num_defs.items():
            self.assertEqual(1, n, t)

        # Every reference must have a corresponding anchor
        for r in references:
            self.assertTrue(r in anchor_2_num_defs,
                            r)


def count_elements(elements: Sequence[str]) -> Dict[str, int]:
    ret_val = dict()

    for e in elements:
        num_reg = ret_val.get(e, 0)
        ret_val[e] = num_reg + 1

    return ret_val


class _TextAnchorsCollector(core.TextVisitor):
    def __init__(self,
                 anchors: List[CrossReferenceTarget],
                 references: List[CrossReferenceTarget],
                 ):
        self.anchors = anchors
        self.references = references

    def visit_string(self, text: core.StringText):
        pass

    def visit_cross_reference(self, text: core.CrossReferenceText):
        self.references.append(text.target)

    def visit_anchor(self, text: core.AnchorText):
        self.anchors.append(text.anchor)

    def accept_sequence(self, items: Sequence[core.Text]):
        for ti in items:
            ti.accept(self)


class _ParagraphItemAnchorsCollector(ParagraphItemVisitor):
    def __init__(self,
                 anchors: List[CrossReferenceTarget],
                 text_handler: _TextAnchorsCollector,
                 ):
        self.anchors = anchors
        self.text_handler = text_handler

    def visit_paragraph(self, paragraph: Paragraph):
        self.text_handler.accept_sequence(paragraph.start_on_new_line_blocks)

    def visit_header_value_list(self, header_value_list: HeaderContentList):
        for item in header_value_list.items:
            item.header.accept(self.text_handler)
            self.accept_sequence(item.content_paragraph_items)

    def visit_literal_layout(self, x: LiteralLayout):
        pass

    def visit_table(self, table: Table):
        for row in table.rows:
            for cell in row:
                self.accept_sequence(cell.paragraph_items)

    def accept_sequence(self, items: Sequence[ParagraphItem]):
        for pi in items:
            self.visit(pi)


class _SectionItemAnchorsCollector(SectionItemVisitor[None]):
    def __init__(self,
                 anchors: List[CrossReferenceTarget],
                 references: List[CrossReferenceTarget],
                 ):
        self.anchors = anchors
        self.references = references
        self.text_handler = _TextAnchorsCollector(anchors, references)
        self.paragraph_handler = _ParagraphItemAnchorsCollector(anchors, self.text_handler)

    def visit_section(self, section: Section):
        self._handle_common(section, section.contents)

    def visit_article(self, article: Article):
        self._handle_common(article, article.contents.section_contents)
        self.paragraph_handler.accept_sequence(article.contents.abstract_paragraphs)

    def _handle_common(self, x: SectionItem,
                       section_contents: SectionContents):
        if x.target:
            self.anchors.append(x.target)
        x.header.accept(self.text_handler)
        self.handle_section_contents(section_contents)

    def handle_section_contents(self, section_contents: SectionContents):
        self.paragraph_handler.accept_sequence(section_contents.initial_paragraphs)
        self.accept_sequence(section_contents.sections)

    def accept_sequence(self, items: Sequence[SectionItem]):
        for si in items:
            si.accept(self)


def _is_internal_target(target: CrossReferenceTarget) -> bool:
    return not isinstance(target, UrlCrossReferenceTarget)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
