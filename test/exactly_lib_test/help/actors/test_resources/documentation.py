from exactly_lib.help.actors.contents_structure import ActorDocumentation
from exactly_lib.help.cross_reference_id import CustomCrossReferenceId
from exactly_lib.util.textformat.structure import structures as docs


class ActorTestImpl(ActorDocumentation):
    def __init__(self, singular_name: str):
        super().__init__(singular_name)

    def single_line_description_str(self) -> str:
        return 'single_line_description_str'

    def act_phase_contents(self) -> list:
        return docs.paras('act_phase_contents')

    def act_phase_contents_syntax(self) -> list:
        return docs.paras('act_phase_contents_syntax')

    def _see_also_specific(self) -> list:
        return [CustomCrossReferenceId('custom-cross-reference-target')]
