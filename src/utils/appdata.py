from typing import Self

from os import mkdir, makedirs
from os.path import exists, dirname, realpath, join

from sys import argv

from utils.logger import logger

cached_data: dict[str, str] = {}
APP_DIR: str = dirname(realpath(argv[0])).rstrip('/src')

def read(filepath: str) -> str | None:
  filepath = join(APP_DIR, filepath)
  logger.log(f"Reading file: {filepath}")

  if not exists(filepath):
    logger.log(f"File not found: {filepath}")
    return None
  
  with open(filepath, 'r') as file:
    logger.log(f"File read successfully: {filepath}")
    return file.read()

def write(filepath: str, content: str) -> bool:
  filepath = join(APP_DIR, filepath)
  folder_path: str = "/".join(filepath.split('/')[:-1])

  logger.log(f"Writing to file: {filepath}")
  
  if not exists(folder_path):
    logger.log(f"Creating directory: {folder_path}")
    makedirs(folder_path, exist_ok=True)
  
  with open(filepath, 'w') as file:
    file.write(content)
    logger.log(f"File written successfully: {filepath}")
  
  return True

def read_config(
  config: str,
  cached_return: bool = True
) -> str | None:
  config_path: str = f"configs/{config}.txt"
  logger.log(f"Reading config: {config_path}")

  if cached_return and config_path in cached_data:
    logger.log(f"Returning cached config: {config_path}")
    return cached_data[config_path]
  
  data: str | None = read(config_path)
  if data is None:
    logger.log(f"Config not found: {config_path}")
    return None

  logger.log(f"Config read successfully: {config_path}")
  cached_data[config_path] = data.strip()
  return cached_data[config_path]

class ConfigError(ValueError):
  def __init__(self: Self, message: str) -> None:
    super().__init__(message)
    self.message = message
    logger.log(f"ConfigError: {message}")

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
    logger.log("Initializing AppData")
    self.setup_success = False
    
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

    logger.log(f"Setting up AppData Directory: {self.datapath}")

    self.setup_app_data_dir()
    versions_raw: str = read(f"{datapath}/versions.txt") or ""

    logger.log(f"Reading versions from: {datapath}/versions.txt")
    for line in versions_raw.split("\n"):
      if not line.strip():
        continue
      
      key, value = line.split(":", 1)
      self.versions[key.strip()] = value.strip()
      logger.log(f"Loaded version for {key.strip()}: {value.strip()}")
    
    logger.log(f"Versions loaded: {self.versions}")
    self.setup_success = True

  def setup_app_data_dir(self: Self) -> None:
    logger.log(f"Setting up application data directory: {self.datapath}")

    if not exists(self.datapath):
      logger.log(f"Creating application data directory: {self.datapath}")
      mkdir(self.datapath)

      logger.log(f"Creating subdirectories in: {self.datapath}")
      mkdir(f"{self.datapath}/data")
      mkdir(f"{self.datapath}/temp")

      with open(f"{self.datapath}/versions.txt", 'w') as file:
        logger.log(f"Creating versions file: {self.datapath}/versions.txt")
        file.write("")
        file.close()

  def v_path(self: Self, repo: str) -> str:
    logger.log(f"Getting versioned path for repository: {repo}")

    dpath: str = self.datapath
    vkey: str = self.versions.get(repo, "")

    return f"{dpath}/{repo}/{vkey}/"
  
  def fetch_data(self: Self, file: str) -> str | None:
    logger.log(f"Fetching data from file: {file}")
    return read(f"{self.datapath}/data/{file}")

  def store_data(self: Self, file: str, content: str) -> bool:
    logger.log(f"Storing data to file: {file}")
    return write(f"{self.datapath}/data/{file}", content)

  def update_versions(self: Self) -> bool:
    logger.log("Updating versions file")
    content: str = ""

    for repo in self.versions:
      content += f"{repo}:{self.versions[repo]}\n"

    logger.log(f"Writing updated versions to: {self.datapath}/versions.txt")
    return write(f"{self.datapath}/versions.txt", content.strip())

  def update_version(self: Self, repo: str, version: str) -> None:
    logger.log(f"Updating version for repository: {repo} to {version}")
    self.versions[repo] = version
    self.update_versions()

