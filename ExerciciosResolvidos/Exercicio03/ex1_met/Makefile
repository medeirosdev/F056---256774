CXX = g++
CXXFLAGS = -Wall -fPIC -std=c++11

LIB = libSimpleMET.so
TEST = testMET

all: $(TEST)

$(LIB): SimpleMET.o
	$(CXX) -shared -o $(LIB) SimpleMET.o

SimpleMET.o: SimpleMET.cpp SimpleMET.h
	$(CXX) $(CXXFLAGS) -c SimpleMET.cpp -o SimpleMET.o

$(TEST): testMET.cpp $(LIB)
	$(CXX) $(CXXFLAGS) testMET.cpp -L. -lSimpleMET -Wl,-rpath,. -o $(TEST)

clean:
	rm -f *.o $(LIB) $(TEST)

.PHONY: all clean
