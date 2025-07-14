from typing import Self
from webview import (
  create_window,
  Window,
)

class Base:
  window: Window

  def __init__(
    self: Self,
    url: str,
    title: str = 'GraphScript',
    dims: tuple[int, int] = (1200, 800),
    acryllic: bool = True,
    frameless: bool = True,
    fulldrag: bool = False,
    resizable: bool = True,
  ) -> None:
    self.window = create_window(
      title=title,
      url=url,
      js_api=self,
      width=dims[0],
      height=dims[1],
      transparent=acryllic,
      vibrancy=acryllic,
      frameless=frameless,
      easy_drag=fulldrag,
      resizable=resizable,
    )

  def close(self: Self) -> None:
    self.window.destroy()
    exit(0)

  def toggle_fullscreen(self: Self) -> None:
    self.window.toggle_fullscreen()

