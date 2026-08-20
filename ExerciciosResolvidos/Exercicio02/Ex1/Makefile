CXX = g++
CXXFLAGS = -Wall -O2

all: hello

hello: hello.cpp
	$(CXX) $(CXXFLAGS) -o hello hello.cpp

#limpa
#todo fazer um clean em específico depois

clean:
	rm -f hello output_*.txt

.PHONY: all clean
