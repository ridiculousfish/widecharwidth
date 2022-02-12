/**
 * {filename}
 * See https://github.com/ridiculousfish/widecharwidth/
 *
 * SHA1 file hashes:
 *  generate.py:         {generate_hash}
 *  template.rs:         {template_hash}
 *  UnicodeData.txt:     {unicode_hash}
 *  EastAsianWidth.txt:  {eaw_hash}
 *  emoji-data.txt:      {emoji_hash}
 */

type R = (u32, u32);

#[derive(Copy, Clone, Debug, Eq, PartialEq)]
pub enum WcWidth {{
  /// The character is single-width
  One,
  /// The character is double-width
  Two,
  /// The character is not printable.
  NonPrint,
  /// The character is a zero-width combiner.
  Combining,
  /// The character is East-Asian ambiguous width.
  Ambiguous,
  /// The character is for private use.
  PrivateUse,
  /// The character is unassigned.
  Unassigned,
  /// Width is 1 in Unicode 8, 2 in Unicode 9+.
  WidenedIn9,
  /// The character is a noncharacter.
  NonCharacter,
}}

/// Simple ASCII characters - used a lot, so we check them first.
const ASCII_TABLE: &'static [R] = &[
    {ascii}
];

/// Private usage range.
const PRIVATE_TABLE: &'static [R] = &[
    {private}
];

/// Nonprinting characters.
const NONPRINT_TABLE: &'static [R] = &[
    {nonprint}
];

/// Width 0 combining marks.
const COMBINING_TABLE: &'static [R] = &[
    {combining}
];

/// Width 0 combining letters.
const COMBININGLETTERS_TABLE: &'static [R] = &[
    {combiningletters}
];

/// Width 2 characters.
const DOUBLEWIDE_TABLE: &'static [R] = &[
    {doublewide}
];

/// Ambiguous-width characters.
const AMBIGUOUS_TABLE: &'static [R] = &[
    {ambiguous}
];

/// Unassigned characters.
const UNASSIGNED_TABLE: &'static [R] = &[
    {unassigned}
];

/// Non-characters.
const NONCHAR_TABLE: &'static [R] = &[
    {noncharacters}
];

/// Characters that were widened from width 1 to 2 in Unicode 9.
const WIDENED_TABLE: &'static [R] = &[
    {widenedin9}
];

fn in_table(arr: &[R], c: u32) -> bool {{
    arr.binary_search_by(|(start, end)| if c >= *start && c <= *end {{
        std::cmp::Ordering::Equal
    }} else {{
        start.cmp(&c)
    }}).is_ok()
}}

impl WcWidth {{
    /// Return the width of character c
    pub fn from_char(c: char) -> Self {{
        let c = c as u32;
        if in_table(&ASCII_TABLE, c) {{
            return Self::One;
        }}
        if in_table(&PRIVATE_TABLE, c) {{
            return Self::PrivateUse;
        }}
        if in_table(&NONPRINT_TABLE, c) {{
            return Self::NonPrint;
        }}
        if in_table(&NONCHAR_TABLE, c) {{
            return Self::NonCharacter;
        }}
        if in_table(&COMBINING_TABLE, c) {{
            return Self::Combining;
        }}
        if in_table(&COMBININGLETTERS_TABLE, c) {{
            return Self::Combining;
        }}
        if in_table(&DOUBLEWIDE_TABLE, c) {{
            return Self::Two;
        }}
        if in_table(&AMBIGUOUS_TABLE, c) {{
            return Self::Ambiguous;
        }}
        if in_table(&UNASSIGNED_TABLE, c) {{
            return Self::Unassigned;
        }}
        if in_table(&WIDENED_TABLE, c) {{
            return Self::WidenedIn9;
        }}
        Self::One
    }}

    /// Returns width for applications that are using unicode 8 or earlier
    pub fn width_unicode_8_or_earlier(self) -> u8 {{
        match self {{
            Self::One => 1,
            Self::Two => 2,
            Self::NonPrint | Self::Combining | Self::Unassigned | Self::NonCharacter => 0,
            Self::Ambiguous | Self::PrivateUse => 1,
            Self::WidenedIn9 => 1,
        }}
    }}

    /// Returns width for applications that are using unicode 9 or later
    pub fn width_unicode_9_or_later(self) -> u8 {{
        if self == Self::WidenedIn9 {{
            return 2;
        }}
        self.width_unicode_8_or_earlier()
    }}
}}

#[cfg(test)]
mod test {{
    use super::*;

    #[test]
    fn basics() {{
        assert_eq!(WcWidth::from_char('w'), WcWidth::One);
        assert_eq!(WcWidth::from_char('\x1f'), WcWidth::NonPrint);
        assert_eq!(WcWidth::from_char('\u{{e001}}'), WcWidth::PrivateUse);
        assert_eq!(WcWidth::from_char('\u{{2716}}'), WcWidth::One);
        assert_eq!(WcWidth::from_char('\u{{270a}}'), WcWidth::WidenedIn9);
        assert_eq!(WcWidth::from_char('\u{{3fffd}}'), WcWidth::Two);
    }}
}}
