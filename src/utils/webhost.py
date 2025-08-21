from typing import Any, Self, Callable, TypeAlias

from os import chdir
from threading import Thread
from random import randint
from functools import partial

from http.server import HTTPServer, SimpleHTTPRequestHandler

from utils.logger import logger

class ActiveServerData:
  server: HTTPServer | None
  thread: Thread | None

  def __init__(self: Self) -> None:
    logger.log("Initializing ActiveServerData")
    self.server = None
    self.thread = None

  def setServer(self: Self, server: HTTPServer) -> None:
    logger.log("Setting server in ActiveServerData")
    self.server = server

  def setThread(self: Self, thread: Thread) -> None:
    logger.log("Setting thread in ActiveServerData")
    self.thread = thread

active_servers: dict[int, ActiveServerData] = {}

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

  active_servers[PORT] = ActiveServerData()

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
      active_servers[port].setServer(httpd)
      httpd.serve_forever()

  logger.log(f"Creating thread for HTTP server on port: {PORT}")
  thread: Thread = Thread(
    target=start_server,
    args=(path, PORT),
    daemon=True
  )

  logger.log(f"Starting thread for HTTP server on port: {PORT}")
  active_servers[PORT].setThread(thread)
  thread.start()
  
  return PORT, thread

def close_server(port: int) -> None:
  logger.log(f"Closing server on port: {port}")
  if port not in active_servers:
    logger.log(f"No active server found on port: {port}")
    return
  
  server_data = active_servers[port]
  if server_data.server:
    server_data.server.shutdown()
    logger.log(f"Server on port {port} has been shut down")
  
  if server_data.thread:
    server_data.thread.join()
    logger.log(f"Thread for port {port} has been joined")
  
  del active_servers[port]
  logger.log(f"Removed active server data for port: {port}")

