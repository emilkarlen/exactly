from exactly_lib.help.entities.suite_reporters.contents_structure import SuiteReporterDocumentation
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.help.utils.rendering.see_also_section import see_also_sections
from exactly_lib.help_texts.entity.suite_reporters import DEFAULT_REPORTER
from exactly_lib.help_texts.entity_names import SUITE_REPORTER_ENTITY_TYPE_NAME
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.utils import append_sections_if_contents_is_non_empty


class IndividualSuiteReporterRenderer(SectionContentsRenderer):
    def __init__(self, suite_reporter: SuiteReporterDocumentation):
        self.suite_reporter = suite_reporter
        self.rendering_environment = None

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        self.rendering_environment = environment
        srd = self.suite_reporter
        initial_paragraphs = [docs.para(srd.single_line_description())]
        initial_paragraphs.extend(srd.main_description_rest())
        initial_paragraphs.extend(self._default_reporter_info())
        sub_sections = []
        names_and_contents = [
            ('Output syntax', srd.syntax_of_output()),
            ('Exit code', srd.exit_code_description()),
        ]
        append_sections_if_contents_is_non_empty(sub_sections, names_and_contents)
        sub_sections.extend(see_also_sections(srd.see_also_items(), environment))
        return doc.SectionContents(initial_paragraphs, sub_sections)

    def _default_reporter_info(self) -> list:
        if self.suite_reporter.singular_name() == DEFAULT_REPORTER.singular_name:
            return docs.paras('This is the default %s.' % SUITE_REPORTER_ENTITY_TYPE_NAME)
        else:
            return []
