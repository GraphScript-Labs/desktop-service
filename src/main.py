from utils.appdata import AppData
from utils.updater import Updater
from utils.webhost import host

from windows.launcher import Launcher
from webview import start

from sys import argv

def setup() -> tuple[AppData, Updater]:
  app_data: AppData = AppData()
  updater: Updater = Updater(app_data)

  return app_data, updater

def install() -> None:
  app_data, updater = setup()
  
  for repo in app_data.repos:
    updater.update(repo)
  
  updater.build_mac()

def main():
  app_data, updater = setup()  
  launcher_path: str = app_data.v_path("launcher")
  port, _ = host(launcher_path)

  Launcher(f"http://localhost:{port}/", app_data, updater)
  start()

if __name__ == '__main__':
  if "setup" in argv:
    install()
    exit(0)
  
  main()

