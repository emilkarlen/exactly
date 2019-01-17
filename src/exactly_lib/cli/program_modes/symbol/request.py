from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from exactly_lib.processing.standalone.settings import TestCaseExecutionSettings


class RequestVariant:
    pass


class SymbolInspectionRequest:
    def __init__(self,
                 case_execution_settings: TestCaseExecutionSettings,
                 variant: RequestVariant):
        self.case_execution_settings = case_execution_settings
        self.variant = variant


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
