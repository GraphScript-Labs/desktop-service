from utils.logger import logger
from utils.appdata import AppData
from utils.updater import Updater
from utils.webhost import host

from windows.launcher import Launcher
from webview import start

from sys import argv

def setup() -> tuple[AppData, Updater]:
  logger.log("Setting up application data and updater")
  app_data: AppData = AppData()
  updater: Updater = Updater(app_data)

  logger.set_folder(f"{app_data.datapath}/logs")
  return app_data, updater

def install() -> None:
  logger.log("Installing GraphScript Desktop Environment")
  app_data, updater = setup()
  
  for repo in app_data.repos:
    logger.log(f"Updating repository: {repo}")
    updater.update(repo, force=True)
  
  logger.log("Building application")
  updater.build_mac()

  logger.log("Installation complete")

def main():
  logger.log("Main function started")

  app_data, updater = setup()
  launcher_path: str = app_data.v_path("launcher")
  port, _ = host(launcher_path)

  logger.log(f"Hosting Launcher on port: {port}")
  Launcher(f"http://localhost:{port}/", app_data, updater)
  start()

if __name__ == '__main__':
  logger.log("Starting GraphScript Desktop Environment")

  if "--setup" in argv:
    install()
    exit(0)
  
  main()

