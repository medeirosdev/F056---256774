#include <TFile.h>
#include <TTree.h>
#include <TH1F.h>
#include <TF1.h>
#include <TCanvas.h>
#include <iostream>

void plot() {
    TFile *file = new TFile("dados.root", "READ");
    TTree *tree = (TTree*)file->Get("tree");

    double x;
    tree->SetBranchAddress("x", &x);

    TH1F *h = new TH1F("h", "dist. gerada;Valor gerado;num de entradas", 50, -5, 5);

    Long64_t nentries = tree->GetEntries();
    for (Long64_t i = 0; i < nentries; i++) {
        tree->GetEntry(i);
        h->Fill(x);
    }
    h->SetLineColor(kBlack);
    h->SetLineStyle(1);
    h->SetLineWidth(3);
    h->SetFillColor(kYellow);

    TCanvas *c = new TCanvas("c", "hist", 800, 600);
    c->SetFillColor(kWhite);

    h->Fit("gausss");
    h->Draw();

    TF1 *fit = h->GetFunction("gaus");
    double fitMean = fit->GetParameter(1);
    double fitSigma = fit->GetParameter(2);
    std::cout << "media do ajustes: " << fitMean << std::endl;
    std::cout << "sigma do ajuste: " << fitSigma << std::endl;

    c->SaveAs("histogram.png");

    file->Close();
}
