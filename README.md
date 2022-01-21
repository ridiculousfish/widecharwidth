widecharwidth is a Python script that outputs implementations of `wcwidth()`, by downloading and parsing the latest `UnicodeData.txt`, `EastAsianWidth.txt`, and `emoji-data.txt`. Currently it generates C++, JavaScript, and Rust code.

## C++ Usage

You may directly copy and use the included `widechar_width.h`.

This header contains a single public function `widechar_wcwidth()`. This returns either a positive width value (1 or 2), or a negative value such as `widechar_private_use`. Note that there are several possible negative return values, to distinguish among different scenarios.

If you aren't sure how to handle negative return values, try this table:

 | return value            | width |
 |-------------------------|---|
 | `widechar_nonprint`     | 0 |
 | `widechar_combining`    | 0 |
 | `widechar_ambiguous`    | 1 |
 | `widechar_private_use`  | 1 |
 | `widechar_unassigned`   | 0 |
 | `widechar_non_character`| 0 |
 | `widechar_widened_in_9` | 2 (or maybe 1, renderer dependent) |

## JavaScript usage

The JS file `widechar_width.js` contains the function `widechar_wcwidth()`. This behaves the same as the C++ version.

## Rust usage

In Rust, use `widechar_width.rs` and match `WcWidth::from_char()`. Example:

```rust
match WcWidth::from_char(c) {
    WcWidth::One | WcWidth::Two => (), // width 1 or 2
    WcWidth::Combining => (),          // zero-width combiner
    WcWidth::NonPrint => (),           // non-printing
    ...
}
```

## Regenerating the sources

To regenerate the generated sources, run `make`. This will download and parse the relevant files, and run tests.

## License

widecharwidth and its output files are released into the public domain. They may be used for any purpose without requiring attribution, or under the CC0 license if public domain is not available. See included LICENSE.

## Limitations

widecharwidth tries to give a width according to [Unicode Standard Annex #11](http://www.unicode.org/reports/tr11/). However, as that mentions:

> Note: The East_Asian_Width property is not intended for use by modern terminal emulators without appropriate tailoring on a case-by-case basis. Such terminal emulators need a way to resolve the halfwidth/fullwidth dichotomy that is necessary for such environments, but the East_Asian_Width property does not provide an off-the-shelf solution for all situations. The growing repertoire of the Unicode Standard has long exceeded the bounds of East Asian legacy character encodings, and terminal emulations often need to be customized to support edge cases and for changes in typographical behavior over time.

So, unfortunately, we are forced to make some decisions. widecharwidth tries to find a sensible interpretation that has wide compatibility across up-to-date terminals.

In addition, a wcwidth-style per-codepoint API is fundamentally limited when it comes to composing codepoints. You *can't*, in general, decide the width of a codepoint in isolation. widecharwidth tries to solve some simple cases, and terminals having typically incomplete unicode support make this tenable.

One example where special interpretation is necessary are korean Hangul. In Unicode, a Hangul syllable are also available in a decomposed form consisting of multiple codepoints - a leading consonant, a vowel and a trailing consonant. widecharwidth, like [glibc](https://sourceware.org/bugzilla/show_bug.cgi?id=22074) assigns the latter two a width of 0. This results in the total width for a complete syllable adding up to the correct value, but if e.g. a vowel ever appeared in isolation it would be deemed to have a width of 0.

In addition some renderers have differing ideas of the width. If that is the case for you, you might want to override widecharwidth for specific codepoints.

For example, in C++:

```c++
    // We render U+1F6E1 (🛡) with a width of 2,
    // but widechar_width says it has a width of 1 because Unicode classifies it as "neutral".
    //
    // So we simply decide the width ourselves
    if (wc >= 0x1F6E1) return 2;

    int width = widechar_wcwidth(wc);

    switch (width) {
        // Some sensible defaults
        case widechar_nonprint:
        case widechar_combining:
        case widechar_unassigned:
        case widechar_non_character:
            return 0;
        case widechar_ambiguous:
        case widechar_private_use:
            return 1;
        case widechar_widened_in_9:
            // Our renderer supports Unicode 9
            return 2;
        default:
            // Use the width widechar_width gave us.
            return width;
    }
```
