from exactly_lib.help.actors.contents_structure import ActorDocumentation
from exactly_lib.help.concepts.configuration_parameters.actor import ACTOR_CONCEPT
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.entity_documentation import AllEntitiesListRenderer
from exactly_lib.help.utils.phase_names import ACT_PHASE_NAME
from exactly_lib.help.utils.render import cross_reference_sections
from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.utils import append_sections_if_contents_is_non_empty


def all_actors_list_renderer(all_actors: list) -> SectionContentsRenderer:
    return AllEntitiesListRenderer(lambda actor: docs.paras(actor.single_line_description()),
                                   all_actors)


class IndividualActorRenderer(SectionContentsRenderer):
    def __init__(self, actor: ActorDocumentation):
        self.actor = actor
        self.rendering_environment = None
        format_map = {
            'actor_concept': formatting.concept(ACTOR_CONCEPT.name().singular),
            'act_phase': ACT_PHASE_NAME.emphasis,
        }
        self._parser = TextParser(format_map)

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        self.rendering_environment = environment
        initial_paragraphs = [docs.para(self.actor.single_line_description())]
        initial_paragraphs.extend(self._default_reporter_info())
        initial_paragraphs.extend(self.actor.main_description_rest())
        sub_sections = []
        append_sections_if_contents_is_non_empty(
            sub_sections,
            [(self._parser.format('{act_phase} phase contents'), self.actor.act_phase_contents()),
             (self._parser.format('Syntax of {act_phase} phase contents'), self.actor.act_phase_contents_syntax())])
        sub_sections.extend(cross_reference_sections(self.actor.see_also(), environment))
        return doc.SectionContents(initial_paragraphs, sub_sections)

    def _default_reporter_info(self) -> list:
        from exactly_lib.help.actors.names_and_cross_references import DEFAULT_ACTOR
        if self.actor.singular_name() == DEFAULT_ACTOR.singular_name:
            return self._parser.fnap('This is the default {actor_concept}.')
        else:
            return []
