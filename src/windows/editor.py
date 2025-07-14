from typing import Self
from windows.base import Base
from webview import (
  SAVE_DIALOG,
  OPEN_DIALOG,
)

class Editor(Base):
  project_id: str

  def __init__(self: Self, url: str, project_id: str):
    self.project_id = project_id
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
    path = self.window.create_file_dialog(
      SAVE_DIALOG,
      save_filename=save_name,
      file_types=file_types,
    )

    if not path: 
      return False
    
    with open(str(path), 'w') as file:
      file.write(content)
    
    return True
  
  def load_file(
    self: Self,
    file_types: list[str] = [
      "All files (*.*)",
    ],
  ) -> str | None:
    path = self.window.create_file_dialog(
      OPEN_DIALOG,
      file_types=file_types,
      allow_multiple=False,
    )

    if not path:
      return None

    path = str(tuple(path)[0])
    with open(path, 'r') as file:
      content = file.read()
    
    return content
  
  def load_project_id(self: Self) -> str | None:
    return self.project_id

