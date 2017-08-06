from exactly_lib.test_case.os_services import OsServices, new_default
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.util.process_execution.os_process_execution import with_no_timeout, ProcessExecutionSettings
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.test_case_file_structure.test_resources import non_home_populator, home_populators
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check import home_and_sds_populators
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_resources.execution.utils import ActResult
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsAction


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
                 hds_contents: home_populators.HomePopulator = home_populators.empty(),
                 process_execution_settings=with_no_timeout(),
                 ):
        self.hds_contents = hds_contents
        self.process_execution_settings = process_execution_settings


class ArrangementWithSds(ArrangementBase):
    def __init__(self,
                 pre_contents_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                 hds_contents: home_populators.HomePopulator = home_populators.empty(),
                 sds_contents: sds_populator.SdsPopulator = sds_populator.empty(),
                 non_home_contents: non_home_populator.NonHomePopulator = non_home_populator.empty(),
                 home_or_sds_contents: home_and_sds_populators.HomeOrSdsPopulator = home_and_sds_populators.empty(),
                 os_services: OsServices = new_default(),
                 process_execution_settings=with_no_timeout(),
                 post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                 symbols: SymbolTable = None,
                 ):
        super().__init__(hds_contents=hds_contents,
                         process_execution_settings=process_execution_settings)
        self.pre_contents_population_action = pre_contents_population_action
        self.sds_contents = sds_contents
        self.non_home_contents = non_home_contents
        self.home_or_sds_contents = home_or_sds_contents
        self.post_sds_population_action = post_sds_population_action
        self.os_services = os_services
        self.process_execution_settings = process_execution_settings
        self.symbols = symbol_table_from_none_or_value(symbols)


class ArrangementPostAct(ArrangementWithSds):
    def __init__(self,
                 pre_contents_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                 hds_contents: home_populators.HomePopulator = home_populators.empty(),
                 sds_contents: sds_populator.SdsPopulator = sds_populator.empty(),
                 non_home_contents: non_home_populator.NonHomePopulator = non_home_populator.empty(),
                 home_or_sds_contents: home_and_sds_populators.HomeOrSdsPopulator = home_and_sds_populators.empty(),
                 post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                 act_result_producer: ActResultProducer = ActResultProducerFromActResult(),
                 os_services: OsServices = new_default(),
                 process_execution_settings: ProcessExecutionSettings = with_no_timeout(),
                 symbols: SymbolTable = None,
                 ):
        super().__init__(pre_contents_population_action=pre_contents_population_action,
                         sds_contents=sds_contents,
                         hds_contents=hds_contents,
                         non_home_contents=non_home_contents,
                         home_or_sds_contents=home_or_sds_contents,
                         post_sds_population_action=post_sds_population_action,
                         os_services=os_services,
                         process_execution_settings=process_execution_settings,
                         symbols=symbols)
        self.act_result_producer = act_result_producer
