from typing import Self, Any

from shutil import copytree, rmtree, move

from os import mkdir, rename, remove, chmod
from os.path import exists

from subprocess import run
from datetime import datetime
from plistlib import dumps
from zipfile import ZipFile

from utils.appdata import AppData, read, write

from certifi import where as certifi_where
from ssl import create_default_context

from urllib.request import (
  urlopen,
  urlretrieve,
  build_opener,
  install_opener,
  HTTPSHandler
)

context = create_default_context(cafile=certifi_where())
opener = build_opener(HTTPSHandler(context=context))
install_opener(opener)

def fetch_url(url: str) -> str | None:
  with urlopen(url) as response:
    if response.status != 200:
      return None
    
    return response.read().decode('utf-8').strip()

class Updater:
  appData: AppData

  def __init__(self: Self, appData: AppData) -> None:
    self.appData = appData

  def web_version(self: Self, repo: str) -> str | None:
    url: str = self.appData.service_url
    branch: str = "latest-release"
    file: str = "version"
    full_url: str = f"{url}/{repo}/{branch}/{file}"
    return fetch_url(full_url)

  def check_updates(self: Self, repo: str) -> bool:
    latest_version: str | None = self.web_version(repo)
    current_version: str | None = self.appData.versions.get(repo)

    if latest_version is None:
      return False
    
    if current_version is None:
      return True
    
    web_ver: int = int(latest_version)
    cur_ver: int = int(current_version.strip("v"))

    if web_ver > cur_ver:
      return True
    
    return False
  
  def update(self: Self, repo: str, force: bool=False) -> bool:
    if not self.check_updates(repo) and not force:
      return False
    
    url: str = self.appData.org_url
    branch: str = "latest-release"
    latest_version: str = self.web_version(repo) or ""
    full_url: str = f"{url}/{repo}/archive/refs/heads/{branch}.zip"

    datapath: str = self.appData.datapath
    local_path: str = f"{datapath}/{repo}/"
    temp_path: str = f"{datapath}/temp/{repo}"
    release_path: str = f"{local_path}/v{latest_version}"

    if not exists(temp_path):
      mkdir(temp_path)

    if exists(release_path):
      rmtree(release_path)
    
    update_zip = urlretrieve(
      full_url,
      f"{temp_path}/{latest_version}.zip"
    )

    with ZipFile(update_zip[0], 'r') as zip_ref:
      zip_ref.extractall(local_path)
      rename(
        f"{local_path}/{repo}-{branch}",
        release_path
      )

      remove(f"{temp_path}/{latest_version}.zip")
      rmtree(temp_path)

    if exists(f"{release_path}/setup_hook.py"):
      hook_code: str = read(f"{release_path}/setup_hook.py") or ""
      namespace: dict[str, Any] = {}
      
      exec(hook_code, namespace)
      namespace["run_hook"](release_path, datapath)

    self.appData.update_version(repo, f"v{latest_version}")
    return True
  
  def build_mac(self: Self):
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

    if exists(build_path):
      rmtree(build_path)
    
    if exists(f"{datapath}/GraphScript.app"):
      rmtree(f"{datapath}/GraphScript.app")

    mkdir(build_path)

    copytree(d_service_path, f"{build_path}/desktop-service")
    copytree(runtime_path, f"{build_path}/runtime")
    copytree(assets_path, f"{build_path}/Resources")

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

    write(
      f"{build_path}/Info.plist",
      dumps(info).decode('utf-8')
    )

    launcher_code: list[str] = [
      """#!/bin/bash""",
      """DIR="$(cd "$(dirname "$0")" && pwd)\"""",
      """RUNTIME_DIR="$DIR/../runtime\"""",
      """SOURCE_DIR="$DIR/../desktop-service/src\"""",
      """export PYTHONPATH="$RUNTIME_DIR\"""",
      """$RUNTIME_DIR/bin/python3 "$SOURCE_DIR/main.py\" "$@\"""",
    ]

    write(
      f"{build_path}/MacOS/launcher",
      "\n".join(launcher_code)
    )

    write(f"{build_path}/PkgInfo", "APPL????")

    chmod(f"{build_path}/MacOS/launcher", 0o755)
    chmod(f"{build_path}/runtime/bin/python3", 0o755)

    mkdir(f"{datapath}/GraphScript.app")
    rename(build_path, f"{datapath}/GraphScript.app/Contents")

    if exists("/Applications/GraphScript.app"):
      try:
        rmtree("/Applications/GraphScript.app")
      except PermissionError:
        run([
          "sudo", "rm", "-rf", "/Applications/GraphScript.app"
        ])
    
    try:
      move(
        f"{datapath}/GraphScript.app",
        "/Applications/GraphScript.app"
      )
    except PermissionError:
      run([
        "sudo", "mv", f"{datapath}/GraphScript.app",
        "/Applications/GraphScript.app"
      ])

