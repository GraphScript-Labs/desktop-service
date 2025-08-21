from webview.menu import Menu, MenuAction

from windows.launcher import Launcher

def create_menu(app_data, updater):
  FileMenu = Menu(
    title="File",
    items=[
      MenuAction(
        title="Open Launcher",
        function=lambda: Launcher(app_data, updater)
      ),
    ]
  )

  CombinedMenu = [FileMenu]
  return CombinedMenu

