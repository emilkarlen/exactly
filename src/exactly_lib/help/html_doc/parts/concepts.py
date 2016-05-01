from exactly_lib.help import cross_reference_id as cross_ref
from exactly_lib.help.concepts.contents_structure import ConceptsHelp, ConceptDocumentation
from exactly_lib.help.concepts.render import IndividualConceptRenderer
from exactly_lib.help.cross_reference_id import CustomTargetInfoFactory
from exactly_lib.help.utils.render import RenderingEnvironment
from exactly_lib.util.textformat.structure import document  as doc
from exactly_lib.util.textformat.structure import structures  as docs


class HtmlDocGeneratorForConceptsHelp:
    def __init__(self,
                 rendering_environment: RenderingEnvironment,
                 concepts_help: ConceptsHelp):
        self.concepts_help = concepts_help
        self.rendering_environment = rendering_environment

    def apply(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        ret_val_sections = []
        ret_val_targets = []
        for concept in sorted(self.concepts_help.all_concepts,
                              key=lambda cn: cn.name().singular):
            assert isinstance(concept, ConceptDocumentation)
            concept_presentation_str = concept.name().singular
            header = docs.anchor_text(docs.text(concept_presentation_str),
                                      concept.cross_reference_target())
            section = doc.Section(header,
                                  IndividualConceptRenderer(concept).apply(self.rendering_environment))
            target_info_node = cross_ref.TargetInfoNode(cross_ref.TargetInfo(concept_presentation_str,
                                                                             concept.cross_reference_target()),
                                                        [])
            ret_val_sections.append(section)
            ret_val_targets.append(target_info_node)
        return ret_val_targets, doc.SectionContents([], ret_val_sections)
