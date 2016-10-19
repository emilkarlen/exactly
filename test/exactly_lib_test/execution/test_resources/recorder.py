from exactly_lib.execution.phase_step import PhaseStep


class Recorder:
    def __init__(self):
        self.phaseStep2recording = dict()
        self.list_recorder = []

    def set_phase_step_recording(self,
                                 phase_step: PhaseStep,
                                 recording):
        self.phaseStep2recording[phase_step] = recording

    def recording_for_phase(self,
                            phase_step: PhaseStep):
        return self.phaseStep2recording[phase_step]

    def add_list_recording(self,
                           recording):
        self.list_recorder.append(recording)

    def add_list_recordings(self,
                            recordings: list):
        self.list_recorder.extend(recordings)
