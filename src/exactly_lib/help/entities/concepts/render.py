from typing import List

from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.help.render import see_also as render_utils
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.section import \
    ArticleContentsConstructor
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs


class IndividualConceptConstructor(ArticleContentsConstructor):
    def __init__(self, concept: ConceptDocumentation):
        self.concept = concept
        self.rendering_environment = None

    def apply(self, environment: ConstructionEnvironment) -> doc.ArticleContents:
        purpose = self.concept.purpose()
        sub_sections = []
        sub_sections += self._rest_section(purpose)
        sub_sections += self._see_also_sections(environment)

        return doc.ArticleContents(docs.paras(purpose.single_line_description),
                                   doc.SectionContents([],
                                                       sub_sections))

    @staticmethod
    def _rest_section(purpose: DescriptionWithSubSections):
        rest = purpose.rest
        if rest.is_empty:
            return []
        sect = docs.section('Description',
                            rest.initial_paragraphs,
                            rest.sections)
        return [sect]

    def _see_also_sections(self, environment: ConstructionEnvironment) -> List[docs.SectionItem]:
        return render_utils.see_also_sections(self.concept.see_also_targets(),
                                              environment)
