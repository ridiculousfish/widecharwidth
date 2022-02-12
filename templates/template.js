/*
 * {filename} for Unicode {unicode_version}
 * See https://github.com/ridiculousfish/widecharwidth/
 *
 * SHA1 file hashes:
 *  (
 *  the hashes for generate.py and the template are git object hashes,
 *  use `git log --all --find-object=<hash>` in the widecharwidth repository
 *  to see which commit they correspond to,
 *  or run `git hash-object` on the file to compare.
 *  The other hashes are simple `sha1sum` style hashes.
 *  )
 *
 *  generate.py:         {generate_hash}
 *  template.js:         {template_hash}
 *  UnicodeData.txt:     {unicode_hash}
 *  EastAsianWidth.txt:  {eaw_hash}
 *  emoji-data.txt:      {emoji_hash}
 */

/* Special width values */
const {p}nonprint = -1;     // The character is not printable.
const {p}combining = -2;    // The character is a zero-width combiner.
const {p}ambiguous = -3;    // The character is East-Asian ambiguous width.
const {p}private_use = -4;  // The character is for private use.
const {p}unassigned = -5;   // The character is unassigned.
const {p}widened_in_9 = -6; // Width is 1 in Unicode 8, 2 in Unicode 9+.
const {p}non_character = -7; // The character is a noncharacter.

/* Simple ASCII characters - used a lot, so we check them first. */
const {p}ascii_table = [
    {ascii}
];

/* Private usage range. */
const {p}private_table = [
    {private}
];

/* Nonprinting characters. */
const {p}nonprint_table = [
    {nonprint}
];

/* Width 0 combining marks. */
const {p}combining_table = [
    {combining}
];

/* Width 0 combining letters. */
const {p}combiningletters_table = [
    {combiningletters}
];

/* Width.2 characters. */
const {p}doublewide_table = [
    {doublewide}
];

/* Ambiguous-width characters. */
const {p}ambiguous_table = [
    {ambiguous}
];

/* Unassigned characters. */
const {p}unassigned_table = [
    {unassigned}
];

/* Non-characters. */
const {p}nonchar_table[] = [
    {noncharacters}
];

/* Characters that were widened from width 1 to 2 in Unicode 9. */
const {p}widened_table[] = [
    {widenedin9}
];

function {p}in_table(data, ucs) {{
    let min = 0;
    let max = data.length - 1;
    let mid;
    if (ucs < data[0][0] || ucs > data[max][1])
        return false;

    while (max >= min) {{
        mid = (min + max) >> 1;
        if (ucs > data[mid][1]) {{
            min = mid + 1;
        }}
        else if (ucs < data[mid][0]) {{
            max = mid - 1;
        }}
        else {{
            return true;
        }}
    }}
    return false;
}}

/* Return the width of character c, or a special negative value. */
function {p}wcwidth(c) {{
    if ({p}in_table({p}ascii_table, c))
        return 1;
    if ({p}in_table({p}private_table, c))
        return {p}private_use;
    if ({p}in_table({p}nonprint_table, c))
        return {p}nonprint;
    if ({p}in_table({p}nonchar_table, c))
        return {p}non_character;
    if ({p}in_table({p}combining_table, c))
        return {p}combining;
    if ({p}in_table({p}combiningletters_table, c))
        return {p}combining;
    if ({p}in_table({p}doublewide_table, c))
        return 2;
    if ({p}in_table({p}ambiguous_table, c))
        return {p}ambiguous;
    if ({p}in_table({p}unassigned_table, c))
        return {p}unassigned;
    if ({p}in_table({p}widened_table, c))
        return {p}widened_in_9;
    return 1;
}}
