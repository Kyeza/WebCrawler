import os
from pathlib import Path

import pytest

from webcrawler_arnoldkyeza.core.datastore.blob_storage import BlobStorage


def test_init_creates_root_directory(tmp_path: Path) -> None:
    root = tmp_path / "blobs-root"

    assert not root.exists()

    storage = BlobStorage(root)

    assert storage.root_path == root
    assert root.exists() and root.is_dir()


@pytest.fixture
def storage(tmp_path: Path) -> BlobStorage:
    return BlobStorage(tmp_path / "blobs")


def test_upload_creates_container_and_writes_bytes(storage: BlobStorage) -> None:
    container = "docs"
    blob_name = "readme.txt"
    data = b"hello world"

    storage.upload(container, blob_name, data)

    blob_path = storage.root_path / container / blob_name
    assert blob_path.exists()
    assert blob_path.read_bytes() == data


def test_upload_overwrites_existing_file(storage: BlobStorage) -> None:
    container = "docs"
    blob_name = "readme.txt"
    first = b"first-version"
    second = b"second-version"

    storage.upload(container, blob_name, first)
    storage.upload(container, blob_name, second)

    blob_path = storage.root_path / container / blob_name
    assert blob_path.exists()
    assert blob_path.read_bytes() == second


def test_upload_nested_blob_name_without_intermediate_dirs_raises(storage: BlobStorage) -> None:
    container = "bin"
    nested_blob = f"subdir{os.sep}child.bin"

    # Act / Assert
    with pytest.raises(FileNotFoundError):
        storage.upload(container, nested_blob, b"data")
