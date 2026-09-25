#include <TFile.h>
#include <TTree.h>
#include <TH1F.h>
#include <TF1.h>
#include <TCanvas.h>
#include <iostream>

int main() {
    TFile *file = new TFile("dados.root", "READ");
    if (file->IsZombie()) {
        std::cout << "nao achou dados.root, roda o ./generate antes" << std::endl;
        return 1;
    }
    TTree *tree = (TTree*)file->Get("tree");

    double x;
    tree->SetBranchAddress("x", &x);

    TH1F *h = new TH1F("h", "dist. gerada;Valor gerado;num de entradas", 50, -5, 5);
    h->SetDirectory(0);

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

    h->Fit("gaus");
    h->Draw();

    TF1 *fit = h->GetFunction("gaus");
    double fitMean = fit->GetParameter(1);
    double fitSigma = fit->GetParameter(2);
    std::cout << "media do ajuste: " << fitMean << std::endl;
    std::cout << "sigma do ajuste: " << fitSigma << std::endl;

    c->SaveAs("fit_cpp.png");

    file->Close();
    return 0;
}
