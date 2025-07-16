from os import mkdir

def write(filepath: str, content: str) -> bool:
  with open(filepath, 'w') as file:
    file.write(content)
  
  return True

def run_hook(release_path: str, data_path: str) -> None:
  mkdir(f"{release_path}/configs")
  configs: dict[str, str] = {
    "datapath": data_path,
    "service_url": "https://raw.githubusercontent.com/GraphScript-Labs",
    "org_url": "https://github.com/GraphScript-Labs",
    "repos": "\n".join([
      "launcher",
      "editor",
      "desktop-service",
      "runtimes",
    ])
  }

  for config in configs:
    write(
      f"{release_path}/configs/{config}.txt",
      configs[config]
    )

