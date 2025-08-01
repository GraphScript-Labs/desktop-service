from typing import Self

from utils.updater import Updater
from utils.shellhost import ShellProcess
from utils.appdata import APP_DIR
from utils.logger import logger

from windows.base import Base

from sys import executable

class Console(Base):
  updater: Updater
  shell: ShellProcess
  filepath: str

  def __init__(
    self: Self,
    url: str,
    filepath: str,
  ) -> None:
    logger.log(f'Initializing console for file: {filepath}')
    super().__init__(
      url=url,
      title="GraphScript Launcher",
      dims=(900, 600),
      min_dims=(480, 320),
    )

    self.filepath = filepath
    self.window.events.loaded += self.start_shell

  def close(self: Self) -> None:
    logger.log(f'Closing console for file: {self.filepath}')
    if self.shell: self.shell.terminate()
    super().close()
  
  def add_console_output(self: Self, message: str) -> None:
    logger.log(f'Console output: {message}')
    self.window.evaluate_js(
      f"window.pushConsoleOutput({repr(message)});"
    )
  
  def emit_finished(self: Self) -> None:
    logger.log(f'Emitting finished for console: {self.filepath}')
    self.window.evaluate_js("window.emitFinished();")

  def start_shell(self: Self) -> None:
    logger.log(f'Starting shell for file: {self.filepath}')
    pythonpath: str = f"{APP_DIR}/../runtime/packages"
    lines: list[str] = [
      "import gsam.cli",
      f"gsam.cli.run_file('{self.filepath}')",
    ]

    command: str = " ".join([
      f'PYTHONPATH={pythonpath}',
      f"{executable}",
      f"-c",
      f'"{"; ".join(lines)}"',
    ])

    logger.log(f'Starting shell process with command: {command}')
    self.shell = ShellProcess(
      command,
      [self.add_console_output],
      [self.emit_finished]
    )

  def push_input(self: Self, input_data: str) -> None:
    logger.log(f'Pushing input to shell: {input_data}')
    self.shell.push_input(input_data)

