#!/usr/bin/env python3
"""Generate the update manifest the Android client reads from the update-channel release.

The client only needs five fields to decide whether a build is installable, but the manifest also
carries the absolute APK URL, size and digest so the download can be verified end to end.
"""
import argparse
import hashlib
import json
import os


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apk", required=True)
    parser.add_argument("--channel", required=True, choices=["stable", "beta"])
    parser.add_argument("--tag", required=True)
    parser.add_argument("--version-name", required=True)
    parser.add_argument("--code", required=True, type=int)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--notes", default="")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    if args.code <= 0:
        raise SystemExit("versionCode must be positive")

    apk_name = os.path.basename(args.apk)
    url = "https://github.com/{repo}/releases/download/{tag}/{name}".format(
        repo=args.repo, tag=args.tag, name=apk_name
    )
    manifest = {
        "name": args.tag,
        "versionName": args.version_name,
        "desc": "{tag} - {name}".format(tag=args.tag, name=apk_name),
        "channel": args.channel,
        "code": args.code,
        "apk": url,
        "size": os.path.getsize(args.apk),
        "sha256": sha256(args.apk),
        "notes": args.notes.strip(),
        "downloads": {"github": {"url": url}},
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print("wrote {out}: {tag} code={code} size={size}".format(
        out=args.out, tag=args.tag, code=args.code, size=manifest["size"]))


if __name__ == "__main__":
    main()
