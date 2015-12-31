class ListElementRecorder:
    def __init__(self,
                 element_list: list,
                 element: str):
        self.recorder = element_list
        self.element = element

    def record(self):
        self.recorder.append(self.element)


class ListRecorder:
    def __init__(self):
        self.__element_list = []

    def recording_of(self, element: str) -> ListElementRecorder:
        return ListElementRecorder(self.__element_list, element)

    @property
    def recorded_elements(self) -> list:
        return self.__element_list
