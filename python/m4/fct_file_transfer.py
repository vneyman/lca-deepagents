from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent / "output"
OUT_DIR.mkdir(exist_ok=True)


def agent_to_local_transfer(files, out_dir: Path, file_absolute_to_check: str) -> None:
    """Mirror all files the agent wrote in its StateBackend to the local filesystem.

    The agent's StateBackend is untrusted, so we verify that each file path
    stays inside out_dir before writing it. We also only write plain text.
    """

    if file_absolute_to_check not in files:
        raise SystemExit(f"Agent did not write {file_absolute_to_check}")

    out_root = out_dir.resolve()
    print("\nWriting agent files to disk:")

    for path in sorted(files):
        # Map the in-state layout onto OUT_DIR: /output/* lands at the root,
        # /research/<genre>/* keeps its folder structure.
        rel = path[len("/output/"):] if path.startswith("/output/") else path.lstrip("/")
        dest = (out_dir / rel).resolve()

        # The file contents are UNTRUSTED web-search text, and the path came from
        # the agent — so verify the destination stays inside OUT_DIR before writing
        # (reject any ../ traversal), and only ever write plain text.
        if dest != out_root and out_root not in dest.parents:
            print(f"  SKIPPED (escapes output dir): {path}")
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        body = _content(files[path])
        dest.write_text(body, encoding="utf-8")
        print(f"  {path}  ->  {dest.relative_to(out_root)}  ({len(body):,} chars)")


def _content(fd) -> str:
    # FileData entries are dicts keyed by "content" (string, or legacy list).
    body = fd["content"] if isinstance(fd, dict) else fd
    return "\n".join(body) if isinstance(body, list) else body
