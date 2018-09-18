from exactly_lib.definitions import formatting
from exactly_lib.definitions.entity.concepts import SUITE_REPORTER_CONCEPT_INFO
from exactly_lib.definitions.entity.suite_reporters import DEFAULT_REPORTER
from exactly_lib.help.entities.suite_reporters.contents_structure import SuiteReporterDocumentation
from exactly_lib.help.render.see_also import see_also_sections
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.section import \
    ArticleContentsConstructor
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.utils import append_sections_if_contents_is_non_empty


class IndividualSuiteReporterConstructor(ArticleContentsConstructor):
    def __init__(self, suite_reporter: SuiteReporterDocumentation):
        self.suite_reporter = suite_reporter

    def apply(self, environment: ConstructionEnvironment) -> doc.ArticleContents:
        srd = self.suite_reporter
        initial_paragraphs = srd.main_description_rest()
        initial_paragraphs.extend(self._default_reporter_info())
        sub_sections = []
        names_and_contents = [
            ('Output syntax', srd.syntax_of_output()),
            ('Exit code', srd.exit_code_description()),
        ]
        append_sections_if_contents_is_non_empty(sub_sections, names_and_contents)
        sub_sections += see_also_sections(srd.see_also_targets(), environment)
        return doc.ArticleContents(docs.paras(srd.single_line_description()),
                                   doc.SectionContents(initial_paragraphs,
                                                       sub_sections))

    def _default_reporter_info(self) -> list:
        if self.suite_reporter.singular_name() == DEFAULT_REPORTER.singular_name:
            return docs.paras('This is the default {reporter_concept}.'.format(
                reporter_concept=formatting.concept_(SUITE_REPORTER_CONCEPT_INFO)))
        else:
            return []
