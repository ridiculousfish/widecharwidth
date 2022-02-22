# {filename} for Unicode {unicode_version}
# See https://github.com/ridiculousfish/widecharwidth/
#
# SHA1 file hashes:
#  (
#  the hashes for generate.py and the template are git object hashes,
#  use `git log --all --find-object=<hash>` in the widecharwidth repository
#  to see which commit they correspond to,
#  or run `git hash-object` on the file to compare.
#  The other hashes are simple `sha1sum` style hashes.
#  )
#
#  generate.py:         {generate_hash}
#  template.py:         {template_hash}
#  UnicodeData.txt:     {unicode_hash}
#  EastAsianWidth.txt:  {eaw_hash}
#  emoji-data.txt:      {emoji_hash}

from typing import Union
from enum import IntEnum

# Special width values
class Special(IntEnum):
    nonprint = -1  # The character is not printable.
    combining = -2  # The character is a zero-width combiner.
    ambiguous = -3  # The character is East-Asian ambiguous width.
    private_use = -4  # The character is for private use.
    unassigned = -5  # The character is unassigned.
    widened_in_9 = -6  # Width is 1 in Unicode 8, 2 in Unicode 9+.
    non_character = -7  # The character is a noncharacter.


class Codepointrange:
    def __init__(self, *ranges):
        self.ranges = sorted(ranges)

    def __contains__(self, char):
        left = 0
        right = len(self.ranges) - 1
        if char < self.ranges[0][0] or char > self.ranges[right][1]:
            return False

        while right >= left:
            middle = (left + right) // 2

            if char < self.ranges[middle][0]:
                right = middle - 1
            elif char > self.ranges[middle][1]:
                left = middle + 1
            else:
                return True
        return False


_TABLE = {{
    # Simple ASCII characters - used a lot, so we check them first.
    "ascii": Codepointrange(
        {ascii}
    ),
    # Private usage range.
    "private": Codepointrange(
        {private}
    ),
    # Nonprinting characters.
    "nonprint": Codepointrange(
        {nonprint}
    ),
    # Width 0 combining marks.
    "combining": Codepointrange(
        {combining}
    ),
    # Width 0 combining letters.
    "combiningletters": Codepointrange(
        {combiningletters}
    ),
    # Width 2 characters.
    "doublewide": Codepointrange(
        {doublewide}
    ),
    # Ambiguous-width characters.
    "ambiguous": Codepointrange(
        {ambiguous}
    ),
    # Unassigned characters.
    "unassigned": Codepointrange(
        {unassigned}
    ),
    # Non-characters.
    "nonchar": Codepointrange(
        {noncharacters}
    ),
    # Characters that were widened from width 1 to 2 in Unicode 9.
    "widened": Codepointrange(
        {widenedin9}
    ),
}}


# Return the width of character c, or a special negative value.
def wcwidth(c: Union[str, int]) -> Union[int, Special]:
    if isinstance(c, str):
        try:
            c = ord(c)
        except:
            raise ValueError("Argument must be a codepoint as a string or int")
    elif c > 0x10FFFF:
        raise ValueError("Argument is too big for Unicode")

    if c in _TABLE["ascii"]:
        return 1
    if c in _TABLE["private"]:
        return Special.private_use
    if c in _TABLE["nonprint"]:
        return Special.nonprint
    if c in _TABLE["nonchar"]:
        return Special.non_character
    if c in _TABLE["combining"]:
        return Special.combining
    if c in _TABLE["combiningletters"]:
        return Special.combining
    if c in _TABLE["doublewide"]:
        return 2
    if c in _TABLE["ambiguous"]:
        return Special.ambiguous
    if c in _TABLE["unassigned"]:
        return Special.unassigned
    if c in _TABLE["widened"]:
        return Special.widened_in_9
    return 1
