from typing import Any, Self, Callable

from os import chdir
from threading import Thread
from random import randint
from functools import partial

from http.server import HTTPServer, SimpleHTTPRequestHandler

from utils.logger import logger

class SilentHandler(SimpleHTTPRequestHandler):
  def __init__(
    self: Self,
    *args: Any,
    directory: str | None = None,
    **kwargs: Any,
  ) -> None:
    logger.log(f"Initializing SilentHandler with directory: {directory}")
    super().__init__(*args, directory=directory, **kwargs)

  def log_message(self, *_, **__: Any) -> None:
    logger.log("SilentHandler received a request, but not logging it")
    return

def host(path: str) -> tuple[int, Thread]:
  logger.log(f"Starting web host for path: {path}")
  PORT: int = randint(49152, 65535)
  logger.log(f"Selected random port: {PORT}")

  def start_server(path: str, port: int) -> None:
    logger.log(f"Starting HTTP server on port: {port} with path: {path}")

    chdir(path)
    server_args: tuple[
      tuple[str, int],
      Callable[..., SimpleHTTPRequestHandler]
    ] = (
      ("localhost", port),
      partial(SilentHandler, directory=path),
    )
    
    with HTTPServer(*server_args) as httpd:
      logger.log(f"HTTP server started on port: {port}")
      httpd.serve_forever()

  logger.log(f"Creating thread for HTTP server on port: {PORT}")
  thread: Thread = Thread(
    target=start_server,
    args=(path, PORT),
    daemon=True
  )

  logger.log(f"Starting thread for HTTP server on port: {PORT}")
  thread.start()
  
  return PORT, thread

