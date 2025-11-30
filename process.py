# process.py (only the changed part shown)
import threading
import time
from dataclasses import dataclass, field
from typing import Optional

TIME_SCALE = 1  # 1 وحدة زمنية = 1 ثانية (أو حسب إعدادك)

@dataclass
class Process:
    pid: str
    arrival_time: int
    burst_time: int
    priority: int = 0

    remaining_time: int = field(init=False)
    start_time: Optional[float] = None
    completion_time: Optional[float] = None
    response_time: Optional[float] = None
    waiting_time: float = 0
    turnaround_time: Optional[float] = None

    _run_event: threading.Event = field(default_factory=threading.Event, init=False, repr=False)
    _terminate_event: threading.Event = field(default_factory=threading.Event, init=False, repr=False)
    _thread: threading.Thread = field(default=None, init=False, repr=False)

    def __post_init__(self):
        self.remaining_time = self.burst_time
        self._thread = threading.Thread(target=self._run, name=f"Process-{self.pid}")
        self._thread.daemon = True

    def start_thread(self):
        self._thread.start()

    def allow_run(self):
        if self.start_time is None:
            self.start_time = time.time()
            self.response_time = self.start_time  # absolute timestamp; scheduler will compute relative response.
        self._run_event.set()

    def pause_run(self):
        self._run_event.clear()

    def terminate(self):
        self._terminate_event.set()
        self._run_event.set()

    def join(self):
        self._thread.join()

    def _run(self):
        while not self._terminate_event.is_set() and self.remaining_time > 0:
            self._run_event.wait()
            if self._terminate_event.is_set():
                break
            # تنفيذ وحدة زمنية
            time.sleep(1 * TIME_SCALE)
            self.remaining_time -= 1
            print(f"[{time.time():.2f}] {self.pid}: executed 1 unit, remaining={self.remaining_time}")

        if self.remaining_time <= 0:
            # فقط نثبت وقت الإنتهاء هنا كـ timestamp حقيقي
            self.completion_time = time.time()
            print(f"[{time.time():.2f}] {self.pid}: completed execution")

# import threading
# import time
# from dataclasses import dataclass, field
# from typing import Optional

# # كل وحدة زمنية = TIME_SCALE ثانية في الواقع (لتسريع السيموليشن)
# TIME_SCALE = 0.25

# @dataclass
# class Process:
#     pid: str
#     arrival_time: int
#     burst_time: int
#     priority: int = 0

#     remaining_time: int = field(init=False)
#     start_time: Optional[float] = None      # absolute time when first got CPU
#     completion_time: Optional[float] = None # absolute time when finished
#     response_time: Optional[float] = None   # alias for start_time
#     waiting_time: float = 0
#     turnaround_time: Optional[float] = None

#     _run_event: threading.Event = field(default_factory=threading.Event, init=False, repr=False)
#     _terminate_event: threading.Event = field(default_factory=threading.Event, init=False, repr=False)
#     _thread: threading.Thread = field(default=None, init=False, repr=False)

#     def __post_init__(self):
#         self.remaining_time = self.burst_time
#         # thread object created here; if we need to re-run we recreate in scheduler.reset
#         self._thread = threading.Thread(target=self._run, name=f"Process-{self.pid}")
#         self._thread.daemon = True

#     def start_thread(self):
#         # start the underlying thread if not running
#         if not self._thread.is_alive():
#             self._thread = threading.Thread(target=self._run, name=f"Process-{self.pid}")
#             self._thread.daemon = True
#             self._thread.start()

#     def allow_run(self):
#         # record first start time (response)
#         if self.start_time is None:
#             self.start_time = time.time()
#             self.response_time = self.start_time
#         self._run_event.set()

#     def pause_run(self):
#         self._run_event.clear()

#     def terminate(self):
#         self._terminate_event.set()
#         self._run_event.set()

#     def join(self, timeout=None):
#         if self._thread is not None:
#             self._thread.join(timeout)

#     def _run(self):
#         # core of process: waits until allowed, executes 1 unit at a time (TIME_SCALE seconds)
#         # stops when remaining_time reaches 0 or terminate flag set
#         print(f"[{time.time():.2f}] {self.pid}: thread started, waiting for CPU")
#         while not self._terminate_event.is_set() and self.remaining_time > 0:
#             # wait until scheduler allows running
#             self._run_event.wait()
#             if self._terminate_event.is_set():
#                 break
#             # simulate doing 1 time unit of work
#             time.sleep(TIME_SCALE)
#             # decrement the remaining time (only this thread touches remaining_time)
#             self.remaining_time -= 1
#             # if finished, record completion time
#             if self.remaining_time <= 0:
#                 self.completion_time = time.time()
#                 self.turnaround_time = self.completion_time - (self.start_time or self.completion_time)
#                 # clear run event to avoid further sleeping
#                 self._run_event.clear()
#                 break
