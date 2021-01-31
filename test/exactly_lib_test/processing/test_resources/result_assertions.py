from typing import Optional

from exactly_lib.execution.full_execution.result import FullExeResultStatus, FullExeResult
from exactly_lib.processing.test_case_processing import Status, AccessErrorType, Result, ErrorInfo
from exactly_lib.section_document.source_location import SourceLocationPath
from exactly_lib.test_case.error_description import ErrorDescription
from exactly_lib_test.execution.full_execution.test_resources import result_assertions as asrt_full_exe_result
from exactly_lib_test.section_document.test_resources import source_location_assertions as asrt_source_loc
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def error_info_matches(description: Assertion[Optional[ErrorDescription]] = asrt.anything_goes(),
                       source_location_path: Assertion[Optional[SourceLocationPath]] = asrt.anything_goes(),
                       section_name: Assertion[Optional[str]] = asrt.anything_goes()) -> Assertion[ErrorInfo]:
    return asrt.is_instance_with__many(
        ErrorInfo,
        [
            asrt.sub_component_many(
                'description',
                ErrorInfo.description.fget,
                [
                    asrt.is_none_or_instance(ErrorDescription),
                    description,
                ]
            ),
            asrt.sub_component_many(
                'source_location_path',
                ErrorInfo.source_location_path.fget,
                [
                    asrt.is_none_or_instance_with(
                        SourceLocationPath,
                        asrt_source_loc.matches_source_location_path(),
                    ),
                    source_location_path

                ]
            ),
            asrt.sub_component_many(
                'maybe_section_name',
                ErrorInfo.maybe_section_name.fget,
                [
                    asrt.is_none_or_instance(str),
                    section_name,
                ]
            ),
        ]
    )


def result_matches(status: Assertion[Status] = asrt.anything_goes(),
                   error_info: Assertion[Optional[ErrorInfo]] = asrt.anything_goes(),
                   access_error_type: Assertion[Optional[AccessErrorType]] = asrt.anything_goes(),
                   execution_result: Assertion[Optional[FullExeResult]] = asrt.anything_goes()
                   ) -> Assertion[Result]:
    return asrt.is_none_or_instance_with__many(
        Result,
        [
            asrt.sub_component(
                'status',
                Result.status.fget,
                asrt.is_instance_with(Status, status)
            ),
            asrt.sub_component_many(
                'access_error_type',
                Result.access_error_type.fget,
                [
                    asrt.is_none_or_instance(AccessErrorType),
                    access_error_type,
                ],
            ),
            asrt.sub_component_many(
                'error_info',
                Result.error_info.fget,
                [
                    asrt.is_none_or_instance_with(ErrorInfo, error_info_matches()),
                    error_info,
                ],
            ),
            asrt.sub_component_many(
                'execution_result',
                Result.execution_result.fget,
                [
                    asrt.is_none_or_instance_with(FullExeResult, asrt_full_exe_result.matches()),
                    execution_result,
                ],
            ),
        ])


def result_is_access_error(access_error_type: AccessErrorType) -> Assertion[Result]:
    return result_matches(
        status=asrt.equals(Status.ACCESS_ERROR),
        access_error_type=asrt.equals(access_error_type)
    )


def result_for_executed_status_matches(full_result_status: FullExeResultStatus) -> Assertion[Result]:
    def get_full_result_status(result: Result) -> FullExeResultStatus:
        return result.execution_result.status

    return asrt.and_([
        asrt.sub_component('status',
                           Result.status.fget,
                           asrt.equals(Status.EXECUTED)),
        asrt.sub_component('full_result/status',
                           get_full_result_status,
                           asrt.equals(full_result_status)),
    ])
