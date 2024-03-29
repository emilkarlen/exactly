from typing import List, Sequence

from exactly_lib.cli.definitions import common_cli_options
from exactly_lib.definitions import formatting, misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.entity import conf_params
from exactly_lib.definitions.test_case import phase_infos
from exactly_lib.definitions.test_case.instructions.instruction_names import ACTOR_INSTRUCTION_NAME
from exactly_lib.definitions.test_case.phase_names import PHASE_NAME_DICTIONARY
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser
from .utils import atc


class _ActionToCheckConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(concepts.ACTION_TO_CHECK_CONCEPT_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        return DescriptionWithSubSections(concepts.ACTION_TO_CHECK_CONCEPT_INFO.single_line_description,
                                          docs.section_contents(self._description()))

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return (
            [
                phase_infos.ACT.cross_reference_target,
                concepts.ACTOR_CONCEPT_INFO.cross_reference_target,
                conf_params.ACTOR_CONF_PARAM_INFO.cross_reference_target,
            ]
        )

    @staticmethod
    def _description() -> Sequence[ParagraphItem]:
        parser = TextParser({
            'action_to_check': concepts.ACTION_TO_CHECK_CONCEPT_INFO.name,
            'actor': concepts.ACTOR_CONCEPT_INFO.name,
            'ATC': concepts.ACTION_TO_CHECK_CONCEPT_INFO.acronym,
            'actor_option': formatting.cli_option(common_cli_options.OPTION_FOR_ACTOR),
            'actor_instruction': formatting.InstructionName(ACTOR_INSTRUCTION_NAME),
            'act': phase_infos.ACT.name,
            'phase': PHASE_NAME_DICTIONARY,
            'os_process': misc_texts.OS_PROCESS_NAME,
        })
        ret_val = list(parser.fnap(_DESCRIPTION))
        ret_val += atc.atc_examples()

        return ret_val


ACTOR_CONCEPT = _ActionToCheckConcept()

_DESCRIPTION = """\
The {action_to_check:/q} ({ATC}) is specified jointly by
the configured {actor:/q}
and the contents of the {act} phase.


It is executed as {os_process:a}.


The {os_process} environment is that of the {act} phase.

 
Depending on which {actor:/q} is configured,
the {ATC} may be, for example:
"""
