from shellcheck_lib.help.program_modes.test_suite.contents_structure import TestSuiteHelp, TestSuiteSectionHelp
from shellcheck_lib.help.utils.render import SectionContentsRenderer, RenderingEnvironment
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure.structures import paras


class OverviewRenderer(SectionContentsRenderer):
    def __init__(self, suite_help: TestSuiteHelp):
        self.suite_help = suite_help

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return doc.SectionContents(paras('TODO: test suite overview help'), [])


class SectionRenderer(SectionContentsRenderer):
    def __init__(self, section_help: TestSuiteSectionHelp):
        self.section_help = section_help

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return doc.SectionContents(paras('TODO suite help for section ' + self.section_help.name),
                                   [])
