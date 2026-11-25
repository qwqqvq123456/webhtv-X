#!/usr/bin/env python3
"""Post-build guard: prove the APK is signed by our key and points at our update host.

Two failures are worth catching at build time rather than on the phone:

* a signing key drift makes every in-app update fail with "signatures do not match" only on the
  device, long after the build looked fine;
* an update URL that still points upstream would install the official build over this fork.

The check is deliberately about the packaged artifact, not the sources, so it also catches a
stale/cached build output.
"""
import argparse
import re
import subprocess
import sys
import zipfile

FORK_OWNER = b"qwqqvq123456"
# Only the release-download path matters here: the About screen may legitimately still link to the
# upstream project page, but an update URL must never resolve to the upstream repository.
UPSTREAM_RELEASE_PATH = b"github.com/Silent1566/webhtv/releases"
FORK_RELEASE_PATH = b"github.com/qwqqvq123456/webhtv/releases"


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apk", required=True)
    parser.add_argument("--expect-sha256", required=True,
                        help="expected signing certificate SHA-256 fingerprint")
    parser.add_argument("--expect-code", required=True, type=int)
    parser.add_argument("--expect-version", required=True)
    args = parser.parse_args()

    problems = []

    aapt2 = run(["bash", "-lc", "find \"${ANDROID_HOME:-$ANDROID_SDK_ROOT}/build-tools\" -type f -name aapt2 | sort | tail -n 1"]).stdout.strip()
    badging = run([aapt2, "dump", "badging", args.apk]).stdout
    code = re.search(r"versionCode='(\d+)'", badging)
    version = re.search(r"versionName='([^']*)'", badging)
    code = int(code.group(1)) if code else 0
    version = version.group(1) if version else ""
    print(f"package: versionCode={code} versionName={version}")
    if code != args.expect_code:
        problems.append(f"versionCode {code} != manifest {args.expect_code}")
    if version != args.expect_version:
        problems.append(f"versionName {version} != manifest {args.expect_version}")

    apksigner = run(["bash", "-lc", "find \"${ANDROID_HOME:-$ANDROID_SDK_ROOT}/build-tools\" -type f -name apksigner | sort | tail -n 1"]).stdout.strip()
    verify = run([apksigner, "verify", "--print-certs", args.apk])
    print(verify.stdout.strip()[:600])
    if verify.returncode != 0:
        problems.append("apksigner verify failed: " + verify.stderr.strip()[:200])
    digest = re.search(r"certificate SHA-256 digest:\s*([0-9a-fA-F]+)", verify.stdout)
    if not digest:
        problems.append("no signing certificate digest in apksigner output")
    else:
        actual = digest.group(1).lower()
        expected = args.expect_sha256.replace(":", "").lower()
        print(f"signer sha256: {actual}")
        if actual != expected:
            problems.append(f"signer {actual[:16]}... != expected {expected[:16]}...")

    fork_hits, upstream_hits, dex_count = 0, 0, 0
    with zipfile.ZipFile(args.apk) as archive:
        for name in archive.namelist():
            if not name.endswith(".dex"):
                continue
            dex_count += 1
            blob = archive.read(name)
            fork_hits += blob.count(FORK_RELEASE_PATH)
            upstream_hits += blob.count(UPSTREAM_RELEASE_PATH)
    print(f"dex: {dex_count} files, fork release url hits={fork_hits}, upstream release url hits={upstream_hits}")
    if fork_hits == 0:
        problems.append("no fork release URL inside the APK; update check would still hit upstream")
    if upstream_hits:
        problems.append(f"upstream release URL still present in dex ({upstream_hits} hits)")

    print()
    if problems:
        print("APK VERIFICATION FAILED")
        for item in problems:
            print(" -", item)
        sys.exit(1)
    print("APK VERIFICATION PASSED")


if __name__ == "__main__":
    main()
