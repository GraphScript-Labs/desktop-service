from typing import Self, Any

from os import mkdir, rename, remove, rmdir
from os.path import exists

from urllib.request import urlopen, urlretrieve
from zipfile import ZipFile

from utils.appdata import AppData, read

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
  
  def update(self: Self, repo: str) -> bool:
    if not self.check_updates(repo):
      return False
    
    url: str = self.appData.org_url
    branch: str = "latest-release"
    latest_version: str = self.web_version(repo) or ""
    full_url: str = f"{url}/{repo}/archive/refs/heads/{branch}.zip"

    datapath: str = self.appData.datapath
    local_path: str = f"{datapath}/{repo}/"
    temp_path: str = f"{datapath}/temp/{repo}"

    if not exists(temp_path):
      mkdir(temp_path)
    
    update_zip = urlretrieve(
      full_url,
      f"{temp_path}/{latest_version}.zip"
    )

    with ZipFile(update_zip[0], 'r') as zip_ref:
      zip_ref.extractall(local_path)
      rename(
        f"{local_path}/{repo}-{branch}",
        f"{local_path}/v{latest_version}"
      )

      remove(f"{temp_path}/{latest_version}.zip")
      rmdir(temp_path)

    release_path: str = f"{local_path}/v{latest_version}"
    if exists(f"{release_path}/setup_hook.py"):
      hook_code: str = read(f"{release_path}/setup_hook.py") or ""
      namespace: dict[str, Any] = {}
      
      exec(hook_code, namespace)
      namespace["run_hook"](release_path, datapath)

    self.appData.update_version(repo, f"v{latest_version}")
    return True

