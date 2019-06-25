from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional

from exactly_lib.cli.program_modes.test_suite.settings import TestSuiteExecutionSettings
from exactly_lib.processing.standalone.settings import TestCaseExecutionSettings


class RequestVariant:
    pass


class SymbolInspectionRequest:
    def __init__(self,
                 case_execution_settings: Optional[TestCaseExecutionSettings],
                 suite_execution_settings: Optional[TestSuiteExecutionSettings],
                 variant: RequestVariant):
        self.case_execution_settings = case_execution_settings
        self.suite_execution_settings = suite_execution_settings
        self.variant = variant

    @staticmethod
    def new_for_case(execution_settings: TestCaseExecutionSettings,
                     variant: RequestVariant) -> 'SymbolInspectionRequest':
        return SymbolInspectionRequest(execution_settings,
                                       None,
                                       variant)

    @staticmethod
    def new_for_suite(execution_settings: TestSuiteExecutionSettings,
                      variant: RequestVariant) -> 'SymbolInspectionRequest':
        return SymbolInspectionRequest(None,
                                       execution_settings,
                                       variant)

    @property
    def is_inspect_test_case(self) -> bool:
        return self.case_execution_settings is not None

    @property
    def case_settings(self) -> TestCaseExecutionSettings:
        if self.case_execution_settings is None:
            raise ValueError('Is suite settings')
        else:
            return self.case_execution_settings

    @property
    def suite_settings(self) -> TestSuiteExecutionSettings:
        if self.suite_execution_settings is None:
            raise ValueError('Is case settings')
        else:
            return self.suite_execution_settings


class RequestVariantList(RequestVariant):
    pass


class RequestVariantIndividual(RequestVariant):
    def __init__(self,
                 name: str,
                 list_references: bool):
        self.name = name
        self.list_references = list_references


RET = TypeVar('RET')


class RequestVariantVisitor(Generic[RET], ABC):
    def visit(self, variant: RequestVariant) -> RET:
        if isinstance(variant, RequestVariantList):
            return self.visit_list(variant)
        elif isinstance(variant, RequestVariantIndividual):
            return self.visit_individual(variant)
        else:
            raise TypeError('Unknown {}: {}'.format(RequestVariant, str(variant)))

    @abstractmethod
    def visit_list(self, list_variant: RequestVariantList) -> RET:
        pass

    @abstractmethod
    def visit_individual(self, individual_variant: RequestVariantIndividual) -> RET:
        pass
