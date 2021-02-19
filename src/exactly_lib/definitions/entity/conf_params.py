from exactly_lib import program_info
from exactly_lib.definitions import conf_params, formatting
from exactly_lib.definitions import test_case_file_structure
from exactly_lib.definitions.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.definitions.cross_ref.concrete_cross_refs import EntityCrossReferenceId
from exactly_lib.definitions.cross_ref.name_and_cross_ref import SingularNameAndCrossReferenceId
from exactly_lib.definitions.doc_format import syntax_text
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.entity.actors import DEFAULT_ACTOR_SINGLE_LINE_VALUE
from exactly_lib.definitions.entity.all_entity_types import CONF_PARAM_ENTITY_TYPE_NAMES
from exactly_lib.definitions.test_case.phase_names import PHASE_NAME_DICTIONARY
from exactly_lib.processing import exit_values
from exactly_lib.test_case import test_case_status
from exactly_lib.util.textformat.structure.core import StringText


class ConfigurationParameterInfo(SingularNameAndCrossReferenceId):
    def __init__(self,
                 singular_name: str,
                 configuration_parameter_name: str,
                 informative_name: str,
                 single_line_description_str: str,
                 default_value_single_line_description: str,
                 cross_reference_target: CrossReferenceId):
        super().__init__(singular_name,
                         single_line_description_str,
                         cross_reference_target)
        self._default_value_single_line_description = default_value_single_line_description
        self._configuration_parameter_name = configuration_parameter_name
        self._informative_name = informative_name

    @property
    def informative_name(self) -> str:
        return self._informative_name

    @property
    def singular_name_text(self) -> StringText:
        return syntax_text(self._singular_name)

    @property
    def configuration_parameter_name(self) -> str:
        return self._configuration_parameter_name

    @property
    def configuration_parameter_name_text(self) -> StringText:
        return syntax_text(self._configuration_parameter_name)

    @property
    def default_value_single_line_description(self) -> str:
        return self._default_value_single_line_description


def cross_ref(configuration_parameter_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(CONF_PARAM_ENTITY_TYPE_NAMES,
                                  configuration_parameter_name)


def _conf_param_info(name: str,
                     configuration_parameter_name: str,
                     default_value_single_line_description: str,
                     single_line_description_str: str) -> ConfigurationParameterInfo:
    return ConfigurationParameterInfo(configuration_parameter_name,
                                      configuration_parameter_name,
                                      name,
                                      single_line_description_str,
                                      default_value_single_line_description,
                                      cross_ref(configuration_parameter_name))


_FORMAT_MAP = {
    'program_name': formatting.program_name(program_info.PROGRAM_NAME),
    'phase': PHASE_NAME_DICTIONARY,
    'PASS': exit_values.EXECUTION__PASS.exit_identifier,
    'FAIL': exit_values.EXECUTION__FAIL.exit_identifier,
}


def _format(s: str) -> str:
    return s.format_map(_FORMAT_MAP)


def _of_tc_dir_info(x: test_case_file_structure.TcDirInfo) -> ConfigurationParameterInfo:
    return _conf_param_info(x.informative_name,
                            x.identifier,
                            'The directory where the test case file is located.',
                            x.single_line_description_str)


ACTOR_CONF_PARAM_INFO = _conf_param_info(
    'actor',
    conf_params.ACTOR,
    DEFAULT_ACTOR_SINGLE_LINE_VALUE,
    concepts.ACTOR_CONCEPT_INFO.single_line_description_str,
)

TEST_CASE_STATUS_CONF_PARAM_INFO = _conf_param_info(
    'test case status',
    conf_params.TEST_CASE_STATUS,
    test_case_status.NAME_DEFAULT,
    _format('The status of the test case - if it is expected to {PASS} or {FAIL}, or should be skipped.'),
)

HDS_CASE_DIRECTORY_CONF_PARAM_INFO = _of_tc_dir_info(test_case_file_structure.HDS_CASE_INFO)

HDS_ACT_DIRECTORY_CONF_PARAM_INFO = _of_tc_dir_info(test_case_file_structure.HDS_ACT_INFO)

ALL_CONF_PARAM_INFOS = (
    ACTOR_CONF_PARAM_INFO,
    TEST_CASE_STATUS_CONF_PARAM_INFO,
    HDS_CASE_DIRECTORY_CONF_PARAM_INFO,
    HDS_ACT_DIRECTORY_CONF_PARAM_INFO,
)
