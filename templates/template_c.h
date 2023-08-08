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

#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#ifndef {p}ARRAY_SIZE
#define {p}ARRAY_SIZE(array) (sizeof(array) / sizeof(array[0]))
#endif

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

static inline bool widechar_in_table(const struct {p}range* arr, size_t len, uint32_t c) {{

    int lo=0;
    int hi=len;

    if(c < arr[0].lo) return(0);
    if(c > arr[len-1].hi) return(0);

    while(1) {{
        int mid = ((hi-lo)/2)+lo;
        if( (c >= arr[mid].lo) && (c <= arr[mid].hi)) {{
            return(1);
        }}
        if(mid == lo) return(0);

        if (c < arr[mid].lo) {{
            hi = mid;
        }} else {{
            lo = mid;
        }}
    }}
    return(0);
}}



/* Return the width of character c, or a special negative value. */
int {p}wcwidth(uint32_t c) {{
    if ({p}in_table({p}ascii_table, {p}ARRAY_SIZE({p}ascii_table), c))
        return 1;
    if ({p}in_table({p}private_table, {p}ARRAY_SIZE({p}private_table), c))
        return {p}private_use;
    if ({p}in_table({p}nonprint_table, {p}ARRAY_SIZE({p}nonprint_table), c))
        return {p}nonprint;
    if ({p}in_table({p}nonchar_table, {p}ARRAY_SIZE({p}nonchar_table), c))
        return {p}non_character;
    if ({p}in_table({p}combining_table, {p}ARRAY_SIZE({p}combining_table), c))
        return {p}combining;
    if ({p}in_table({p}combiningletters_table, {p}ARRAY_SIZE({p}combiningletters_table), c))
        return {p}combining;
    if ({p}in_table({p}doublewide_table, {p}ARRAY_SIZE({p}doublewide_table), c))
        return 2;
    if ({p}in_table({p}ambiguous_table, {p}ARRAY_SIZE({p}ambiguous_table), c))
        return {p}ambiguous;
    if ({p}in_table({p}unassigned_table, {p}ARRAY_SIZE({p}unassigned_table), c))
        return {p}unassigned;
    if ({p}in_table({p}widened_table, {p}ARRAY_SIZE({p}widened_table), c))
        return {p}widened_in_9;
    return 1;
}}

#endif // WIDECHAR_WIDTH_H
