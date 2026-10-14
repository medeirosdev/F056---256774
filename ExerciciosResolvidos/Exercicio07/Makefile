CXX      = g++
CXXFLAGS = -O2 -Wall $(shell pythia8-config --cxxflags) $(shell root-config --cflags)
LDFLAGS  = $(shell pythia8-config --libs) $(shell root-config --libs)

all: ttbar_pythia

ttbar_pythia: ttbar_pythia.cc
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

run: ttbar_pythia
	./ttbar_pythia qq | tee pythia_qq.log
	./ttbar_pythia total | tee pythia_total.log

plot:
	root -l -b -q plot_ttbar.C

clean:
	rm -f ttbar_pythia *.o

.PHONY: all run plot clean
