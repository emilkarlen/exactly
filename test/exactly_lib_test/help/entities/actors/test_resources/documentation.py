from typing import List

from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity.actors import name_and_ref_target
from exactly_lib.help.entities.actors.contents_structure import ActorDocumentation
from exactly_lib.util.textformat.structure.document import SectionContents


class ActorTestImpl(ActorDocumentation):
    def __init__(self, singular_name: str,
                 act_phase_contents: SectionContents = SectionContents([]),
                 act_phase_contents_syntax: SectionContents = SectionContents([]),
                 see_also_specific: list = None):
        super().__init__(name_and_ref_target(singular_name,
                                             'single line description str'))
        self._act_phase_contents = act_phase_contents
        self._act_phase_contents_syntax = act_phase_contents_syntax
        self.__see_also_specific = [] if see_also_specific is None else see_also_specific

    def act_phase_contents(self) -> SectionContents:
        return self._act_phase_contents

    def act_phase_contents_syntax(self) -> SectionContents:
        return self._act_phase_contents_syntax

    def _see_also_specific(self) -> List[SeeAlsoTarget]:
        return self.__see_also_specific
