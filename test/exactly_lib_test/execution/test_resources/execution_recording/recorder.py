class ListElementRecorder:
    def __init__(self,
                 recording_media: list,
                 element):
        self.recording_media = recording_media
        self.element = element

    def record(self):
        self.recording_media.append(self.element)


class ListRecorder:
    def __init__(self):
        self.__element_list = []

    def recording_of(self, element) -> ListElementRecorder:
        return ListElementRecorder(self.__element_list, element)

    @property
    def recorded_elements(self) -> list:
        return self.__element_list
