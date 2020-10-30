from typing import Optional

from exactly_lib.appl_env.os_services import OsServices
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.test_case_utils.os_services import os_services_access
from exactly_lib.util.process_execution.execution_elements import with_no_timeout, ProcessExecutionSettings
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.tcfs.test_resources import non_hds_populator, hds_populators, \
    tcds_populators, sds_populator
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangementPostAct
from exactly_lib_test.test_case.test_resources.act_result import ActResultProducer, ActResultProducerFromActResult
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    TcdsAction, PlainTcdsActionFromTcdsAction
from exactly_lib_test.util.process_execution.test_resources.proc_exe_env import proc_exe_env_for_test


class ArrangementBase:
    def __init__(self,
                 hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                 process_execution_settings: ProcessExecutionSettings = with_no_timeout(),
                 ):
        self.hds_contents = hds_contents
        self.process_execution_settings = process_execution_settings


class ArrangementWithSds(ArrangementBase):
    def __init__(self,
                 pre_contents_population_action: TcdsAction = TcdsAction(),
                 hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                 sds_contents: sds_populator.SdsPopulator = sds_populator.empty(),
                 non_hds_contents: non_hds_populator.NonHdsPopulator = non_hds_populator.empty(),
                 tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
                 os_services: OsServices = os_services_access.new_for_current_os(),
                 process_execution_settings=proc_exe_env_for_test(),
                 post_sds_population_action: TcdsAction = TcdsAction(),
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


class ProcessExecutionArrangement:
    def __init__(self,
                 os_services: OsServices = os_services_access.new_for_current_os(),
                 process_execution_settings: ProcessExecutionSettings = with_no_timeout(),
                 ):
        self.os_services = os_services
        self.process_execution_settings = process_execution_settings


class ArrangementPostAct2:
    def __init__(self,
                 tcds: TcdsArrangementPostAct = TcdsArrangementPostAct(),
                 symbols: Optional[SymbolTable] = None,
                 process_execution: ProcessExecutionArrangement = ProcessExecutionArrangement(),
                 ):
        self.symbols = symbol_table_from_none_or_value(symbols)
        self.tcds = tcds
        self.process_execution = process_execution


class ArrangementPostAct(ArrangementWithSds):
    def __init__(self,
                 pre_contents_population_action: TcdsAction = TcdsAction(),
                 hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                 sds_contents: sds_populator.SdsPopulator = sds_populator.empty(),
                 non_hds_contents: non_hds_populator.NonHdsPopulator = non_hds_populator.empty(),
                 tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
                 post_sds_population_action: TcdsAction = TcdsAction(),
                 act_result_producer: ActResultProducer = ActResultProducerFromActResult(),
                 os_services: OsServices = os_services_access.new_for_current_os(),
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

    def as_arrangement_2(self) -> ArrangementPostAct2:
        return ArrangementPostAct2(
            TcdsArrangementPostAct(
                self.tcds_contents,
                self.hds_contents,
                non_hds_populator.multiple([self.non_hds_contents,
                                            self.sds_contents]),
                self.act_result_producer,
                PlainTcdsActionFromTcdsAction(self.pre_contents_population_action,
                                              self.symbols),
                PlainTcdsActionFromTcdsAction(self.post_sds_population_action,
                                              self.symbols),
            ),
            self.symbols,
            ProcessExecutionArrangement(
                self.os_services,
                self.process_execution_settings,
            )
        )
