import os

import uvicorn

from repoguard.api import from_environment
from repoguard.sdk import RepoGuard


def main() -> None:
    engine = RepoGuard(os.environ["REPOGUARD_REPOSITORY"], os.environ["REPOGUARD_DATABASE"])
    engine.index(os.environ.get("REPOGUARD_TARGET", "HEAD"), base=os.environ.get("REPOGUARD_BASE"))
    uvicorn.run(from_environment(), host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
