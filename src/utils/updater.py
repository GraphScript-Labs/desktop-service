from typing import Self, Any

from shutil import copytree, rmtree, move

from os import mkdir, rename, remove, chmod
from os.path import exists

from subprocess import run, Popen
from datetime import datetime
from plistlib import dumps
from zipfile import ZipFile

from utils.appdata import AppData, read, write
from utils.logger import logger

from certifi import where as certifi_where
from ssl import create_default_context

from urllib.request import (
  urlopen,
  urlretrieve,
  build_opener,
  install_opener,
  HTTPSHandler
)

logger.log("Setting up SSL context for URL fetching")

context = create_default_context(cafile=certifi_where())
opener = build_opener(HTTPSHandler(context=context))
install_opener(opener)

logger.log("SSL context setup complete")

def fetch_url(url: str) -> str | None:
  logger.log(f"Fetching URL: {url}")
  with urlopen(url) as response:
    if response.status != 200:
      logger.log(f"Failed to fetch URL: {url}")
      return None

    logger.log(f"Successfully fetched URL: {url}")
    return response.read().decode('utf-8').strip()

class Updater:
  appData: AppData

  def __init__(self: Self, appData: AppData) -> None:
    logger.log("Initializing Updater")
    self.appData = appData

  def web_version(self: Self, repo: str) -> str | None:
    url: str = self.appData.service_url
    branch: str = "latest-release"
    file: str = "version"
    full_url: str = f"{url}/{repo}/{branch}/{file}"
    logger.log(f"Fetching web version for {repo} from {full_url}")
    return fetch_url(full_url)

  def check_updates(self: Self, repo: str) -> bool:
    logger.log(f"Checking updates for repository: {repo}")
    latest_version: str | None = self.web_version(repo)
    current_version: str | None = self.appData.versions.get(repo)

    if latest_version is None:
      logger.log(f"No latest version found for {repo}, skipping update check")
      return False
    
    if current_version is None:
      logger.log(f"No current version found for {repo}, update required")
      return True
    
    web_ver: int = int(latest_version)
    cur_ver: int = int(current_version.strip("v"))

    logger.log(f"Comparing web version")
    if web_ver > cur_ver:
      logger.log(f"Update available for {repo}")
      logger.log(f"{repo}: v{cur_ver} -> v{web_ver}")
      return True
    
    logger.log(f"No update available for {repo}")
    return False
  
  def update(self: Self, repo: str, force: bool=False) -> bool:
    logger.log(f"Updating repository: {repo} with force={force}")
    if not self.check_updates(repo) and not force:
      logger.log(f"No updates available for {repo}, skipping")
      return False
    
    url: str = self.appData.org_url
    branch: str = "latest-release"
    latest_version: str = self.web_version(repo) or ""
    full_url: str = f"{url}/{repo}/archive/refs/heads/{branch}.zip"
    logger.log(f"Downloading update from {full_url} for {repo}")

    datapath: str = self.appData.datapath
    local_path: str = f"{datapath}/{repo}/"
    temp_path: str = f"{datapath}/temp/{repo}"
    release_path: str = f"{local_path}/v{latest_version}"

    logger.log(f"Preparing paths for update")

    if not exists(temp_path):
      logger.log(f"Creating temporary directory: {temp_path}")
      mkdir(temp_path)

    if exists(release_path):
      logger.log(f"Removing old release directory: {release_path}")
      rmtree(release_path)
    
    logger.log(f"Creating local path for update: {local_path}")
    update_zip = urlretrieve(
      full_url,
      f"{temp_path}/{latest_version}.zip"
    )

    with ZipFile(update_zip[0], 'r') as zip_ref:
      logger.log(f"Extracting update zip to: {local_path}")
      zip_ref.extractall(local_path)

      logger.log(f"Renaming extracted folder to: {release_path}")
      rename(
        f"{local_path}/{repo}-{branch}",
        release_path
      )

      logger.log(f"Removing temporary files and directories")
      remove(f"{temp_path}/{latest_version}.zip")
      rmtree(temp_path)

    logger.log(f"Update for {repo} completed")
    if exists(f"{release_path}/setup_hook.py"):
      logger.log(f"Running setup hook for {repo}")

      hook_code: str = read(f"{release_path}/setup_hook.py") or ""
      namespace: dict[str, Any] = {}
      
      exec(hook_code, namespace)
      namespace["run_hook"](release_path, datapath)
      logger.log(f"Setup hook for {repo} executed")

    logger.log(f"Updating version for {repo} to v{latest_version}")
    self.appData.update_version(repo, f"v{latest_version}")
    return True
  
  def build_mac(self: Self):
    logger.log("Building macOS application")

    version: str = self.appData.versions.get("desktop-service", "0")
    runtime_path: str = self.appData.v_path("runtimes")
    d_service_path: str = self.appData.v_path("desktop-service")

    timestamp: float = float(version.strip("v"))
    tdt: datetime = datetime.fromtimestamp(timestamp)
    version: str = tdt.strftime("%Y.%m.%d.%H%M%S")
    short_version: str = tdt.strftime("%Y.%m.%d")

    datapath: str = self.appData.datapath
    build_path: str = f"{datapath}/build"
    assets_path: str = f"{d_service_path}/assets"

    runtime_name: str = "py313-mac"
    runtime_path = f"{runtime_path}/{runtime_name}"

    logger.log(f"Runtime path: {runtime_path}, using runtime: {runtime_name}")

    if exists(build_path):
      logger.log(f"Removing old build directory: {build_path}")
      rmtree(build_path)
    
    if exists(f"{datapath}/GraphScript.app"):
      logger.log(f"Removing old GraphScript.app directory")
      rmtree(f"{datapath}/GraphScript.app")

    logger.log(f"Creating new build directory: {build_path}")
    mkdir(build_path)

    logger.log(f"Copying desktop service files to build path")
    copytree(d_service_path, f"{build_path}/desktop-service")

    logger.log(f"Copying runtime files to build path")
    copytree(runtime_path, f"{build_path}/runtime")

    logger.log(f"Copying assets to build path")
    copytree(assets_path, f"{build_path}/Resources")

    logger.log(f"Creating Info.plist for macOS application")
    info: dict[str, Any] = {
      "CFBundleName": "GraphScript",
      "CFBundleDisplayName": "GraphScript",
      "CFBundleIdentifier": "dev.graphscript.dservice",
      "CFBundleVersion": version,
      "CFBundleShortVersionString": short_version,
      "CFBundlePackageType": "APPL",
      "CFBundleIconFile": "GraphScript.icns",
      "CFBundleExecutable": "launcher",
      "CFBundleURLTypes": [
        {
          "CFBundleURLName": "GraphScript URL",
          "CFBundleURLSchemes": ["graphscript"]
        }
      ]
    }

    logger.log(f"Writing Info.plist to {build_path}/Info.plist")
    write(
      f"{build_path}/Info.plist",
      dumps(info).decode('utf-8')
    )

    logger.log(f"Creating MacOS directory in build path")
    launcher_code: list[str] = [
      """#!/bin/bash""",
      """DIR="$(cd "$(dirname "$0")" && pwd)\"""",
      """RUNTIME_DIR="$DIR/../runtime\"""",
      """SOURCE_DIR="$DIR/../desktop-service/src\"""",
      """export PYTHONPATH="$RUNTIME_DIR/packages\"""",
      """$RUNTIME_DIR/bin/python3 "$SOURCE_DIR/main.py\" "$@\"""",
    ]

    logger.log(f"Writing launcher script to {build_path}/MacOS/launcher")
    write(
      f"{build_path}/MacOS/launcher",
      "\n".join(launcher_code)
    )

    logger.log(f"Creating PkgInfo file in build path")
    write(f"{build_path}/PkgInfo", "APPL????")

    logger.log(f"Setting permissions for launcher and runtime")
    chmod(f"{build_path}/MacOS/launcher", 0o755)
    chmod(f"{build_path}/runtime/bin/python3", 0o755)

    logger.log(f"Setting up application directory structure")
    mkdir(f"{datapath}/GraphScript.app")
    rename(build_path, f"{datapath}/GraphScript.app/Contents")

    if exists("/Applications/GraphScript.app"):
      logger.log(f"Removing existing GraphScript.app from /Applications")
      try:
        rmtree("/Applications/GraphScript.app")
      except PermissionError:
        logger.log(f"Permission denied, trying with sudo")
        run([
          "sudo", "rm", "-rf", "/Applications/GraphScript.app"
        ])
    
    logger.log(f"Moving GraphScript.app to /Applications")
    try:
      move(
        f"{datapath}/GraphScript.app",
        "/Applications/GraphScript.app"
      )
    except PermissionError:
      logger.log(f"Permission denied, trying with sudo")
      run([
        "sudo", "mv", f"{datapath}/GraphScript.app",
        "/Applications/GraphScript.app"
      ])

    logger.log(f"macOS application build complete")
    Popen([
      "/bin/bash",
      "-c",
      "sleep 2 && open /Applications/GraphScript.app"
    ])

    logger.log(f"macOS application launched successfully")

