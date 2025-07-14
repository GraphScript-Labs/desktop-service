from typing import Any, Self, Callable

from os import chdir
from threading import Thread
from random import randint
from functools import partial

from http.server import HTTPServer, SimpleHTTPRequestHandler

class SilentHandler(SimpleHTTPRequestHandler):
  def __init__(
    self: Self,
    *args: Any,
    directory: str | None = None,
    **kwargs: Any,
  ) -> None:
    super().__init__(*args, directory=directory, **kwargs)

  def log_message(self, *_, **__: Any) -> None:
    return

def host(path: str) -> tuple[int, Thread]:
  PORT: int = randint(49152, 65535)

  def start_server(path: str, port: int) -> None:
    chdir(path)
    server_args: tuple[
      tuple[str, int],
      Callable[..., SimpleHTTPRequestHandler]
    ] = (
      ("localhost", port),
      partial(SilentHandler, directory=path),
    )
    
    with HTTPServer(*server_args) as httpd:
      httpd.serve_forever()

  thread: Thread = Thread(
    target=start_server,
    args=(path, PORT),
    daemon=True
  )

  thread.start()
  return PORT, thread

