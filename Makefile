test: tester_cpp tester_c rust
	./tester_cpp
	./tester_c

widechar_width.h widechar_width_c.h widechar_width.js widechar_width.rs widechar_width.py widechar_width.java: generate.py
	./generate.py

wcwidth9.h:
	@echo "Tests require original wcwidth9.h from https://github.com/joshuarubin/wcwidth9"
	wget https://raw.githubusercontent.com/joshuarubin/wcwidth9/master/wcwidth9.h

rust: widechar_width.rs
	rustfmt widechar_width.rs
	rustc widechar_width.rs --crate-type lib --test
	./widechar_width

tester_cpp: test.cpp widechar_width.h | wcwidth9.h
	clang++ -std=c++11 test.cpp -o $@

tester_c: test.c widechar_width.h | wcwidth9.h
	clang test.c -o $@

clean:
	rm -f UnicodeData.txt emoji-data.txt EastAsianWidth.txt widechar_width.h widechar_width_c.h widechar_width.js widechar_width.rs widechar_width.py widechar_width.java tester
