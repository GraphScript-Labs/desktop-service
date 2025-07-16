from typing import Self

from os import mkdir, makedirs
from os.path import exists, dirname, realpath, join

from sys import argv

cached_data: dict[str, str] = {}
APP_DIR: str = dirname(realpath(argv[0])).rstrip('/src')

def read(filepath: str) -> str | None:
  filepath = join(APP_DIR, filepath)

  if not exists(filepath):
    return None
  
  with open(filepath, 'r') as file:
    return file.read()

def write(filepath: str, content: str) -> bool:
  filepath = join(APP_DIR, filepath)
  folder_path: str = "/".join(filepath.split('/')[:-1])
  
  if not exists(folder_path):
    makedirs(folder_path, exist_ok=True)
  
  with open(filepath, 'w') as file:
    file.write(content)
  
  return True

def read_config(
  config: str,
  cached_return: bool = True
) -> str | None:
  config_path: str = f"configs/{config}.txt"
  if cached_return and config_path in cached_data:
    return cached_data[config_path]
  
  data: str | None = read(config_path)
  if data is None:
    return None

  cached_data[config_path] = data.strip()
  return cached_data[config_path]

class ConfigError(ValueError):
  def __init__(self: Self, message: str) -> None:
    super().__init__(message)
    self.message = message

  def __str__(self: Self) -> str:
    return f"ConfigError: {self.message}"

class AppData:
  setup_success: bool = False
  datapath: str
  service_url: str
  org_url: str
  versions: dict[str, str] = {}
  repos: list[str] = []

  def __init__(self: Self) -> None:
    datapath: str | None = read_config("datapath")
    service_url: str | None = read_config("service_url")
    org_url: str | None = read_config("org_url")
    repos: str | None = read_config("repos")

    if not datapath:
      raise ConfigError("Datapath")
    
    if not service_url:
      raise ConfigError("Service URL")
    
    if not org_url:
      raise ConfigError("Organization URL")
    
    if not repos:
      raise ConfigError("Repositories")

    self.datapath = datapath
    self.service_url = service_url
    self.org_url = org_url
    self.repos = repos.split("\n")

    self.setup_app_data_dir()
    versions_raw: str = read(f"{datapath}/versions.txt") or ""

    for line in versions_raw.split("\n"):
      if not line.strip():
        continue
      
      key, value = line.split(":", 1)
      self.versions[key.strip()] = value.strip()
    
    self.setup_success = True

  def setup_app_data_dir(self: Self) -> None:
    if not exists(self.datapath):
      mkdir(self.datapath)
      mkdir(f"{self.datapath}/data")
      mkdir(f"{self.datapath}/temp")

      with open(f"{self.datapath}/versions.txt", 'w') as file:
        file.write("")
        file.close()

  def v_path(self: Self, repo: str) -> str:
    dpath: str = self.datapath
    vkey: str = self.versions.get(repo, "")

    return f"{dpath}/{repo}/{vkey}/"
  
  def fetch_data(self: Self, file: str) -> str | None:
    return read(f"{self.datapath}/data/{file}")

  def store_data(self: Self, file: str, content: str) -> bool:
    return write(f"{self.datapath}/data/{file}", content)

  def update_versions(self: Self) -> bool:
    content: str = ""

    for repo in self.versions:
      content += f"{repo}:{self.versions[repo]}\n"

    return write(f"{self.datapath}/versions.txt", content.strip())

  def update_version(self: Self, repo: str, version: str) -> None:
    self.versions[repo] = version
    self.update_versions()

