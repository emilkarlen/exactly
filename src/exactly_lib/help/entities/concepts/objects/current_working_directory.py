from typing import List

from exactly_lib import program_info
from exactly_lib.definitions import formatting, path, misc_texts
from exactly_lib.definitions.cross_ref import name_and_cross_ref
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.current_directory_and_path_type import cd_instruction_section_on_def_instruction
from exactly_lib.definitions.entity import concepts, types
from exactly_lib.definitions.formatting import InstructionName
from exactly_lib.definitions.test_case import phase_names, phase_infos
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.definitions.test_case.instructions.define_symbol import DEFINE_SYMBOL_INSTRUCTION_CROSS_REFERENCE
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.tcfs.sds import SUB_DIRECTORY__ACT
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.textformat_parser import TextParser


class _CurrentWorkingDirectoryConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        tp = TextParser({

            'cd_concept': formatting.concept(self.singular_name()),
            'CD': self.acronym(),

            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
            'sds_concept': formatting.concept_(concepts.SDS_CONCEPT_INFO),
            'act_sub_dir': SUB_DIRECTORY__ACT + '/',
            'path_type': formatting.symbol_type_(types.PATH_TYPE_INFO),
            'act_phase': phase_names.ACT.emphasis,
            'rel_cd_option': formatting.cli_option(path.REL_CWD_OPTION),

            'cd_instruction': InstructionName(instruction_names.CHANGE_DIR_INSTRUCTION_NAME),
            'def_instruction': InstructionName(instruction_names.SYMBOL_DEFINITION_INSTRUCTION_NAME),
            'instruction': concepts.INSTRUCTION_CONCEPT_INFO.name,

            'os_process': misc_texts.OS_PROCESS_NAME,

        })
        return DescriptionWithSubSections(
            self.single_line_description(),
            SectionContents(
                tp.fnap(_INITIAL_PARAGRAPHS),
                [
                    docs.section(
                        tp.text(_USING_THE_CD_HEADER),
                        tp.fnap(_USING_THE_CD)
                    ),
                    docs.section(
                        tp.text(_DESCRIPTION_DEF_INSTRUCTION_HEADER),
                        cd_instruction_section_on_def_instruction()
                    ),
                ]
            ))

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        ret_val = name_and_cross_ref.cross_reference_id_list([
            concepts.SDS_CONCEPT_INFO,
            types.PATH_TYPE_INFO,
        ])
        ret_val += [
            phase_infos.ACT.cross_reference_target,
            DEFINE_SYMBOL_INSTRUCTION_CROSS_REFERENCE,
        ]
        return ret_val


CURRENT_WORKING_DIRECTORY_CONCEPT = _CurrentWorkingDirectoryConcept()

############################################################
# MENTION
#
# - There is a CD concept
#
# - Initial value
# - Modification of CD, and scope of change of CD
#
# - Usage of CD - instructions PATH arguments -rel-cd
#                 processes executed by $, run
#                 ATC process
############################################################
_INITIAL_PARAGRAPHS = """\
During the execution of a test case, there is a {cd_concept} (CD).

It is initialized to the {act_sub_dir} sub directory of the {sds_concept}.


The {CD} is the same for all instructions and phases,
unless changed by the {cd_instruction} instruction.

A change of {CD} stay in effect for all following instructions and phases.
"""

_USING_THE_CD_HEADER = 'Using the {cd_concept}'

_USING_THE_CD = """\
{instruction:/u} arguments of type {path_type} that are relative to the {CD}
(via the {rel_cd_option} option).


{os_process:s} executed from within a test case
have the {CD} as Present Working Directory (PWD)
when the process starts.

This applies to the {act_phase} phase (as a whole),
and {instruction:s} that execute {os_process:s}.

The {act_phase} phase is always executed as a single
{os_process} execution.


Change of PWD in a process do not change the {CD}
of following instructions and phases.
"""

_DESCRIPTION_DEF_INSTRUCTION_HEADER = '{def_instruction} instruction'
