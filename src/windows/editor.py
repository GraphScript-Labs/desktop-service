from typing import Self

from utils.appdata import AppData
from utils.webhost import host
from utils.logger import logger

from windows.base import Base
from windows.console import Console

from webview import (
  SAVE_DIALOG,
  OPEN_DIALOG,
)

class Editor(Base):
  project_id: str
  app_data: AppData

  def __init__(
    self: Self,
    url: str,
    project_id: str,
    app_data: AppData,
  ):
    logger.log(f'Initializing editor for project ID: {project_id}')
    self.project_id = project_id
    self.app_data = app_data

    super().__init__(
      url=url,
      title='GraphScript',
    )

  def save_file(
    self: Self,
    content: str,
    save_name: str,
    file_types: list[str] = [
      "All files (*.*)",
    ],
  ) -> bool:
    logger.log(f'Saving file: {save_name}')
    path = self.window.create_file_dialog(
      SAVE_DIALOG,
      save_filename=save_name,
      file_types=file_types,
    )

    if not path:
      logger.log('Save operation cancelled by user.')
      return False
    
    with open(str(path), 'w') as file:
      file.write(content)
    
    logger.log(f'File saved successfully at: {path}')
    return True
  
  def load_file(
    self: Self,
    file_types: list[str] = [
      "All files (*.*)",
    ],
  ) -> str | None:
    logger.log('Loading file...')
    path = self.window.create_file_dialog(
      OPEN_DIALOG,
      file_types=file_types,
      allow_multiple=False,
    )

    if not path:
      logger.log('Load operation cancelled by user.')
      return None

    path = str(tuple(path)[0])
    with open(path, 'r') as file:
      content = file.read()
    
    logger.log(f'File loaded successfully from: {path}')
    return content
  
  def load_project_id(self: Self) -> str | None:
    logger.log(f'Loading project ID: {self.project_id}')
    return self.project_id
  
  def backup_project(
    self: Self,
    content: str,
  ) -> bool:
    path: str = f"projects/pr_{self.project_id}/lastload.json"
    logger.log(f'Saving project backup at: {path}')
    
    self.app_data.store_data(path, content)
    logger.log(f'Project backup saved at: {path}')
    
    return True
  
  def restore_project(
    self: Self,
  ) -> str | None:
    path: str = f"projects/pr_{self.project_id}/lastload.json"
    logger.log(f'Restoring project from: {path}')
    return self.app_data.fetch_data(path)
  
  def run_project(self: Self, script: str) -> None:
    logger.log(f'Running project with ID: {self.project_id}')

    console_path: str = self.app_data.v_path("console")
    script_path: str = f"projects/pr_{self.project_id}/console/entry.gsam"
    port, _ = host(console_path)

    logger.log(f'Hosting console at port: {port}')
    self.app_data.store_data(
      script_path,
      script,
    )

    logger.log(f'Launching console for script: {script_path}')
    Console(
      f"http://localhost:{port}/",
      f"{self.app_data.datapath}/data/{script_path}",
    )

