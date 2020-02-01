from exactly_lib import program_info
from exactly_lib.definitions import formatting, type_system, misc_texts
from exactly_lib.definitions import test_case_file_structure
from exactly_lib.definitions.entity import concepts, types, conf_params
from exactly_lib.definitions.formatting import InstructionName
from exactly_lib.definitions.test_case import phase_names, phase_infos
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.help.render import see_also
from exactly_lib.util.textformat.constructor import paragraphs
from exactly_lib.util.textformat.constructor import sections
from exactly_lib.util.textformat.section_target_hierarchy import hierarchies as h, generator
from exactly_lib.util.textformat.structure.structures import *
from exactly_lib.util.textformat.textformat_parser import TextParser


def root(header: str) -> generator.SectionHierarchyGenerator:
    tp = TextParser({

        'program_name': formatting.program_name(program_info.PROGRAM_NAME),
        'conf_param': formatting.concept_(concepts.CONFIGURATION_PARAMETER_CONCEPT_INFO),

        'tcds_concept': formatting.concept_(concepts.TCDS_CONCEPT_INFO),
        'TCDS': concepts.TCDS_CONCEPT_INFO.acronym,

        'SDS': concepts.SDS_CONCEPT_INFO.acronym,
        'sds_concept': formatting.concept_(concepts.SDS_CONCEPT_INFO),
        'Sds_concept_header': concepts.SDS_CONCEPT_INFO.singular_name.capitalize(),
        'sds_single_line_description':
            concepts.SDS_CONCEPT_INFO.single_line_description_str.capitalize(),

        'HDS': concepts.HDS_CONCEPT_INFO.acronym,
        'hds_concept': formatting.concept_(concepts.HDS_CONCEPT_INFO),
        'Hds_concept_header': concepts.HDS_CONCEPT_INFO.singular_name.capitalize(),
        'hds_single_line_description':
            concepts.HDS_CONCEPT_INFO.single_line_description_str.capitalize(),

        'conf_phase': phase_names.CONFIGURATION,
        'act_phase': phase_names.ACT,

        'act_hds_conf_param': formatting.conf_param(test_case_file_structure.HDS_ACT_INFO.identifier),

        'data': type_system.DATA_TYPE_CATEGORY_NAME,
        'path_type': formatting.term(types.PATH_TYPE_INFO.singular_name),

        'symbol_concept': formatting.concept_(concepts.SYMBOL_CONCEPT_INFO),
        'def_instruction': InstructionName(instruction_names.SYMBOL_DEFINITION_INSTRUCTION_NAME),

        'os_process': misc_texts.OS_PROCESS_NAME,
        'time_out_conf_param': formatting.conf_param_(conf_params.TIMEOUT_CONF_PARAM_INFO),

        'relativity': formatting.concept(misc_texts.RELATIVITY.singular),
        'relativities': formatting.concept(misc_texts.RELATIVITY.plural),

        'cd': formatting.emphasis(instruction_names.CHANGE_DIR_INSTRUCTION_NAME),
        'env': formatting.emphasis(instruction_names.ENV_VAR_INSTRUCTION_NAME),
        'CD': formatting.concept_(concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO),
    })

    def const_paragraphs_child(local_target_name: str,
                               header_: str,
                               paragraphs_: List[ParagraphItem]) -> generator.SectionHierarchyGenerator:
        return h.child(local_target_name,
                       h.leaf(header_,
                              sections.constant_contents(section_contents(paragraphs_)))
                       )

    return h.hierarchy(
        header,
        children=[
            h.child_hierarchy(
                'dir-structure',
                'Directory structure and Current directory',
                paragraphs.constant(tp.fnap(_DS_CD_PREAMBLE)),
                [
                    const_paragraphs_child(
                        'sds',
                        concepts.SDS_CONCEPT_INFO.singular_name.capitalize() +
                        ' and Current directory',
                        tp.fnap(_SDS_AND_CD)
                    ),
                    const_paragraphs_child(
                        'hds',
                        concepts.HDS_CONCEPT_INFO.singular_name.capitalize(),
                        tp.fnap(_HDS),
                    ),
                    const_paragraphs_child(
                        'file-ref',
                        'File references',
                        tp.fnap(_FILE_REFERENCES)
                    ),
                    h.child('see-also',
                            h.with_not_in_toc(
                                h.leaf(
                                    see_also.SEE_ALSO_TITLE,
                                    see_also.SeeAlsoSectionContentsConstructor(
                                        see_also.items_of_targets(_dir_struct_see_also_targets())
                                    )))
                            ),
                ]
            ),
            h.child_hierarchy(
                'symbols',
                concepts.SYMBOL_CONCEPT_INFO.plural_name.capitalize(),
                paragraphs.constant(tp.fnap(_SYMBOLS)),
                [
                    h.with_not_in_toc(
                        h.child_leaf(
                            'see-also',
                            see_also.SEE_ALSO_TITLE,
                            see_also.SeeAlsoSectionContentsConstructor(
                                see_also.items_of_targets(_symbols_see_also_targets())
                            ))
                    )
                ]
            ),
            h.child_hierarchy(
                'os-proc',
                tp.text(misc_texts.OS_PROCESS_ENVIRONMENT_SECTION_HEADER),
                paragraphs.constant(tp.fnap(_OS_PROC_INTRO)),
                [
                    const_paragraphs_child(
                        'cd',
                        'Current directory',
                        tp.fnap(_OS_PROC_CURRENT_DIRECTORY),
                    ),
                    const_paragraphs_child(
                        'env-vars',
                        'Environment variables',
                        tp.fnap(_OS_PROC_ENVIRONMENT_VARIABLES),
                    ),
                    const_paragraphs_child(
                        'timeout',
                        'Timeout',
                        tp.fnap(_OS_PROC_TIMEOUT),
                    ),
                    h.with_not_in_toc(
                        h.child_leaf(
                            'see-also',
                            see_also.SEE_ALSO_TITLE,
                            see_also.SeeAlsoSectionContentsConstructor(
                                see_also.items_of_targets(_os_process_see_also_targets())
                            )))
                    ,
                ],
            ),
        ]
    )


_DS_CD_PREAMBLE = """\
Files and directories used by tests are organized in the {tcds_concept} ({TCDS}).

It consists of two parts:


  * {Sds_concept_header} ({SDS})
  
    {sds_single_line_description}
  
  * {Hds_concept_header} ({HDS})

    {hds_single_line_description}
"""

############################################################
# MENTION
#
# - Each TC executed in a tmp dir (SDS)
# - SDS is in system tmp dir
#
# - CD is inside SDS
# - CD can be changed
############################################################
_SDS_AND_CD = """\
The {SDS} is created in a platform dependent location for temporary files.


The current directory is set to one of the directories inside the {SDS}
at the beginning of execution.

This means that files and directories created in the current directory will be removed
at the end of the execution.


The current directory is the same for all phases,
unless changed by the {cd} instruction.

A change of {CD} stay in effect for all following instructions and phases.
"""

############################################################
# MENTION
#
# - HDS for persistent files
# - HDS initial value
# - Set in [conf]
############################################################
_HDS = """\
The {HDS} organizes files that exist before the execution
and that should probably not be modified.


One of the directories in the {HDS} is the {act_hds_conf_param} directory.
It is the location of the executable program file
that is tested - i.e. the location of files referenced from the {act_phase} phase.


All directories in the {HDS} are initialized to the directory
that contains the test case file.
They can be changed by the {conf_phase} phase.
"""

############################################################
# MENTION
#
# - Functionality for referencing predefined files
# - Instruction argument default location
# - Prevention of modifying predefined files (via relativity validation)
#
# - PATH type for convenient referencing of files in various directories
############################################################
_FILE_REFERENCES = """\
{program_name} has functionality for referencing files in the
{TCDS} using the {path_type} type.


The {path_type} {data} type has syntax for expressing paths relative to any of the {TCDS} directories.
  

The directory that a {path_type} value is relative to is called the
{relativity} of the value.


Arguments to instructions that are paths use the {path_type} {data} type.

Each argument have different accepted {relativities}
and
different default {relativity}.

The defaults are chosen to be the most likely {relativity}.
The accepted {relativities} are chosen to prevent modification of files in the {HDS}.
"""


def _dir_struct_see_also_targets() -> List[see_also.SeeAlsoTarget]:
    return [
        concepts.TCDS_CONCEPT_INFO.cross_reference_target,
        concepts.SDS_CONCEPT_INFO.cross_reference_target,
        concepts.HDS_CONCEPT_INFO.cross_reference_target,
        concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO.cross_reference_target,
        concepts.SYMBOL_CONCEPT_INFO.cross_reference_target,
        types.PATH_TYPE_INFO.cross_reference_target,
        phase_infos.CONFIGURATION.cross_reference_target,
    ]


############################################################
# MENTION
#
# - unique name
# - global name space
# - type
# - constant
# - availability by following instructions
############################################################
_SYMBOLS = """\
A {symbol_concept} is a named constant defined by the {def_instruction:emphasis} instruction.


Once defined, it is available to all following instructions
in the phase where it is defined, and in all following phases.


Symbols may be used to define reusable values used by instructions and the {act_phase} phase.
"""


def _symbols_see_also_targets() -> List[see_also.SeeAlsoTarget]:
    return [
        concepts.SYMBOL_CONCEPT_INFO.cross_reference_target,
        phase_infos.SETUP.instruction_cross_reference_target(
            instruction_names.SYMBOL_DEFINITION_INSTRUCTION_NAME),
    ]


_OS_PROC_INTRO = """\
{program_name} executes {os_process:s} as part of a test case.
Part of their environment is controlled by {program_name}.
"""

############################################################
# MENTION
#
# - Which env vars are available.
# - Manipulating env vars
############################################################
_OS_PROC_ENVIRONMENT_VARIABLES = """\
All OS environment variables
that are set when {program_name} is started
are available in {os_process:s} run from the test case.


Environment variables can be manipulated by the {env} instruction.
"""

_OS_PROC_CURRENT_DIRECTORY = """\
The current directory (PWD) is the same as for instructions.


It is changed by the {cd} instruction.
"""

_OS_PROC_TIMEOUT = """\
Timeout for all {os_process:s} is determined by the {conf_param} {time_out_conf_param}.
"""


def _os_process_see_also_targets() -> List[see_also.SeeAlsoTarget]:
    return [
        concepts.TCDS_CONCEPT_INFO.cross_reference_target,
        concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO.cross_reference_target,
        concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO.cross_reference_target,
        conf_params.TIMEOUT_CONF_PARAM_INFO.cross_reference_target,
    ]
