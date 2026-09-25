#include <TFile.h>
#include <TTree.h>
#include <TRandom3.h>
#include <iostream>

int main() {
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

    std::cout << "gerou " << N << " numeros em dados.root" << std::endl;
    return 0;
}
