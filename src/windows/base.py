from typing import Self
from webview import (
  create_window,
  Window,
)

from utils.logger import logger

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
    min_dims: tuple[int, int] = (200, 100),
  ) -> None:
    logger.log(f'Creating window "{title}"')
    self.window = create_window(
      title=title,
      url=url,
      js_api=self,
      width=dims[0],
      height=dims[1],
      min_size=min_dims,
      transparent=acryllic,
      vibrancy=acryllic,
      frameless=frameless,
      easy_drag=fulldrag,
      resizable=resizable,
    )

  def close(self: Self) -> None:
    logger.log(f'Closing window "{self.window.title}"')
    self.window.destroy()
    exit(0)

  def toggle_fullscreen(self: Self) -> None:
    logger.log(f'Toggling fullscreen for window "{self.window.title}"')
    self.window.toggle_fullscreen()

