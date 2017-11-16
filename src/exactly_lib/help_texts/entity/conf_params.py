from exactly_lib import program_info
from exactly_lib.help.utils.entity_documentation import EntityTypeNames
from exactly_lib.help_texts import conf_params
from exactly_lib.help_texts.cross_reference_id import EntityCrossReferenceId
from exactly_lib.help_texts.entity import concepts
from exactly_lib.help_texts.entity.concepts import CONFIGURATION_PARAMETER_CONCEPT_INFO
from exactly_lib.help_texts.entity_identifiers import CONFIGURATION_PARAMETER_ENTITY_TYPE_IDENTIFIER
from exactly_lib.help_texts.name_and_cross_ref import SingularNameAndCrossReferenceId, CrossReferenceId
from exactly_lib.help_texts.names import formatting
from exactly_lib.help_texts.test_case.phase_names import phase_name_dictionary

CONF_PARAM_ENTITY_TYPE_NAMES = EntityTypeNames(
    CONFIGURATION_PARAMETER_CONCEPT_INFO.name,
    CONFIGURATION_PARAMETER_ENTITY_TYPE_IDENTIFIER,
    formatting.syntax_element(CONFIGURATION_PARAMETER_CONCEPT_INFO.singular_name))


class ConfigurationParameterInfo(SingularNameAndCrossReferenceId):
    def __init__(self,
                 singular_name: str,
                 configuration_parameter_name: str,
                 single_line_description_str: str,
                 cross_reference_target: CrossReferenceId):
        super().__init__(singular_name,
                         single_line_description_str,
                         cross_reference_target)
        self._configuration_parameter_name = configuration_parameter_name

    @property
    def configuration_parameter_name(self) -> str:
        return self._configuration_parameter_name


def concept_cross_ref(concept_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(CONF_PARAM_ENTITY_TYPE_NAMES.identifier,
                                  CONF_PARAM_ENTITY_TYPE_NAMES.name.singular,
                                  concept_name)


def conf_param_info(name: str,
                    configuration_parameter_name: str,
                    single_line_description_str: str) -> ConfigurationParameterInfo:
    return ConfigurationParameterInfo(name,
                                      configuration_parameter_name,
                                      single_line_description_str,
                                      concept_cross_ref(configuration_parameter_name))


def _format(s: str) -> str:
    return s.format(program_name=formatting.program_name(program_info.PROGRAM_NAME),
                    phase=phase_name_dictionary())


ACTOR_CONF_PARAM_INFO = conf_param_info(
    'actor',
    conf_params.ACTOR,
    concepts.ACTOR_CONCEPT_INFO.single_line_description_str
)

EXECUTION_MODE_CONF_PARAM_INFO = conf_param_info(
    'execution mode',
    conf_params.EXECUTION_MODE,
    _format('Determines how the outcome of the {phase[assert]} phase is interpreted, '
            'or if the test case should be skipped.')
)

HOME_CASE_DIRECTORY_CONF_PARAM_INFO = conf_param_info(
    'home directory',
    conf_params.HOME_CASE_DIRECTORY,
    'Default location of files referenced from the test case.'
)

HOME_ACT_DIRECTORY_CONF_PARAM_INFO = conf_param_info(
    'act-home directory',
    conf_params.HOME_ACT_DIRECTORY,
    _format('Default location of files referenced from the {phase[act]} phase.')
)

TIMEOUT_CONF_PARAM_INFO = conf_param_info(
    'timeout',
    conf_params.TIMEOUT,
    _format('Timeout of sub processes executed by instructions and the {phase[act]} phase.')
)

ALL_CONF_PARAM_INFOS = (
    ACTOR_CONF_PARAM_INFO,
    EXECUTION_MODE_CONF_PARAM_INFO,
    HOME_CASE_DIRECTORY_CONF_PARAM_INFO,
    HOME_ACT_DIRECTORY_CONF_PARAM_INFO,
    TIMEOUT_CONF_PARAM_INFO,
)
