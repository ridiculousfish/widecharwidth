/**
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

#ifndef WIDECHAR_WIDTH_H
#define WIDECHAR_WIDTH_H

#include <algorithm>
#include <iterator>
#include <cstddef>
#include <cstdint>

namespace {{

/* Special width values */
enum {{
  {p}nonprint = -1,     // The character is not printable.
  {p}combining = -2,    // The character is a zero-width combiner.
  {p}ambiguous = -3,    // The character is East-Asian ambiguous width.
  {p}private_use = -4,  // The character is for private use.
  {p}unassigned = -5,   // The character is unassigned.
  {p}widened_in_9 = -6, // Width is 1 in Unicode 8, 2 in Unicode 9+.
  {p}non_character = -7 // The character is a noncharacter.
}};

/* An inclusive range of characters. */
struct {p}range {{
  uint32_t lo;
  uint32_t hi;
}};

/* Simple ASCII characters - used a lot, so we check them first. */
static const struct {p}range {p}ascii_table[] = {{
    {ascii}
}};

/* Private usage range. */
static const struct {p}range {p}private_table[] = {{
    {private}
}};

/* Nonprinting characters. */
static const struct {p}range {p}nonprint_table[] = {{
    {nonprint}
}};

/* Width 0 combining marks. */
static const struct {p}range {p}combining_table[] = {{
    {combining}
}};

/* Width 0 combining letters. */
static const struct {p}range {p}combiningletters_table[] = {{
    {combiningletters}
}};

/* Width 2 characters. */
static const struct {p}range {p}doublewide_table[] = {{
    {doublewide}
}};

/* Ambiguous-width characters. */
static const struct {p}range {p}ambiguous_table[] = {{
    {ambiguous}
}};

/* Unassigned characters. */
static const struct {p}range {p}unassigned_table[] = {{
    {unassigned}
}};

/* Non-characters. */
static const struct {p}range {p}nonchar_table[] = {{
    {noncharacters}
}};

/* Characters that were widened from width 1 to 2 in Unicode 9. */
static const struct {p}range {p}widened_table[] = {{
    {widenedin9}
}};

template<typename Collection>
bool {p}in_table(const Collection &arr, uint32_t c) {{
    auto where = std::lower_bound(std::begin(arr), std::end(arr), c,
        []({p}range p, uint32_t c) {{ return p.hi < c; }});
    return where != std::end(arr) && where->lo <= c;
}}

/* Return the width of character c, or a special negative value. */
int {p}wcwidth(uint32_t c) {{
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

}} // namespace
#endif // WIDECHAR_WIDTH_H
