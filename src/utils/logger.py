from typing import Self, Callable

from os import makedirs
from os.path import exists

from datetime import datetime

class LogSystem:
  logs: list[str] = []
  logpath: str | None = None

  def __init__(self: Self) -> None:
    self.logs = []
    self.logpath = None

  def log(self: Self, message: str = "") -> None:
    self.logs.append(message)
    if not self.logpath: return
    with open(self.logpath, 'a') as f:
      f.write(f"{message}\n")

  def set_folder(self: Self, folderpath: str) -> Self:
    if not exists(folderpath):
      makedirs(folderpath)

    filename: str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    self.logpath = f"{folderpath}/{filename}.log"

    with open(self.logpath, 'w') as f:
      f.write("")

    with open(self.logpath, 'a') as f:
      for log in self.logs:
        f.write(f"{log}\n")

    return self

def invoke_immediately(
  func: Callable[[], LogSystem]
) -> LogSystem:
  return func()

@invoke_immediately
def logger() -> LogSystem:
  return LogSystem()

