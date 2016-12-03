from exactly_lib.help.actors.contents_structure import ActorDocumentation, ActorsHelp
from exactly_lib.help.utils.entity_documentation import AllEntitiesListRenderer
from exactly_lib.help.utils.render import SectionContentsRenderer, RenderingEnvironment
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.structures import para


def all_actors_list_renderer(actors_help: ActorsHelp) -> SectionContentsRenderer:
    return AllEntitiesListRenderer(actors_help.all_actors)


class IndividualActorRenderer(SectionContentsRenderer):
    def __init__(self, actor: ActorDocumentation):
        self.actor = actor
        self.rendering_environment = None

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        self.rendering_environment = environment
        initial_paragraphs = [para(self.actor.single_line_description())]
        sub_sections = []
        return doc.SectionContents(initial_paragraphs, sub_sections)
