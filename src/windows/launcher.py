from typing import Self

from utils.appdata import AppData
from utils.updater import Updater
from utils.webhost import host

from windows.base import Base
from windows.editor import Editor

from webview import windows

class Launcher(Base):
  app_data: AppData
  updater: Updater

  def __init__(
    self: Self,
    url: str,
    app_data: AppData,
    updater: Updater
  ) -> None:
    self.app_data = app_data
    self.updater = updater

    super().__init__(
      url=url,
      title="GraphScript Launcher",
      dims=(800, 600),
      resizable=False,
    )
  
  def get_data(self: Self) -> str:
    default_template: str = '{"projects": []}'
    return self.app_data.fetch_data("launcher.json") or default_template
  
  def store_data(self: Self, data: str) -> bool:
    return self.app_data.store_data("launcher.json", data)

  def open_project(self: Self, project_id: str) -> None:
    editor_path: str = self.app_data.v_path("editor")
    port, _ = host(editor_path)

    Editor(
      f"http://localhost:{port}/",
      project_id,
      self.app_data,
    )

  def get_version(self: Self) -> str:
    return self.app_data.versions["launcher"]

  def check_updates(self: Self) -> bool:
    repos = ["launcher", "editor"]
    return any(map(self.updater.check_updates, repos))
  
  def update(self: Self) -> None:
    repos = ["launcher", "editor"]
    for repo in repos:
      self.updater.update(repo)

    for window in windows:
      window.destroy()
      exit(0)

