from dataclasses import dataclass
from pathlib import Path
from typing import Union

PROJECT_ROOT = Path(__file__).parent.parent.parent


@dataclass
class BlobStorage:
    root_path: Union[str, Path]

    def __post_init__(self):
        try:
            self.root_path = Path(self.root_path) if isinstance(self.root_path, str) else self.root_path
            self.root_path.mkdir(parents=True, exist_ok=True)
        except FileExistsError as e:
            raise e
        except Exception as e:
            raise e

    def _resolve_path(self, container: str, blob_name: str) -> Path:
        container_path = self.root_path / container
        container_path.mkdir(parents=True, exist_ok=True)
        return container_path / blob_name

    def upload(self, container: str, blob_name: str, data: bytes) -> None:
        # remember to compress data with gzip to optimise storage
        path = self._resolve_path(container, blob_name)
        with open(path, 'wb') as f:
            f.write(data)
