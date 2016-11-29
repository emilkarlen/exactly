from exactly_lib.help import cross_reference_id as cross_ref
from exactly_lib.help.actors.contents_structure import ActorsHelp, ActorDocumentation
from exactly_lib.help.actors.render import IndividualActorRenderer
from exactly_lib.help.cross_reference_id import CustomTargetInfoFactory
from exactly_lib.help.utils.render import RenderingEnvironment
from exactly_lib.util.textformat.structure import document  as doc
from exactly_lib.util.textformat.structure import structures  as docs


class HtmlDocGeneratorForActorsHelp:
    def __init__(self,
                 rendering_environment: RenderingEnvironment,
                 actors_help: ActorsHelp):
        self.actors_help = actors_help
        self.rendering_environment = rendering_environment

    def apply(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        ret_val_sections = []
        ret_val_targets = []
        for actor in sorted(self.actors_help.all_actors, key=lambda cn: cn.name()):
            assert isinstance(actor, ActorDocumentation)
            actor_presentation_str = actor.name()
            header = docs.anchor_text(docs.text(actor_presentation_str),
                                      actor.cross_reference_target())
            section = doc.Section(header,
                                  IndividualActorRenderer(actor).apply(self.rendering_environment))
            target_info_node = cross_ref.TargetInfoNode(cross_ref.TargetInfo(actor_presentation_str,
                                                                             actor.cross_reference_target()),
                                                        [])
            ret_val_sections.append(section)
            ret_val_targets.append(target_info_node)
        return ret_val_targets, doc.SectionContents([], ret_val_sections)
