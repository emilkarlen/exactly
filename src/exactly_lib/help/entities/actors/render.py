from exactly_lib.help.entities.actors.contents_structure import ActorDocumentation
from exactly_lib.help.render.see_also_section import see_also_sections
from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.entity import concepts
from exactly_lib.help_texts.test_case.phase_names import ACT_PHASE_NAME
from exactly_lib.util.textformat.construction.section_contents_constructor import ConstructionEnvironment, \
    ArticleContentsConstructor
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser
from exactly_lib.util.textformat.utils import append_sections_if_contents_is_non_empty


class IndividualActorConstructor(ArticleContentsConstructor):
    def __init__(self, actor: ActorDocumentation):
        self.actor = actor
        self.rendering_environment = None
        format_map = {
            'actor_concept': formatting.concept_(concepts.ACTOR_CONCEPT_INFO),
            'act_phase': ACT_PHASE_NAME.emphasis,
        }
        self._parser = TextParser(format_map)

    def apply(self, environment: ConstructionEnvironment) -> doc.ArticleContents:
        self.rendering_environment = environment

        initial_paragraphs = self._default_reporter_info()
        initial_paragraphs.extend(self.actor.main_description_rest())
        sub_sections = []
        append_sections_if_contents_is_non_empty(
            sub_sections,
            [(self._parser.format('{act_phase} phase contents'), self.actor.act_phase_contents()),
             (self._parser.format('Syntax of {act_phase} phase contents'), self.actor.act_phase_contents_syntax())])
        sub_sections += see_also_sections(self.actor.see_also_targets(), environment)
        return doc.ArticleContents(docs.paras(self.actor.single_line_description()),
                                   doc.SectionContents(initial_paragraphs,
                                                       sub_sections))

    def _default_reporter_info(self) -> list:
        from exactly_lib.help_texts.entity.actors import DEFAULT_ACTOR
        if self.actor.singular_name() == DEFAULT_ACTOR.singular_name:
            return self._parser.fnap('This is the default {actor_concept}.')
        else:
            return []
