from typing import IO, Self, Callable, TypeAlias

from subprocess import Popen, PIPE
from threading import Thread

from utils.logger import logger

OutputCallback: TypeAlias = Callable[[str], None]
FinishedCallback: TypeAlias = Callable[[], None]

class ShellProcess:
  process: Popen[str] | None = None
  output_callbacks: list[OutputCallback] = []
  finished_callbacks: list[FinishedCallback] = []

  def __init__(
    self: Self,
    args: list[str] | str,
    output_callbacks: list[OutputCallback],
    finished_callbacks: list[FinishedCallback] = [],
  ) -> None:
    logger.log(f"Starting shell process with args: {args}")

    self.output_callbacks = output_callbacks
    self.finished_callbacks = finished_callbacks

    logger.log(f"Starting shell process with args: {args}")
    self.process = Popen(
      args,
      stdin=PIPE,
      stdout=PIPE,
      stderr=PIPE,
      universal_newlines=True,
      shell=True,
    )

    logger.log(f"Starting reader thread for process output")
    thread = Thread(
      target=self.reader_thread,
      args=(self.process.stdout,)
    )

    logger.log(f"Reader thread started for process output")
    thread.daemon = True
    thread.start()

  def on_flush(self: Self, chunk: str):
    logger.log(f"Flushing output chunk: {chunk}")
    for callback in self.output_callbacks:
      callback(chunk)

  def alert_finished(self: Self) -> None:
    logger.log(f"Process finished, calling finished callbacks")
    for callback in self.finished_callbacks:
      callback()
  
  def reader_thread(self: Self, stdout_pipe: IO[str] | None):
    logger.log(f"Reader thread started for process output")
    if not stdout_pipe:
      logger.log(f"No stdout pipe available, exiting reader thread")
      return
    
    buffer = ""
    logger.log(f"Reading process output from stdout pipe")

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
    logger.log(f"Pushing input to shell process: {input_data}")
    if self.process and self.process.stdin:
      logger.log(f"Writing input to process stdin")
      self.process.stdin.write(input_data + "\n")
      self.process.stdin.flush()

  def terminate(self: Self) -> None:
    logger.log(f"Terminating shell process")
    if self.process:
      self.process.terminate()
      self.process.wait()
      self.process = None
      logger.log(f"Shell process terminated")

