CXX      = g++
CXXFLAGS = -O2 -Wall -std=c++17 $(shell root-config --cflags)
LDFLAGS  = $(shell root-config --libs)

all: generate plot_and_fit

generate: generate.cpp
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

plot_and_fit: plot_and_fit.cpp
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

clean:
	rm -f generate plot_and_fit *.o

.PHONY: all clean
