from typing import Self
from webview import Window, SAVE_DIALOG, OPEN_DIALOG

class API:
  window: Window | None

  def __init__(self: Self):
    self.window = None

  def attach_window(self: Self, window: Window):
    self.window = window

  def close(self: Self):
    if self.window is None: return
    self.window.destroy()
    exit(0)

  def toggle_fullscreen(self: Self):
    if self.window is None: return
    self.window.toggle_fullscreen()

  def save_file(
    self: Self,
    content: str,
    save_name: str,
    file_types: list[str] = [
      "All files (*.*)",
    ],
  ) -> bool:
    if self.window is None: return False
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
    if self.window is None: return None
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

