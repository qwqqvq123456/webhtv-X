#!/usr/bin/env python3
"""Pull the upstream release notes for one channel so the in-app update dialog shows them.

GitHub releases are repository objects: a fork copies commits, not releases, and merge-upstream
only replays git history. Without this step the manifest we publish carries our own commit
subjects and the user never sees what upstream actually changed.

The lookup is per channel: a stable build reports the newest non-prerelease upstream release, a
beta build reports the newest prerelease. Nothing is invented when upstream leaves the body empty;
the file is simply left blank and the manifest falls back to the build summary.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def fetch(repo, token):
    url = f"https://api.github.com/repos/{repo}/releases?per_page=30"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "webhtv-release-notes",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.loads(response.read().decode())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="Silent1566/webhtv")
    parser.add_argument("--channel", required=True, choices=["stable", "beta"])
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    try:
        releases = fetch(args.repo, token)
    except Exception as error:
        print(f"WARN: 读取上游 release 失败，清单将只带本构建说明: {error}")
        open(args.out, "w").close()
        return

    picked = None
    for release in releases:
        tag = release.get("tag_name") or ""
        if not tag.startswith("v") or release.get("draft"):
            continue
        is_beta = bool(release.get("prerelease")) or "-beta-" in tag
        if (args.channel == "beta") != is_beta:
            continue
        if not (release.get("body") or "").strip():
            continue
        picked = release
        break

    if not picked:
        print(f"WARN: 上游 {args.channel} 通道没有带正文的发布，清单将只带本构建说明")
        open(args.out, "w").close()
        return

    body = picked["body"].strip()
    with open(args.out, "w", encoding="utf-8") as handle:
        handle.write(f"—— 上游 {picked['tag_name']} 更新日志 ——\n\n{body}\n")
    print(f"picked upstream {picked['tag_name']} ({len(body)} chars) -> {args.out}")


if __name__ == "__main__":
    main()
