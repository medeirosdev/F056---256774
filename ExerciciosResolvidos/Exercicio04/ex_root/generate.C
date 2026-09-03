#include <TFile.h>
#include <TTree.h>
#include <TRandom3.h>

void generate() {
    const int N = 1000;
    double mean = 0.0;
    double sigma = 1.0;

    TFile *file = new TFile("dados.root", "RECREATE");
    TTree *tree = new TTree("tree", "Num aleat gaussianos");

    double x;
    tree->Branch("x", &x, "x/D");
    TRandom3 rnd(0);
    for (int i = 0; i < N; i++) {
        x = rnd.Gaus(mean, sigma);
        tree->Fill();
    }

    file->cd();
    tree->Write();
    file->Close();
}
