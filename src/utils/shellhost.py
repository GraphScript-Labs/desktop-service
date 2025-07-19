from typing import IO, Self, Callable, TypeAlias

from subprocess import Popen, PIPE, STDOUT
from threading import Thread

OutputCallback: TypeAlias = Callable[[str], None]
FinishedCallback: TypeAlias = Callable[[], None]

class ShellProcess:
  process: Popen[str] | None = None
  output_callbacks: list[OutputCallback] = []
  finished_callbacks: list[FinishedCallback] = []

  def __init__(
    self: Self,
    args: list[str],
    output_callbacks: list[OutputCallback],
    finished_callbacks: list[FinishedCallback] = [],
  ) -> None:
    self.output_callbacks = output_callbacks
    self.finished_callbacks = finished_callbacks
    self.process = Popen(
      args,
      stdin=PIPE,
      stdout=PIPE,
      stderr=STDOUT,
      universal_newlines=True
    )

    thread = Thread(
      target=self.reader_thread,
      args=(self.process.stdout,)
    )

    thread.daemon = True
    thread.start()

  def on_flush(self: Self, chunk: str):
    for callback in self.output_callbacks:
      callback(chunk)

  def alert_finished(self: Self) -> None:
    for callback in self.finished_callbacks:
      callback()
  
  def reader_thread(self: Self, stdout_pipe: IO[str] | None):
    if not stdout_pipe:
      return
    
    buffer = ""

    while True:
      char = stdout_pipe.read(1)

      if not char:
        if buffer:
          self.on_flush(buffer)
          buffer = ""
        
        self.alert_finished()
        break

      buffer += char

      if char in ['\n', '\r']:
        self.on_flush(buffer)
        buffer = ""
  
  def push_input(self: Self, input_data: str) -> None:
    if self.process and self.process.stdin:
      self.process.stdin.write(input_data + "\n")
      self.process.stdin.flush()

  def terminate(self: Self) -> None:
    if self.process:
      self.process.terminate()
      self.process.wait()
      self.process = None

