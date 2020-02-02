from typing import Optional

from exactly_lib import program_info
from exactly_lib.definitions import formatting, misc_texts
from exactly_lib.definitions.cross_ref.concrete_cross_refs import EntityCrossReferenceId
from exactly_lib.definitions.cross_ref.name_and_cross_ref import EntityTypeNames, \
    SingularAndPluralAndAcronymNameAndCrossReferenceId
from exactly_lib.definitions.entity import all_entity_types
from exactly_lib.definitions.test_case import phase_names, phase_infos
from exactly_lib.util.name import NameWithGender, an_name_with_plural_s, a_name_with_plural_s

_CURRENT_DIRECTORY_SINGULAR = 'current directory'


def concept_cross_ref(concept_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(all_entity_types.CONCEPT_ENTITY_TYPE_NAMES,
                                  concept_name)


def name_and_ref_target(name: NameWithGender,
                        single_line_description_str: str,
                        acronym: Optional[str] = None) -> SingularAndPluralAndAcronymNameAndCrossReferenceId:
    return SingularAndPluralAndAcronymNameAndCrossReferenceId(formatting.concept_name_with_formatting(name),
                                                              single_line_description_str,
                                                              concept_cross_ref(name.singular),
                                                              acronym)


def name_and_ref_target_for_entity_type(names: EntityTypeNames,
                                        single_line_description_str: str
                                        ) -> SingularAndPluralAndAcronymNameAndCrossReferenceId:
    return name_and_ref_target(names.name, single_line_description_str)


ACTION_TO_CHECK_NAME = NameWithGender('an', 'action to check', "actions to check")

_FORMAT_MAP = {
    'program_name': formatting.program_name(program_info.PROGRAM_NAME),
    'phase': phase_names.PHASE_NAME_DICTIONARY,
    'act': phase_infos.ACT.name,
    'actor': formatting.concept(all_entity_types.ACTOR_ENTITY_TYPE_NAMES.name.singular),
    'action_to_check': formatting.concept(ACTION_TO_CHECK_NAME.singular),
    'current_directory_concept': formatting.concept(_CURRENT_DIRECTORY_SINGULAR),
    'os_process': misc_texts.OS_PROCESS_NAME,
}


def _format(s: str) -> str:
    return s.format_map(_FORMAT_MAP)


_CONFIGURATION_PARAMETER_SINGLE_LINE_DESCRIPTION = """\
A value set in the {0} phase that determine how the remaining phases are executed."""

CONFIGURATION_PARAMETER_CONCEPT_INFO = name_and_ref_target_for_entity_type(
    all_entity_types.CONF_PARAM_ENTITY_TYPE_NAMES,
    _CONFIGURATION_PARAMETER_SINGLE_LINE_DESCRIPTION.format(phase_names.CONFIGURATION)
)

INSTRUCTION_CONCEPT_INFO = name_and_ref_target(
    an_name_with_plural_s('instruction'),
    _format('The building block of all phases except {phase[act]:syntax}.'),
)

TCDS_CONCEPT_INFO = name_and_ref_target(
    a_name_with_plural_s('test case directory structure'),
    'Persistent and temporary directories used in the execution of a test case.',
    'TCDS',
)

HDS_CONCEPT_INFO = name_and_ref_target(
    a_name_with_plural_s('home directory structure'),
    'A set of persistent directories for files used by every execution of a test case.',
    'HDS',
)

SDS_CONCEPT_INFO = name_and_ref_target(
    a_name_with_plural_s('sandbox directory structure'),
    _format('A set of temporary directories used by a single execution of a test case. '
            'One of them is the initial {current_directory_concept}.'),
    'SDS',
)

CURRENT_WORKING_DIRECTORY_CONCEPT_INFO = name_and_ref_target(
    NameWithGender('a', _CURRENT_DIRECTORY_SINGULAR, 'current directories'),
    _format('The current directory of the environment in which instruction and {os_process:s} are executed.'),
    'CD',
)

ENVIRONMENT_VARIABLE_CONCEPT_INFO = name_and_ref_target(
    an_name_with_plural_s('environment variable'),
    _format('OS environment variables available to processes executed from within a test case.')
)

PREPROCESSOR_CONCEPT_INFO = name_and_ref_target(
    a_name_with_plural_s('preprocessor'),
    'A shell command that transforms a test case file as the first step of processing it'
)

SHELL_SYNTAX_CONCEPT_INFO = name_and_ref_target(
    NameWithGender('a', 'shell syntax', "shell syntaxes"),
    'Quoting of strings in command lines.'
)

SUITE_REPORTER_CONCEPT_INFO = name_and_ref_target_for_entity_type(
    all_entity_types.SUITE_REPORTER_ENTITY_TYPE_NAMES,
    'Reports the outcome of a test suite via stdout, stderr and exit code.'
)

TYPE_CONCEPT_INFO = name_and_ref_target_for_entity_type(
    all_entity_types.TYPE_ENTITY_TYPE_NAMES,
    'Type system for symbols and instruction arguments.'
)

SYMBOL_CONCEPT_INFO = name_and_ref_target(
    all_entity_types.SYMBOL_CONCEPT_NAME,
    _format('A named constant, with one of the types of {program_name}\'s type system.')
)

ACTOR_CONCEPT_INFO = name_and_ref_target_for_entity_type(
    all_entity_types.ACTOR_ENTITY_TYPE_NAMES,
    _format('Resolves the {action_to_check} by interpreting the contents of the {act} phase.')
)

ACTION_TO_CHECK_CONCEPT_INFO = name_and_ref_target(
    ACTION_TO_CHECK_NAME,
    _format('The action that is executed in the {act} phase.'),
    'ATC',
)

DIRECTIVE_CONCEPT_INFO = name_and_ref_target_for_entity_type(
    all_entity_types.DIRECTIVE_ENTITY_TYPE_NAMES,
    'Processing during file reading and syntax checking.',
)
