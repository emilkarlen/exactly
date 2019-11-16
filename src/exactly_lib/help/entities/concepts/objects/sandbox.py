from typing import List

from exactly_lib import program_info
from exactly_lib.cli.definitions.program_modes.test_case import command_line_options
from exactly_lib.common.help.see_also import SeeAlsoUrlInfo
from exactly_lib.definitions import formatting
from exactly_lib.definitions import test_case_file_structure as tcds
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.concrete_cross_refs import PredefinedHelpContentsPartReference, \
    HelpPredefinedContentsPart
from exactly_lib.definitions.doc_format import file_name_text, dir_name_text
from exactly_lib.definitions.entity import concepts, types
from exactly_lib.definitions.formatting import AnyInstructionNameDictionary, InstructionName
from exactly_lib.definitions.test_case import phase_names, phase_infos
from exactly_lib.definitions.test_case.instructions.instruction_names import CHANGE_DIR_INSTRUCTION_NAME
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.test_case_file_structure import sandbox_directory_structure as sds
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType
from exactly_lib.test_case_file_structure.relative_path_options import REL_SDS_OPTIONS_MAP
from exactly_lib.test_case_file_structure.sandbox_directory_structure import DirWithSubDirs
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem, Text
from exactly_lib.util.textformat.structure.document import SectionContents, Section
from exactly_lib.util.textformat.textformat_parser import TextParser


class _SandboxConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(concepts.SDS_CONCEPT_INFO)

        self._tp = TextParser({
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
            'phase': phase_names.PHASE_NAME_DICTIONARY,
            'instruction': AnyInstructionNameDictionary(),
            'cwd': formatting.concept_(concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO),
            'cd_instruction': InstructionName(CHANGE_DIR_INSTRUCTION_NAME),
            'keep_sandbox_option': formatting.cli_option(command_line_options.OPTION_FOR_KEEPING_SANDBOX_DIRECTORY),
        })

    def purpose(self) -> DescriptionWithSubSections:
        rest_paragraphs = []
        sub_sections = []
        rest_paragraphs += self._tp.fnap(_SANDBOX_PRE_DIRECTORY_TREE)
        sub_sections.append(directory_structure_list_section(sds.DIRECTORIES))
        sub_sections += self._sandbox_directories_info_sections()
        return DescriptionWithSubSections(self.single_line_description(),
                                          SectionContents(rest_paragraphs, sub_sections))

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return [
            concepts.TCDS_CONCEPT_INFO.cross_reference_target,
            concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO.cross_reference_target,
            concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO.cross_reference_target,
            types.PATH_TYPE_INFO.cross_reference_target,
            phase_infos.SETUP.instruction_cross_reference_target(CHANGE_DIR_INSTRUCTION_NAME),
            PredefinedHelpContentsPartReference(HelpPredefinedContentsPart.TEST_CASE_CLI),
            SeeAlsoUrlInfo('Platform dependent location of sandbox',
                           'https://docs.python.org/3/library/tempfile.html#tempfile.gettempdir')
        ]

    def _sandbox_directories_info_sections(self) -> List[docs.SectionItem]:
        def section(directory_name: str,
                    dir_info: tcds.TcDirInfo,
                    paragraph_items: List[ParagraphItem]) -> Section:
            return docs.section(dir_name_text(directory_name),
                                docs.paras(dir_info.single_line_description_str + '.') +
                                paragraph_items)

        return [
            section(sds.SUB_DIRECTORY__ACT,
                    tcds.SDS_ACT_INFO,
                    self._act_dir_description_paragraphs()),
            section(sds.SUB_DIRECTORY__RESULT,
                    tcds.SDS_RESULT_INFO,
                    self._result_dir_description_paragraphs()),
            section(sds.PATH__TMP_USER,
                    tcds.SDS_TMP_INFO,
                    self._tmp_user_dir_description_paragraphs()),
            docs.section(dir_name_text(sds.SUB_DIRECTORY__INTERNAL),
                         self._internal_dir_description_paragraphs())
        ]

    def _act_dir_description_paragraphs(self) -> List[ParagraphItem]:
        rel_opt_info = REL_SDS_OPTIONS_MAP[RelSdsOptionType.REL_ACT]
        ret_val = []
        ret_val += self._tp.fnap(_ACT_DIR_DESCRIPTION)
        ret_val += _dir_env_variables_and_rel_options(env_var_name=rel_opt_info.directory_variable_name_text,
                                                      rel_option=rel_opt_info.option_name_text)
        return ret_val

    def _result_dir_description_paragraphs(self) -> List[ParagraphItem]:
        ret_val = []
        ret_val += self._tp.fnap(_RESULT_DIR_DESCRIPTION)
        ret_val.append(docs.simple_header_only_list(map(file_name_text, sds.RESULT_FILE_ALL),
                                                    lists.ListType.ITEMIZED_LIST))
        ret_val += self._result_dir_env_variable_and_rel_option()
        return ret_val

    def _tmp_user_dir_description_paragraphs(self) -> List[ParagraphItem]:
        rel_opt_info = REL_SDS_OPTIONS_MAP[RelSdsOptionType.REL_TMP]
        ret_val = []
        ret_val += self._tp.fnap(_USR_TMP_DIR_DESCRIPTION)
        ret_val += _dir_env_variables_and_rel_options(env_var_name=rel_opt_info.directory_variable_name_text,
                                                      rel_option=rel_opt_info.option_name_text)
        return ret_val

    def _result_dir_env_variable_and_rel_option(self) -> List[ParagraphItem]:
        rel_opt_info = REL_SDS_OPTIONS_MAP[RelSdsOptionType.REL_RESULT]
        return [_dir_info_items_table(rel_opt_info.directory_variable_name_text,
                                      rel_opt_info.option_name_text,
                                      self._tp.format(_RESULT_DIR_ENV_VARIABLE))
                ]

    def _internal_dir_description_paragraphs(self) -> List[ParagraphItem]:
        return self._tp.fnap(_INTERNAL_DIRECTORIES)


SANDBOX_CONCEPT = _SandboxConcept()

_SANDBOX_PRE_DIRECTORY_TREE = """\
Each execution of a test case uses its own sandbox.


It is created in a platform dependent location for temporary files.


The sandbox is created just before the {phase[setup]} phase is executed,
and deleted when test case execution ends
(unless {keep_sandbox_option} is used).
"""

_ACT_DIR_DESCRIPTION = """\
It will be the {cwd} for the {phase[act]} phase, and following phases,
unless it is changed by the {cd_instruction} instruction.


(Files and directories that {phase[setup]:syntax} creates
are installed into the {cwd}, if no instruction options are used to change this.)
"""

_RESULT_DIR_DESCRIPTION = """\
This directory is initially empty.

It is populated when the {phase[act]} phase is executed
with the following files (with obvious contents):
"""

_USR_TMP_DIR_DESCRIPTION = """\
{program_name} does not touch this directory.

The test case can use it as a place where it is safe to put temporary files without
the risk of name clashes with files from other program.
"""

_RESULT_DIR_ENV_VARIABLE = """\
The value of this environment variable
is the absolute path of this directory
(after the {phase[act]} phase has been executed)."""


def _dir_env_variables_and_rel_options(env_var_name: Text,
                                       rel_option: Text) -> List[ParagraphItem]:
    return [_dir_info_items_table(env_var_name,
                                  rel_option,
                                  'The value of this environment variable is the absolute path of this directory.')
            ]


def _dir_info_items_table(env_var_name: Text,
                          rel_option: Text,
                          env_var_description: str) -> ParagraphItem:
    return docs.first_column_is_header_table([
        [
            docs.cell(docs.paras(env_var_name)),
            docs.cell(docs.paras(env_var_description)),
        ],
        [
            docs.cell(docs.paras(rel_option)),
            docs.cell(docs.paras('This option (accepted by many instructions) refers to this directory.')),
        ],
    ])


def directory_structure_list_section(dir_with_sub_dir_list: List[DirWithSubDirs]) -> Section:
    return docs.section('Directory structure',
                        [_directory_structure_list(dir_with_sub_dir_list)])


def _directory_structure_list(dir_with_sub_dir_list: List[DirWithSubDirs]) -> ParagraphItem:
    items = []
    for dir_wsd in dir_with_sub_dir_list:
        sub_dirs_items = []
        if dir_wsd.sub_dirs:
            sub_dirs_items = [_directory_structure_list(dir_wsd.sub_dirs)]
        items.append(docs.list_item(dir_name_text(dir_wsd.name), sub_dirs_items))
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.ITEMIZED_LIST))


_INTERNAL_DIRECTORIES = """\
Root directory for files that are reserved for {program_name}.
"""
