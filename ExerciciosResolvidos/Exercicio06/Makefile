CXX      = g++
CXXFLAGS = -O2 -Wall $(shell pythia8-config --cxxflags) $(shell root-config --cflags)
LDFLAGS  = $(shell pythia8-config --libs) $(shell root-config --libs)

all: main_higgs

main_higgs: main_higgs.cc
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

run: main_higgs
	./main_higgs main_higgs.cmnd higgs_mass.root
	./main_higgs bkg_qcd.cmnd bkg_qcd.root
	./main_higgs bkg_z.cmnd bkg_z.root
	./main_higgs bkg_ttbar.cmnd bkg_ttbar.root

plot:
	root -l -b -q plot_mass.C

clean:
	rm -f main_higgs *.o

.PHONY: all run plot clean
