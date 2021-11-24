test: tester rust
	./tester

widechar_width.h widechar_width.js widechar_width.rs: generate.py
	./generate.py

wcwidth9.h:
	@echo "Tests require original wcwidth9.h from https://github.com/joshuarubin/wcwidth9"
	@false

rust: widechar_width.rs
	rustc widechar_width.rs --crate-type lib --test
	./widechar_width
	
tester: test.cpp widechar_width.h | wcwidth9.h
	clang++ -std=c++11 test.cpp -o tester

clean:
	rm -f UnicodeData.txt emoji-data.txt EastAsianWidth.txt widechar_width.h widechar_width.js tester
