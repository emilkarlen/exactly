from exactly_lib.help.suite_reporters.contents_structure import SuiteReporterDocumentation
from exactly_lib.help.utils.doc_utils import append_sections_if_contents_is_non_empty
from exactly_lib.help.utils.entity_documentation import AllEntitiesListRenderer
from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
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
        srd = self.suite_reporter
        initial_paragraphs = [docs.para(srd.single_line_description())]
        initial_paragraphs.extend(srd.main_description_rest())
        sub_sections = []
        names_and_contents = [
            ('Output syntax', srd.syntax_of_output()),
            ('Exit code', srd.exit_code_description()),
        ]
        append_sections_if_contents_is_non_empty(sub_sections, names_and_contents)
        return doc.SectionContents(initial_paragraphs, sub_sections)
