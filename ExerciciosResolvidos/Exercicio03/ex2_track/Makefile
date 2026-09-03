CXX = g++
CXXFLAGS = -Wall -fPIC -std=c++11

TEST = testTrack

all: $(TEST)

libTrack.so: Track.o
	$(CXX) -shared -o libTrack.so Track.o

Track.o: Track.cpp Track.h
	$(CXX) $(CXXFLAGS) -c Track.cpp -o Track.o

libSimTrack.so: SimTrack.o libTrack.so
	$(CXX) -shared -o libSimTrack.so SimTrack.o -L. -lTrack

SimTrack.o: SimTrack.cpp SimTrack.h Track.h
	$(CXX) $(CXXFLAGS) -c SimTrack.cpp -o SimTrack.o

$(TEST): testTrack.cpp libSimTrack.so libTrack.so
	$(CXX) $(CXXFLAGS) testTrack.cpp -L. -lSimTrack -lTrack -Wl,-rpath,. -o $(TEST)

clean:
	rm -f *.o libTrack.so libSimTrack.so $(TEST)

.PHONY: all clean
