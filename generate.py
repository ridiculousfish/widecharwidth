#!/usr/bin/env python3

""" Outputs the width file to stdout. """

import datetime
import hashlib
import os.path
import re
import sys

from collections.abc import Iterable
from typing import NamedTuple
from urllib.request import urlretrieve

VERSION = "15.0.0"
UNICODE_DATA_URL = "https://unicode.org/Public/%s/ucd/UnicodeData.txt" % VERSION
EAW_URL = "https://unicode.org/Public/%s/ucd/EastAsianWidth.txt" % VERSION
EMOJI_DATA_URL = "https://unicode.org/Public/%s/ucd/emoji/emoji-data.txt" % VERSION

# A handful of field names
# See https://www.unicode.org/L2/L1999/UnicodeData.html
FIELD_CODEPOINT = 0
FIELD_NAME = 1
FIELD_CATEGORY = 2

# Category for unassigned codepoints.
CAT_UNASSIGNED = "Cn"

# Category for private use codepoints.
CAT_PRIVATE_USE = "Co"

# Category for surrogates.
CAT_SURROGATE = "Cs"

# Category for non-characters.
# Note this does not appear in UnicodeData.txt.
# See https://www.unicode.org/faq/private_use.html
CAT_NON_CHARACTERS = "non-characters"

# Maximum codepoint value.
MAX_CODEPOINT = 0x10FFFF

CPP_PREFIX = "widechar_"

# Ambiguous East Asian characters
WIDTH_AMBIGUOUS_EASTASIAN = -3

# Width changed from 1 to 2 in Unicode 9.0
WIDTH_WIDENED_IN_9 = -6

# Private use characters.
WIDTH_PRIVATE_USE = -7


class CodePoint(object):  # pylint: disable=too-few-public-methods
    """Represents a single Unicode codepoint"""

    def __init__(self, codepoint):
        self.codepoint = codepoint
        self.width = None
        self.category = CAT_UNASSIGNED

    def hex(self):
        """Return the codepoint as a hex string"""
        return "0x%05X" % self.codepoint


# Settings controlling language output.
class LangSettings(NamedTuple):
    range_chars: str  # open/close characters for ranges, like "{}"
    indentation: str = "    "
    keep_last: bool = False


# Data parsed from unicode.org datafiles.
# Datas are lists of lines, with comment-only lines removed.
# Hashes are sha1 strings.
class UnicodeDatas(NamedTuple):
    unicode_data: list[str]
    unicode_hash: str
    eaw_data: list[str]
    eaw_hash: str
    emoji_data: list[str]
    emoji_hash: str


def log(msg):
    """Logs a string to stderr"""
    sys.stderr.write(str(msg) + "\n")


def read_datafile(url):
    """Download a file from url to name if not already present.
    Return the file as a tuple (lines, sha1)
    lines will have comment-only lines removed, sha1 is a string.
    """
    name = url.rsplit("/", 1)[-1]
    if not os.path.isfile(name):
        log("Downloading " + name)
        urlretrieve(url, name)
    with open(name, "rb") as ofile:
        data = ofile.read()
    hashval = hashlib.sha1(data).hexdigest()
    lines = data.decode("utf-8").split("\n")
    lines = [line for line in lines if not line.startswith("#")]
    return (lines, hashval)


def set_general_categories(unicode_data, cps):
    """Receives lines from UnicodeData.txt,
    and sets general categories for codepoints."""
    for line in unicode_data:
        fields = line.strip().split(";")
        if len(fields) > FIELD_CATEGORY:
            for idx in hexrange_to_range(fields[FIELD_CODEPOINT]):
                cps[idx].category = fields[FIELD_CATEGORY]


def merged_codepoints(cps: Iterable[CodePoint]):
    """return a list of codepoints (start, end) for inclusive ranges"""
    cps = sorted(cps, key=lambda cp: cp.codepoint)
    if not cps:
        return []
    ranges = [(cps[0], cps[0])]
    for cp in cps[1:]:
        last_range = ranges[-1]
        if cp.codepoint == last_range[1].codepoint + 1:
            ranges[-1] = (last_range[0], cp)
            continue
        ranges.append((cp, cp))
    return ranges


def gen_seps(length, indentation, keep_last):
    """Yield separators for a table of given length"""
    table_columns = 1
    for idx in range(1, length + 1):
        if idx == length:
            yield "" if not keep_last else ","
        elif idx % table_columns == 0:
            yield ",\n" + indentation
        else:
            yield ", "


def codepoints_to_carray_str(settings: LangSettings, cps: Iterable[CodePoint]):
    """Given a list of codepoints, return a C array string representing their inclusive ranges."""
    result = ""
    ranges = merged_codepoints(cps)
    seps = gen_seps(len(ranges), settings.indentation, settings.keep_last)
    for (start, end) in ranges:
        result += "%s%s, %s%s%s" % (
            settings.range_chars[0],
            start.hex(),
            end.hex(),
            settings.range_chars[1],
            next(seps),
        )
    return result


def hexrange_to_range(hexrange):
    """Given a string like 1F300..1F320 representing an inclusive range,
    return the range of codepoints.
    If the string is like 1F321, return a range of just that element.
    """
    fields = [int(val, 16) for val in hexrange.split("..")]
    if len(fields) == 1:
        fields += fields
    return range(fields[0], fields[1] + 1)


def parse_eaw_line(eaw_line):
    """Return a list of tuples (codepoint, width) from an EAW line"""
    # Remove hash.
    line = eaw_line.split("#", 1)[0]
    fields = line.strip().split(";")
    if len(fields) != 2:
        return []
    cps, width_type = fields
    # width_types:
    #  A: ambiguous, F: fullwidth, H: halfwidth,
    #  N: neutral, Na: east-asian Narrow
    if width_type == "A":
        width = WIDTH_AMBIGUOUS_EASTASIAN
    elif width_type in ["F", "W"]:
        width = 2
    else:
        width = 1
    return [(cp, width) for cp in hexrange_to_range(cps)]


def set_eaw_widths(eaw_data_lines, cps):
    """Read from EastAsianWidth.txt, set width values on the codepoints"""
    for line in eaw_data_lines:
        for (cp, width) in parse_eaw_line(line):
            cps[cp].width = width
    # Apply the following special cases:
    #  - The unassigned code points in the following blocks default to "W":
    #         CJK Unified Ideographs Extension A: U+3400..U+4DBF
    #         CJK Unified Ideographs:             U+4E00..U+9FFF
    #         CJK Compatibility Ideographs:       U+F900..U+FAFF
    #  - All undesignated code points in Planes 2 and 3, whether inside or
    #      outside of allocated blocks, default to "W":
    #         Plane 2:                            U+20000..U+2FFFD
    #         Plane 3:                            U+30000..U+3FFFD
    wide_ranges = [
        (0x3400, 0x4DBF),
        (0x4E00, 0x9FFF),
        (0xF900, 0xFAFF),
        (0x20000, 0x2FFFD),
        (0x30000, 0x3FFFD),
    ]
    for wr in wide_ranges:
        for cp in range(wr[0], wr[1] + 1):
            if cps[cp].width is None:
                cps[cp].width = 2


def parse_emoji_line(line):
    """Return a list {cp, version} for the line"""
    # Example line: 0023   ; Emoji #  1.1  [1] (#)  number sign
    fields_comment = line.split("#", 1)
    if len(fields_comment) != 2:
        return []
    fields, comment = fields_comment
    cps, prop = fields.split(";")
    prop = prop.strip()
    version = 0.0
    # Some code points are marked "reserved" and do not have a version "NA".
    fmtre = re.search(r"^\s*E\d+\.\d+", comment)
    version = float(fmtre.group(0).strip()[1:]) if fmtre else 0.0
    return [(cp, version, prop) for cp in hexrange_to_range(cps)]


def set_emoji_widths(emoji_data_lines, cps):
    """Read from emoji-data.txt, set codepoint widths"""
    for line in emoji_data_lines:
        for (cp, version, prop) in parse_emoji_line(line):
            # The Regional Indicators are special
            if cp in range(0x1F1E6, 0x1F200):
                continue

            # We only care about emoji *presentation*.
            # Other codepoints should be rendered as text by default,
            # so their EAW width applies.
            if prop == "Emoji_Presentation":
                # If this emoji was introduced before Unicode 9, then it was widened in 9.
                # The version we get here is the *Emoji* version.
                # Before Unicode 11 this was different, Unicode 9 shipped with Emoji 3.0.
                cps[cp].width = 2 if version >= 3.0 else WIDTH_WIDENED_IN_9


def set_hardcoded_ranges(cps):
    """Mark private use and surrogate codepoints"""
    # Private use can be determined awkwardly from UnicodeData.txt,
    # but we just hard-code them.
    # We do not treat "private use high surrogate" as private use
    # so as to match wcwidth9().
    private_ranges = [(0xE000, 0xF8FF), (0xF0000, 0xFFFFD), (0x100000, 0x10FFFD)]
    for (first, last) in private_ranges:
        for idx in range(first, last + 1):
            cps[idx].category = CAT_PRIVATE_USE

    surrogate_ranges = [(0xD800, 0xDBFF), (0xDC00, 0xDFFF)]
    for (first, last) in surrogate_ranges:
        for idx in range(first, last + 1):
            cps[idx].category = CAT_SURROGATE

    # See "noncharacters" discussion at https://www.unicode.org/faq/private_use.html
    # "Last two code points of each of the 16 supplementary planes" and also BMP (plane 0).
    nonchar_ranges = [(0xFDD0, 0xFDEF)]
    for plane in range(0, 16 + 1):
        c = 0x10000 * plane + 0xFFFE
        nonchar_ranges.append((c, c + 1))

    for (first, last) in nonchar_ranges:
        for idx in range(first, last + 1):
            cps[idx].category = CAT_NON_CHARACTERS


def read_datas():
    """Read our three Unicode files, and return a UnicodeDatas."""
    unicode_data, unicode_hash = read_datafile(UNICODE_DATA_URL)
    eaw_data, eaw_hash = read_datafile(EAW_URL)
    emoji_data, emoji_hash = read_datafile(EMOJI_DATA_URL)
    return UnicodeDatas(
        unicode_data, unicode_hash, eaw_data, eaw_hash, emoji_data, emoji_hash
    )


def make_codepoints(datas: UnicodeDatas):
    """Given a UnicodeDatas, return a list of CodePoints."""
    cps = [CodePoint(i) for i in range(MAX_CODEPOINT + 1)]
    set_general_categories(datas.unicode_data, cps)
    set_eaw_widths(datas.eaw_data, cps)
    set_emoji_widths(datas.emoji_data, cps)
    set_hardcoded_ranges(cps)
    return cps


def make_fields(
    datas: UnicodeDatas,
    cps: list[CodePoint],
    settings: LangSettings,
    template_hash: str,
    generate_hash: str,
    filename,
):
    """Return a dictionary of fields, ready to be plugged into a template string."""
    log("Thinking...")

    def categories(cats):
        """Return a carray string of codepoints in any of the given categories."""
        catset = set(cats)
        matches = [cp for cp in cps if cp.category in catset]
        return codepoints_to_carray_str(settings, matches)

    def codepoints_with_width(width):
        """Return a carray string of codepoints with the given width."""
        return codepoints_to_carray_str(
            settings, (cp for cp in cps if cp.width == width)
        )

    # A carray string of ASCII codepoints."
    ascii_codepoints = codepoints_to_carray_str(
        settings, (cp for cp in cps if 0x20 <= cp.codepoint < 0x7F)
    )

    # A decomposed Hangul syllable is a grapheme that consists of up to three
    # code points. The first code point has width 2. The rest consists of
    # Jamo vowels and/or a trailing consonant, both of which have width 1.
    # This means that clients who naïvely sum individual characters'
    # wcwidth(), will compute string widths different from the intended width
    # (2).  Work around this by forcing width 0 for these characters. This
    # matches glibc and others.
    combiningletters = codepoints_to_carray_str(
        settings,
        (
            cp
            for cp in cps
            if (
                (cp.codepoint >= 0x1160 and cp.codepoint <= 0x11FF)
                or (cp.codepoint >= 0xD7B0 and cp.codepoint <= 0xD7FF)
            )
        ),
    )

    fields = {
        "p": CPP_PREFIX,
        "filename": filename,
        "unicode_version": VERSION,
        "generate_hash": generate_hash,
        "template_hash": template_hash,
        "unicode_hash": datas.unicode_hash,
        "eaw_hash": datas.eaw_hash,
        "emoji_hash": datas.emoji_hash,
        "ascii": ascii_codepoints,
        "private": categories([CAT_PRIVATE_USE]),
        "noncharacters": categories([CAT_NON_CHARACTERS]),
        "nonprint": categories(["Cc", "Cf", "Zl", "Zp", CAT_SURROGATE]),
        "combining": categories(["Mn", "Mc", "Me"]),
        "combiningletters": combiningletters,
        "doublewide": codepoints_with_width(2),
        "unassigned": categories([CAT_UNASSIGNED]),
        "ambiguous": codepoints_with_width(WIDTH_AMBIGUOUS_EASTASIAN),
        "widenedin9": codepoints_with_width(WIDTH_WIDENED_IN_9),
    }
    return fields


def gitobjecthash(data):
    """Generate the git object hash of a bit of data
    like `git hash-object`
    """
    h = hashlib.sha1()
    h.update(b"blob %u\0" % len(data))
    h.update(data)
    return h.hexdigest()


if __name__ == "__main__":
    with open(__file__, "rb") as oof:
        data = oof.read()
    generate_hash = gitobjecthash(data)
    datas = read_datas()
    cps = make_codepoints(datas)
    langs = {
        # Suffix: Braces, indentation, keep the last comma
        ".h": ("{}",),
        ".js": ("[]",),
        ".py": ("()", "    " * 2, True),
        ".rs": ("()",),
        ".java": ("{}", "    " * 2),
    }
    for suffix, settings in langs.items():
        with open("templates/template" + suffix) as templatefile:
            template = templatefile.read()
            template_hash = gitobjecthash(template.encode("utf-8"))
            output = "widechar_width" + suffix
            fields = make_fields(
                datas,
                cps,
                LangSettings(*settings),
                template_hash,
                generate_hash,
                output,
            )
            with open(output, "w") as fd:
                fd.write(template.strip().format(**fields))
                fd.write("\n")
                log("Output " + output)
