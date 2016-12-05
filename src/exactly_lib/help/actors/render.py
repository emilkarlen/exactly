from exactly_lib.help.actors.contents_structure import ActorDocumentation
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
        sub_sections = []
        return doc.SectionContents(initial_paragraphs, sub_sections)
