from exactly_lib.help.actors.contents_structure import ActorDocumentation, ActorsHelp
from exactly_lib.help.utils.render import SectionContentsRenderer, RenderingEnvironment
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.structures import para, text, SEPARATION_OF_HEADER_AND_CONTENTS, \
    paras


class AllActorsListRenderer(SectionContentsRenderer):
    def __init__(self, actors_help: ActorsHelp):
        self.actors_help = actors_help

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return doc.SectionContents([_sorted_actors_list(self.actors_help.all_actors)], [])


class IndividualActorRenderer(SectionContentsRenderer):
    def __init__(self, actor: ActorDocumentation):
        self.actor = actor
        self.rendering_environment = None

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        self.rendering_environment = environment
        initial_paragraphs = [para(self.actor.single_line_description())]
        sub_sections = []
        return doc.SectionContents(initial_paragraphs, sub_sections)


def _sorted_actors_list(actors: iter) -> ParagraphItem:
    all_actors = sorted(actors, key=lambda ad: ad.name())
    items = [lists.HeaderContentListItem(text(actor.name()),
                                         paras(actor.single_line_description()))
             for actor in all_actors]
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.VARIABLE_LIST,
                                                custom_indent_spaces=0,
                                                custom_separations=SEPARATION_OF_HEADER_AND_CONTENTS))
