from enum import Enum
from pyrealtime.layer import MultiOutputMixin, ProducerMixin, ThreadLayer
import time

try:
  from enum import auto
except ImportError:
    __my_enum_auto_id = 0

    def auto() -> int:
        global __my_enum_auto_id
        i = __my_enum_auto_id
        __my_enum_auto_id += 1
        return i


class ScriptState(Enum):
    STATE_SHOW_PROMPT = auto()
    STATE_PROMPT_READY = auto()
    STATE_PRE_PAUSE = auto()
    STATE_RECORD = auto()
    STATE_STOP_RECORD = auto()
    STATE_RESET = auto()


class ScriptProducer(MultiOutputMixin, ProducerMixin, ThreadLayer):

    def __init__(self, record_time=0, pre_pause_time=0, post_pause_time=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.script = None
        self.step = 0
        self.state = ScriptState.STATE_SHOW_PROMPT
        self.record_time = record_time
        self.pre_pause_time = pre_pause_time
        self.post_pause_time = post_pause_time
        self.can_advance = True

    def initialize(self):
        super().initialize()
        self.script = self.make_script()

    def make_script(self):
        raise NotImplementedError

    def get_input(self):
        if self.step < len(self.script):
            state, data = self.do_single_input(self.script[self.step])
            data['state'] = state
            return data
        else:
            time.sleep(1)
            return None

    def do_state_prompt(self, script_entry):
        return ScriptState.STATE_PROMPT_READY, {}

    def do_state_prompt_ready(self, script_entry):
        return ScriptState.STATE_PRE_PAUSE, {}

    def do_state_pre_pause(self, script_entry):
        time.sleep(self.pre_pause_time)
        return ScriptState.STATE_RECORD, {}

    def do_state_record(self, script_entry):
        time.sleep(self.record_time)
        return ScriptState.STATE_STOP_RECORD, {}

    def do_state_stop_record(self, script_entry):
        time.sleep(self.post_pause_time)
        self.step += 1
        return ScriptState.STATE_RESET, {}

    def do_state_reset(self):
        if self.can_advance:
            return ScriptState.STATE_SHOW_PROMPT, {}
        else:
            return ScriptState.STATE_RESET, {}

    def do_single_input(self, script_entry):

        state = data = None

        if self.state == ScriptState.STATE_SHOW_PROMPT:
            state, data = self.do_state_prompt(script_entry)
        elif self.state == ScriptState.STATE_PROMPT_READY:
            state, data = self.do_state_prompt_ready(script_entry)
        elif self.state == ScriptState.STATE_PRE_PAUSE:
            state, data = self.do_state_pre_pause(script_entry)
        elif self.state == ScriptState.STATE_RECORD:
            state, data = self.do_state_record(script_entry)
        elif self.state == ScriptState.STATE_STOP_RECORD:
            state, data = self.do_state_stop_record(script_entry)
        elif self.state == ScriptState.STATE_RESET:
            state, data = self.do_state_reset()

        self.state = state

        return state, data
