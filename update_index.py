import json
import sys
from pathlib import Path

from b2sdk.v2 import B2Api, InMemoryAccountInfo

CREDENTIALS_PATH = Path(__file__).parent / "b2_credentials.json"
INDEX_PATH = Path(__file__).parent / "index.txt"
IGNORE_PREFIXES = ["Movies/_MMM/"]

def load_credentials(path: Path) -> dict:
    if not path.exists():
        sys.exit(
            f"Credentials file not found: {path}."
        )
    return json.loads(path.read_text())


def main() -> None:
    creds = load_credentials(CREDENTIALS_PATH)

    b2_api = B2Api(InMemoryAccountInfo())
    b2_api.authorize_account(
        "production",
        creds["application_key_id"],
        creds["application_key"],
    )
    bucket = b2_api.get_bucket_by_name(creds["bucket_name"])

    filenames = sorted(
        file_version.file_name
        for file_version, _ in bucket.ls(recursive=True)
        if file_version.file_name != "index.txt"
        and not file_version.file_name.endswith(".bzEmpty") # There's one of these for every folder. Useless.
        and not file_version.file_name.startswith(tuple(IGNORE_PREFIXES))
    )
    urls = [bucket.get_download_url(name) for name in filenames]

    INDEX_PATH.write_text("\n".join(urls) + "\n" if urls else "")

    bucket.upload_local_file(
        local_file=str(INDEX_PATH),
        file_name="index.txt",
    )
    print(f"Uploaded index.txt with {len(filenames)} filenames.")


if __name__ == "__main__":
    main()
