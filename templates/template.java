import java.util.stream.Stream;

import static java.lang.String.format;

/**
 * {filename} for Unicode {unicode_version}
 * See <a href="https://github.com/ridiculousfish/widecharwidth/">https://github.com/ridiculousfish/widecharwidth/</a>
 *
 * <p>SHA1 file hashes:
 * (
 * the hashes for generate.py and the template are git object hashes,
 * use `git log --all --find-object=hash` in the widecharwidth repository
 * to see which commit they correspond to,
 * or run `git hash-object` on the file to compare.
 * The other hashes are simple `sha1sum` style hashes.
 * )
 *
 * <ul>
 * <li>generate.py:         {generate_hash}</li>
 * <li>template.java:       {template_hash}</li>
 * <li>UnicodeData.txt:     {unicode_hash}</li>
 * <li>EastAsianWidth.txt:  {eaw_hash}</li>
 * <li>emoji-data.txt:      {emoji_hash}</li>
 * </ul>
 */
public class WcWidth {{

    private WcWidth() {{
    }}

    public enum Type {{
        ONE(1, ASCII_TABLE),                                    // The character is single-width
        PRIVATE_USE(1, PRIVATE_TABLE),                          // The character is for private use.
        NON_PRINT(0, NON_PRINT_TABLE),                          // The character is not printable
        NON_CHARACTER(0, NON_CHARACTER_TABLE),                  // The character is a non-character.
        COMBINING(0, COMBINING_TABLE, COMBINING_LETTERS_TABLE), // The character is a zero-width combiner
        TWO(2, DOUBLE_WIDE_TABLE),                              // The character is double-width
        AMBIGUOUS(1, AMBIGUOUS_TABLE),                          // The character is East-Asian ambiguous width.
        UNASSIGNED(0, UNASSIGNED_TABLE),                        // The character is unassigned.
        WIDENED_IN_9(2, WIDENED_IN_9_TABLE);                    // Width is 1 in Unicode 8, 2 in Unicode 9+.

        private final int defaultWidth;
        private final int[][][] tables;

        Type(int defaultWidth, int[][]... tables) {{
            this.defaultWidth = defaultWidth;
            this.tables = tables;
        }}

        public int defaultWidth() {{
            return defaultWidth;
        }}

        private boolean contains(int c) {{
            return Stream.of(tables).anyMatch(table -> contains(c, table));
        }}

        private boolean contains(int c, int[][] table) {{
            var min = 0;
            var max = table.length - 1;

            if (c < table[0][0] || c > table[max][1]) {{
                return false;
            }}

            while (max >= min) {{
                var mid = (min + max) / 2;

                if (c > table[mid][1]) {{
                    min = mid + 1;
                }} else if (c < table[mid][0]) {{
                    max = mid - 1;
                }} else {{
                    return true;
                }}
            }}

            return false;
        }}

        public static Type of(int c) {{
            if (c < 0 || c > 0x10FFFF) {{
                throw new IllegalArgumentException(format("'0x%X' is not a Unicode code point", c))
            }}

            return Stream.of(Type.values())
                    .filter(type -> type.contains(c))
                    .findFirst()
                    .orElse(ONE);
        }}

    }}

    // Simple ASCII characters - used a lot, so we check them first.
    private static final int[][] ASCII_TABLE = {{
        {ascii}
    }};

    // Private usage range.
    private static final int[][] PRIVATE_TABLE = {{
        {private}
    }};

    // Nonprinting characters.
    private static final int[][] NON_PRINT_TABLE = {{
        {nonprint}
    }};

    // Width 0 combining marks.
    private static final int[][] COMBINING_TABLE = {{
        {combining}
    }};

    // Width 0 combining letters.
    private static final int[][] COMBINING_LETTERS_TABLE = {{
        {combiningletters}
    }};

    // Width 2 characters.
    private static final int[][] DOUBLE_WIDE_TABLE = {{
        {doublewide}
    }};

    // Ambiguous-width characters.
    private static final int[][] AMBIGUOUS_TABLE = {{
        {ambiguous}
    }};

    // Unassigned characters.
    private static final int[][] UNASSIGNED_TABLE = {{
        {unassigned}
    }};

    // Non-characters.
    private static final int[][] NON_CHARACTER_TABLE = {{
        {noncharacters}
    }};

    // Characters that were widened from width 1 to 2 in Unicode 9.
    private static final int[][] WIDENED_IN_9_TABLE = {{
        {widenedin9}
    }};
    
}}
