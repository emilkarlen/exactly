from exactly_lib.help.suite_reporters.contents_structure import SuiteReporterDocumentation
from exactly_lib.help.utils.entity_documentation import AllEntitiesListRenderer
from exactly_lib.help.utils.render import SectionContentsRenderer, RenderingEnvironment
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs


def all_suite_reporters_list_renderer(all_suite_reporters: list) -> SectionContentsRenderer:
    return AllEntitiesListRenderer(lambda suite_reporter: docs.paras(suite_reporter.single_line_description()),
                                   all_suite_reporters)


class IndividualSuiteReporterRenderer(SectionContentsRenderer):
    def __init__(self, suite_reporter: SuiteReporterDocumentation):
        self.suite_reporter = suite_reporter
        self.rendering_environment = None

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        self.rendering_environment = environment
        initial_paragraphs = [docs.para(self.suite_reporter.single_line_description())]
        sub_sections = []
        return doc.SectionContents(initial_paragraphs, sub_sections)
