from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.test_case.os_services import OsServices, new_default
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.util.process_execution.execution_elements import with_no_timeout, ProcessExecutionSettings
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.test_case_file_structure.test_resources import non_hds_populator, hds_populators, \
    tcds_populators, sds_populator
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    HdsAndSdsAction


class ActEnvironment(tuple):
    def __new__(cls,
                tcds: Tcds):
        return tuple.__new__(cls, (tcds,))

    @property
    def tcds(self) -> Tcds:
        return self[0]


class ActResultProducer:
    def apply(self, act_environment: ActEnvironment) -> SubProcessResult:
        raise NotImplementedError()


class ActResultProducerFromActResult(ActResultProducer):
    def __init__(self, act_result: SubProcessResult = SubProcessResult()):
        self.act_result = act_result

    def apply(self, act_environment: ActEnvironment) -> SubProcessResult:
        return self.act_result


class ArrangementBase:
    def __init__(self,
                 hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                 process_execution_settings: ProcessExecutionSettings = with_no_timeout(),
                 ):
        self.hds_contents = hds_contents
        self.process_execution_settings = process_execution_settings


class ArrangementWithSds(ArrangementBase):
    def __init__(self,
                 pre_contents_population_action: HdsAndSdsAction = HdsAndSdsAction(),
                 hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                 sds_contents: sds_populator.SdsPopulator = sds_populator.empty(),
                 non_hds_contents: non_hds_populator.NonHdsPopulator = non_hds_populator.empty(),
                 tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
                 os_services: OsServices = new_default(),
                 process_execution_settings=with_no_timeout(),
                 post_sds_population_action: HdsAndSdsAction = HdsAndSdsAction(),
                 symbols: SymbolTable = None,
                 fs_location_info: FileSystemLocationInfo = ARBITRARY_FS_LOCATION_INFO,
                 ):
        super().__init__(hds_contents=hds_contents,
                         process_execution_settings=process_execution_settings)
        self.pre_contents_population_action = pre_contents_population_action
        self.sds_contents = sds_contents
        self.non_hds_contents = non_hds_contents
        self.tcds_contents = tcds_contents
        self.post_sds_population_action = post_sds_population_action
        self.os_services = os_services
        self.process_execution_settings = process_execution_settings
        self.symbols = symbol_table_from_none_or_value(symbols)
        self.fs_location_info = fs_location_info


class ArrangementPostAct(ArrangementWithSds):
    def __init__(self,
                 pre_contents_population_action: HdsAndSdsAction = HdsAndSdsAction(),
                 hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                 sds_contents: sds_populator.SdsPopulator = sds_populator.empty(),
                 non_hds_contents: non_hds_populator.NonHdsPopulator = non_hds_populator.empty(),
                 tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
                 post_sds_population_action: HdsAndSdsAction = HdsAndSdsAction(),
                 act_result_producer: ActResultProducer = ActResultProducerFromActResult(),
                 os_services: OsServices = new_default(),
                 process_execution_settings: ProcessExecutionSettings = with_no_timeout(),
                 symbols: SymbolTable = None,
                 fs_location_info: FileSystemLocationInfo = ARBITRARY_FS_LOCATION_INFO,
                 ):
        super().__init__(pre_contents_population_action=pre_contents_population_action,
                         sds_contents=sds_contents,
                         hds_contents=hds_contents,
                         non_hds_contents=non_hds_contents,
                         tcds_contents=tcds_contents,
                         post_sds_population_action=post_sds_population_action,
                         os_services=os_services,
                         process_execution_settings=process_execution_settings,
                         symbols=symbols,
                         fs_location_info=fs_location_info)
        self.act_result_producer = act_result_producer
