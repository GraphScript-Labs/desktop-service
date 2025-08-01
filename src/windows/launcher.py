from typing import Self

from utils.appdata import AppData
from utils.updater import Updater
from utils.webhost import host
from utils.logger import logger

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
    logger.log('Initializing Launcher window')

    self.app_data = app_data
    self.updater = updater

    super().__init__(
      url=url,
      title="GraphScript Launcher",
      dims=(800, 600),
      resizable=False,
    )
  
  def get_data(self: Self) -> str:
    logger.log('Fetching launcher data')
    return self.app_data.fetch_data("launcher.json") or ""
  
  def store_data(self: Self, data: str) -> bool:
    logger.log('Storing launcher data')
    return self.app_data.store_data("launcher.json", data)

  def open_project(self: Self, project_id: str) -> None:
    logger.log(f'Opening project with ID: {project_id}')

    editor_path: str = self.app_data.v_path("editor")
    port, _ = host(editor_path)

    logger.log(f'Hosting editor at port: {port}')
    logger.log(f'Opening editor for project ID: {project_id}')

    Editor(
      f"http://localhost:{port}/",
      project_id,
      self.app_data,
    )

    self.close()

  def get_version(self: Self) -> dict[str, str]:
    logger.log('Fetching version information')
    return self.app_data.versions

  def check_updates(self: Self) -> bool:
    logger.log('Checking for updates')
    
    repos = self.app_data.repos
    check_update = self.updater.check_updates
    updatesAvailable = any(map(check_update, repos))
    
    logger.log(f'Updates available: {updatesAvailable}')
    return updatesAvailable
  
  def update(self: Self) -> None:
    logger.log('Updating application')
    updater: Updater = self.updater

    repos = self.app_data.repos
    should_build: bool = updater.check_updates("desktop-service")

    for repo in repos:
      logger.log(f'Updating repository: {repo}')
      updater.update(repo)
    
    if should_build:
      logger.log('Building desktop service after updates')
      updater.build_mac()

    for window in windows:
      logger.log(f'Closing window: {window.title}')
      window.destroy()
      exit(0)

    logger.log('All windows closed, exiting application')
    exit(0)

