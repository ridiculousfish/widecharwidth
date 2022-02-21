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
#  template.js:         {template_hash}
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


# Simple ASCII characters - used a lot, so we check them first.
ascii_table = Codepointrange(
    {ascii}
)

# Private usage range.
private_table = Codepointrange(
    {private}
)

# Nonprinting characters.
nonprint_table = Codepointrange(
    {nonprint}
)

# Width 0 combining marks.
combining_table = Codepointrange(
    {combining}
)

# Width 0 combining letters.
combiningletters_table = Codepointrange(
    {combiningletters}
)

# Width.2 characters.
doublewide_table = Codepointrange(
    {doublewide}
)

# Ambiguous-width characters.
ambiguous_table = Codepointrange(
    {ambiguous}
)

# Unassigned characters.
unassigned_table = Codepointrange(
    {unassigned}
)

# Non-characters.
nonchar_table = Codepointrange(
    {noncharacters}
)

# Characters that were widened from width 1 to 2 in Unicode 9.
widened_table = Codepointrange(
    {widenedin9}
)


# Return the width of character c, or a special negative value.
def wcwidth(c: Union[str, int]) -> Union[int, Special]:
    if isinstance(c, str):
        try:
            c = ord(c)
        except:
            raise ValueError("Argument must be a codepoint as a string or int")
    elif c > 0x10FFFF:
        raise ValueError("Argument is too big for Unicode")

    if c in ascii_table:
        return 1
    if c in private_table:
        return Special.private_use
    if c in nonprint_table:
        return Special.nonprint
    if c in nonchar_table:
        return Special.non_character
    if c in combining_table:
        return Special.combining
    if c in combiningletters_table:
        return Special.combining
    if c in doublewide_table:
        return 2
    if c in ambiguous_table:
        return Special.ambiguous
    if c in unassigned_table:
        return Special.unassigned
    if c in widened_table:
        return Special.widened_in_9
    return 1
