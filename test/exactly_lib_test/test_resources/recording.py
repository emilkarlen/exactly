import unittest
from typing import TypeVar, Generic, List


class MaxNumberOfTimesChecker:
    def __init__(self,
                 put: unittest.TestCase,
                 max_num_times: int,
                 err_msg_object_name: str,
                 err_msg_header: str = '',
                 ):
        self._put = put
        self._max_num_times = max_num_times
        self._err_msg_object_name = err_msg_object_name
        self._err_msg_header = err_msg_header

        self.current_num_invocations = 0

    def register(self, name: str = ''):
        self.current_num_invocations += 1
        if self.current_num_invocations > self._max_num_times:
            self._put.fail('{}Maximum number of {} ({}) exceeded: {} '.format(
                self._err_msg_header_str(name),
                self._err_msg_object_name,
                self._max_num_times,
                self.current_num_invocations,
            )
            )

    def _err_msg_header_str(self, name: str) -> str:
        header = self._err_msg_header + ': ' if self._err_msg_header else ''
        return (
            ''.join((header, ' ', name, ': '))
            if name
            else
            header
        )


T = TypeVar('T')


class SequenceRecorder(Generic[T]):
    def __init__(self):
        self._recordings = []

    def record(self, method: T):
        self._recordings.append(method)

    @property
    def recordings(self) -> List[T]:
        return self._recordings
