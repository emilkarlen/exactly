from exactly_lib.test_case.home_and_sds import HomeAndSds
from exactly_lib.test_case.os_services import OsServices, new_default
from exactly_lib.util.process_execution.os_process_execution import with_no_timeout, ProcessExecutionSettings
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_case.test_resources.value_definition import symbol_table_from_none_or_value
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.execution.home_and_sds_check import home_or_sds_populator
from exactly_lib_test.test_resources.execution.home_and_sds_check.home_and_sds_utils import HomeAndSdsAction
from exactly_lib_test.test_resources.execution.sds_check import sds_populator
from exactly_lib_test.test_resources.execution.utils import ActResult


class ActEnvironment(tuple):
    def __new__(cls,
                home_and_sds: HomeAndSds):
        return tuple.__new__(cls, (home_and_sds,))

    @property
    def home_and_sds(self) -> HomeAndSds:
        return self[0]


class ActResultProducer:
    def apply(self, act_environment: ActEnvironment) -> ActResult:
        raise NotImplementedError()


class ActResultProducerFromActResult(ActResultProducer):
    def __init__(self, act_result: ActResult = ActResult()):
        self.act_result = act_result

    def apply(self, act_environment: ActEnvironment) -> ActResult:
        return self.act_result


class ArrangementBase:
    def __init__(self,
                 home_contents: file_structure.DirContents = file_structure.DirContents([]),
                 process_execution_settings=with_no_timeout(),
                 ):
        self.home_contents = home_contents
        self.process_execution_settings = process_execution_settings


class ArrangementWithSds(ArrangementBase):
    def __init__(self,
                 pre_contents_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                 home_contents: file_structure.DirContents = file_structure.DirContents([]),
                 sds_contents: sds_populator.SdsPopulator = sds_populator.empty(),
                 os_services: OsServices = new_default(),
                 process_execution_settings=with_no_timeout(),
                 home_or_sds_contents: home_or_sds_populator.HomeOrSdsPopulator = home_or_sds_populator.empty(),
                 post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                 value_definitions: SymbolTable = None,
                 ):
        super().__init__(home_contents=home_contents,
                         process_execution_settings=process_execution_settings)
        self.pre_contents_population_action = pre_contents_population_action
        self.sds_contents = sds_contents
        self.home_or_sds_contents = home_or_sds_contents
        self.post_sds_population_action = post_sds_population_action
        self.os_services = os_services
        self.process_execution_settings = process_execution_settings
        self.value_definitions = symbol_table_from_none_or_value(value_definitions)


class ArrangementPostAct(ArrangementWithSds):
    def __init__(self,
                 pre_contents_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                 home_contents: file_structure.DirContents = file_structure.DirContents([]),
                 sds_contents: sds_populator.SdsPopulator = sds_populator.empty(),
                 act_result_producer: ActResultProducer = ActResultProducerFromActResult(),
                 os_services: OsServices = new_default(),
                 process_execution_settings: ProcessExecutionSettings = with_no_timeout(),
                 home_or_sds_contents: home_or_sds_populator.HomeOrSdsPopulator = home_or_sds_populator.empty(),
                 post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                 ):
        super().__init__(pre_contents_population_action=pre_contents_population_action,
                         home_contents=home_contents,
                         sds_contents=sds_contents,
                         os_services=os_services,
                         process_execution_settings=process_execution_settings,
                         home_or_sds_contents=home_or_sds_contents,
                         post_sds_population_action=post_sds_population_action)
        self.act_result_producer = act_result_producer
