from utils.appdata import AppData
from utils.updater import Updater
from utils.webhost import host

from windows.launcher import Launcher
from webview import start

def main():
  app_data: AppData = AppData()
  updater: Updater = Updater(app_data)
  
  launcher_path: str = app_data.v_path("launcher")
  port, _ = host(launcher_path)

  Launcher(f"http://localhost:{port}/", app_data, updater)
  start()

if __name__ == '__main__':
  main()

