from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation
from exactly_lib.help.program_modes.test_suite.contents_structure import TestSuiteHelp
from exactly_lib.help.utils.render import SectionContentsRenderer, RenderingEnvironment
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.structures import paras


class OverviewRenderer(SectionContentsRenderer):
    def __init__(self, suite_help: TestSuiteHelp):
        self.suite_help = suite_help

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return doc.SectionContents(paras('TODO: test suite overview help'), [])


class SectionRenderer(SectionContentsRenderer):
    def __init__(self, section_help: SectionDocumentation):
        self.section_help = section_help

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return self.section_help.render(environment)
