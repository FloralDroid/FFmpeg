#!/usr/bin/env python3
# Copyright 2026 FloralDroid
# SPDX-License-Identifier: LGPL-2.1-or-later

import argparse
import pathlib
import re
import shutil


def output_name(source: pathlib.Path) -> pathlib.Path:
    if source.parent.name in ("libavcodec", "libavutil"):
        return pathlib.Path(source.parent.name) / source.name
    return pathlib.Path(source.name)


def normalized_config(source: pathlib.Path) -> str:
    contents = source.read_text(encoding="utf-8")
    is_arm64 = "#define ARCH_AARCH64 1" in contents
    is_x86_64 = "#define ARCH_X86_64 1" in contents
    if is_arm64 == is_x86_64:
        raise ValueError(f"{source}: expected exactly one supported target architecture")
    required = "#define CONFIG_V4L2_M2M 1" if is_arm64 else "#define HAVE_VAAPI_DRM 1"
    if required not in contents:
        raise ValueError(f"{source}: missing {required}")

    backend = "v4l2-m2m" if is_arm64 else "vaapi"
    if is_arm64:
        required_features = (
            "#define HAVE_ARMV8 1",
            "#define HAVE_ARMV8_EXTERNAL 1",
            "#define HAVE_ARMV8_INLINE 1",
            "#define HAVE_NEON 1",
            "#define HAVE_NEON_EXTERNAL 1",
            "#define HAVE_NEON_INLINE 1",
        )
        for feature in required_features:
            if feature not in contents:
                raise ValueError(f"{source}: missing {feature}")
        # AOSP Soong invokes Clang's integrated assembler, which does not
        # implement GNU as's .func/.endfunc directives used by asm.S.
        contents = re.sub(
            r'^#define HAVE_AS_FUNC [01]$',
            '#define HAVE_AS_FUNC 0',
            contents,
            count=1,
            flags=re.MULTILINE,
        )
    contents = re.sub(
        r'^#define FFMPEG_CONFIGURATION ".*"$',
        f'#define FFMPEG_CONFIGURATION "--toolchain=aosp-soong --backend={backend}"',
        contents,
        count=1,
        flags=re.MULTILINE,
    )
    contents = re.sub(
        r'^#define CC_IDENT ".*"$',
        '#define CC_IDENT "AOSP Soong Clang"',
        contents,
        count=1,
        flags=re.MULTILINE,
    )
    return contents


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("sources", nargs="+", type=pathlib.Path)
    args = parser.parse_args()

    outputs = set()
    for source in args.sources:
        relative = output_name(source)
        if relative in outputs:
            raise ValueError(f"duplicate generated output: {relative}")
        outputs.add(relative)
        destination = args.output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.name == "config.h":
            destination.write_text(normalized_config(source), encoding="utf-8")
        else:
            shutil.copyfile(source, destination)


if __name__ == "__main__":
    main()
