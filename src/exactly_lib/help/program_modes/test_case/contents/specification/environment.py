from exactly_lib import program_info
from exactly_lib.definitions import formatting, type_system, misc_texts
from exactly_lib.definitions import test_case_file_structure
from exactly_lib.definitions.entity import concepts, types
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

        'tcds_concept': formatting.concept_(concepts.TEST_CASE_DIRECTORY_STRUCTURE_CONCEPT_INFO),
        'TCDS': concepts.TEST_CASE_DIRECTORY_STRUCTURE_CONCEPT_INFO.acronym,

        'SDS': concepts.SANDBOX_CONCEPT_INFO.acronym,
        'sds_concept': formatting.concept_(concepts.SANDBOX_CONCEPT_INFO),
        'Sds_concept_header': concepts.SANDBOX_CONCEPT_INFO.singular_name.capitalize(),
        'sds_single_line_description':
            concepts.SANDBOX_CONCEPT_INFO.single_line_description_str.capitalize(),

        'HDS': concepts.HOME_DIRECTORY_STRUCTURE_CONCEPT_INFO.acronym,
        'hds_concept': formatting.concept_(concepts.HOME_DIRECTORY_STRUCTURE_CONCEPT_INFO),
        'Hds_concept_header': concepts.HOME_DIRECTORY_STRUCTURE_CONCEPT_INFO.singular_name.capitalize(),
        'hds_single_line_description':
            concepts.HOME_DIRECTORY_STRUCTURE_CONCEPT_INFO.single_line_description_str.capitalize(),

        'conf_phase': phase_names.CONFIGURATION,
        'act_phase': phase_names.ACT,

        'act_home_conf_param': formatting.conf_param(test_case_file_structure.HDS_ACT_INFO.identifier),

        'data': type_system.DATA_TYPE_CATEGORY_NAME,
        'path_type': formatting.term(types.PATH_TYPE_INFO.singular_name),

        'Symbols': formatting.concept(concepts.SYMBOL_CONCEPT_INFO.plural_name.capitalize()),

        'relativity': formatting.concept(misc_texts.RELATIVITY.singular),
        'relativities': formatting.concept(misc_texts.RELATIVITY.plural),

        'cd': formatting.emphasis(instruction_names.CHANGE_DIR_INSTRUCTION_NAME),
        'env': formatting.emphasis(instruction_names.ENV_VAR_INSTRUCTION_NAME),
        'CD': formatting.concept_(concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO),
    })

    def const_paragraphs(header_: str, paragraphs_: List[ParagraphItem]) -> generator.SectionHierarchyGenerator:
        return h.leaf(header_,
                      sections.constant_contents(section_contents(paragraphs_)))

    return h.hierarchy__str(
        header,
        children=[
            h.child_hierarchy('dir-structure',
                              'Directory structure and Current directory',
                              paragraphs.constant(tp.fnap(_DS_CD_PREAMBLE)),
                              [
                                  h.child('sds',
                                          const_paragraphs(
                                              concepts.SANDBOX_CONCEPT_INFO.singular_name.capitalize() +
                                              ' and Current directory',
                                              tp.fnap(_SDS_AND_CD))
                                          ),
                                  h.child('hds',
                                          const_paragraphs(
                                              concepts.HOME_DIRECTORY_STRUCTURE_CONCEPT_INFO.singular_name.capitalize(),
                                              tp.fnap(_HDS))
                                          ),
                                  h.child('file-ref',
                                          const_paragraphs(
                                              'File references',
                                              tp.fnap(_FILE_REFERENCES))
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
            h.child('env-vars',
                    h.leaf(
                        'Environment variables',
                        sections.contents(
                            [paragraphs.constant(tp.fnap(_ENVIRONMENT_VARIABLES))],
                            [
                                see_also.SeeAlsoSectionConstructor(
                                    see_also.items_of_targets(_env_var_see_also_targets())
                                )
                            ]
                        ))
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
The {sds_concept} ({SDS}) is created in a platform dependent location for temporary files.


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
The {hds_concept} ({HDS}) organizes files that exist before the execution
and that should probably not be modified.


One of the directories in the {HDS} is the {act_home_conf_param} directory.
It is the default location of the executable program file
that is tested, i.e. the location of files referenced from the {act_phase} phase.


All directories in the {HDS} are initialized to the directory
that contains the test case file,
and can be changed in the {conf_phase} phase.
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
{TCDS}:


  * The {path_type} {data} type has syntax for expressing paths relative to any of the {TCDS} directories.
  
  * {Symbols} may be defined with the {path_type} {data} type for convenient reusable references to directories.
  

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
        concepts.TEST_CASE_DIRECTORY_STRUCTURE_CONCEPT_INFO.cross_reference_target,
        concepts.SANDBOX_CONCEPT_INFO.cross_reference_target,
        concepts.HOME_DIRECTORY_STRUCTURE_CONCEPT_INFO.cross_reference_target,
        concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO.cross_reference_target,
        concepts.SYMBOL_CONCEPT_INFO.cross_reference_target,
        types.PATH_TYPE_INFO.cross_reference_target,
        phase_infos.CONFIGURATION.cross_reference_target,
    ]


############################################################
# MENTION
#
# - Which env vars are available.
# - Env vars and TCDS
# - Manipulating env vars
############################################################
_ENVIRONMENT_VARIABLES = """\
All OS environment variables
that are set when {program_name} is started
are available in processes run from the test case.


In addition to these, {program_name} sets some environment variables
that correspond to directories in the {tcds_concept}.


Environment variables can be manipulated by the {env} instruction.
"""


def _env_var_see_also_targets() -> List[see_also.SeeAlsoTarget]:
    return [
        concepts.TEST_CASE_DIRECTORY_STRUCTURE_CONCEPT_INFO.cross_reference_target,
        concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO.cross_reference_target,
    ]
