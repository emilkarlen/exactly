from exactly_lib import program_info
from exactly_lib.help_texts.cross_reference_id import EntityCrossReferenceId
from exactly_lib.help_texts.entity_names import CONCEPT_ENTITY_TYPE_NAME
from exactly_lib.help_texts.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId, Name
from exactly_lib.help_texts.names import formatting
from exactly_lib.help_texts.test_case.phase_names import CONFIGURATION_PHASE_NAME, phase_name_dictionary


def concept_cross_ref(concept_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(CONCEPT_ENTITY_TYPE_NAME, concept_name)


def name_and_ref_target(name: Name,
                        single_line_description_str: str) -> SingularAndPluralNameAndCrossReferenceId:
    return SingularAndPluralNameAndCrossReferenceId(name,
                                                    single_line_description_str,
                                                    concept_cross_ref(name.singular))


def _format(s: str) -> str:
    return s.format(program_name=formatting.program_name(program_info.PROGRAM_NAME),
                    phase=phase_name_dictionary())


_CONFIGURATION_PARAMETER_SINGLE_LINE_DESCRIPTION = """\
A value set in the {0} phase that determine how the remaining phases are executed."""

CONFIGURATION_PARAMETER_CONCEPT_INFO = name_and_ref_target(
    Name('configuration parameter', 'configuration parameters'),
    _CONFIGURATION_PARAMETER_SINGLE_LINE_DESCRIPTION.format(CONFIGURATION_PHASE_NAME)
)

CURRENT_WORKING_DIRECTORY_CONCEPT_INFO = name_and_ref_target(
    Name('current directory', 'current directories'),
    'The current directory of the environment in which an instruction is executed.'
)

ENVIRONMENT_VARIABLE_CONCEPT_INFO = name_and_ref_target(
    Name('environment variable', 'environment variables'),
    _format('Environment variables set by {program_name}.')
)

PREPROCESSOR_CONCEPT_INFO = name_and_ref_target(
    Name('preprocessor', 'preprocessors'),
    'A program that transforms a test case file as the first step in the processing of it.'
)

SANDBOX_CONCEPT_INFO = name_and_ref_target(
    Name('sandbox', 'sandboxes'),
    'The temporary directory where a test case is executed.'
)

SHELL_SYNTAX_CONCEPT_INFO = name_and_ref_target(
    Name('shell syntax', "shell syntaxes"),
    'Quoting of strings in command lines.'
)

SUITE_REPORTER_CONCEPT_INFO = name_and_ref_target(
    Name('reporter', 'reporters'),
    'Reports the outcome of a test suite via stdout, stderr and exit code.'
)

TYPE_CONCEPT_INFO = name_and_ref_target(
    Name('type', 'types'),
    'Type system for symbols and instruction arguments.'
)

SYMBOL_CONCEPT_INFO = name_and_ref_target(
    Name('symbol', 'symbols'),
    'A named, constant, value.'
)

ACTOR_CONCEPT_INFO = name_and_ref_target(
    Name('actor', 'actors'),
    _format('Interprets the contents of the {phase[act]} phase, and executes it.')
)

EXECUTION_MODE_CONCEPT_INFO = name_and_ref_target(
    Name('execution mode', 'execution modes'),
    _format('Determines how the outcome of the {phase[assert]} phase is interpreted, '
            'or if the test case should be skipped.')
)

HOME_CASE_DIRECTORY_CONCEPT_INFO = name_and_ref_target(
    Name('home directory', 'home directories'),
    'Default location of files referenced from the test case.'
)

HOME_ACT_DIRECTORY_CONCEPT_INFO = name_and_ref_target(
    Name('act-home directory', 'act-home directories'),
    _format('Default location of files referenced from the {phase[act]} phase.')
)

TIMEOUT_CONCEPT_INFO = name_and_ref_target(
    Name('timeout', 'timeouts'),
    _format('Timeout of sub processes executed by instructions and the {phase[act]} phase.')
)
