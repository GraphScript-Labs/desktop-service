from utils.appdata import AppData
from utils.updater import Updater
from utils.webhost import host

from windows.launcher import Launcher
from webview import start

def main():
  appData: AppData = AppData()
  updater: Updater = Updater(appData)
  
  launcher_path: str = appData.v_path("launcher")
  port, _ = host(launcher_path)

  Launcher(f"http://localhost:{port}/", appData, updater)
  start()

if __name__ == '__main__':
  main()

