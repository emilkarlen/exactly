from exactly_lib.help.actors.contents_structure import ActorDocumentation
from exactly_lib.help.entity_names import ACTOR_ENTITY_TYPE_NAME
from exactly_lib.help.utils.entity_documentation import AllEntitiesListRenderer
from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs


def all_actors_list_renderer(all_actors: list) -> SectionContentsRenderer:
    return AllEntitiesListRenderer(lambda actor: docs.paras(actor.single_line_description()),
                                   all_actors)


class IndividualActorRenderer(SectionContentsRenderer):
    def __init__(self, actor: ActorDocumentation):
        self.actor = actor
        self.rendering_environment = None

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        self.rendering_environment = environment
        initial_paragraphs = [docs.para(self.actor.single_line_description())]
        initial_paragraphs.extend(self._default_reporter_info())
        sub_sections = []
        return doc.SectionContents(initial_paragraphs, sub_sections)

    def _default_reporter_info(self) -> list:
        from exactly_lib.help.actors.names_and_cross_references import DEFAULT_ACTOR
        if self.actor.singular_name() == DEFAULT_ACTOR.singular_name:
            return docs.paras('This is the default %s.' % ACTOR_ENTITY_TYPE_NAME)
        else:
            return []
