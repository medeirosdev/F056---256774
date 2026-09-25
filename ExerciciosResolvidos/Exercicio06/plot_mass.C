#include <TFile.h>
#include <TTree.h>
#include <TH1F.h>
#include <TCanvas.h>
#include <TLegend.h>
#include <TStyle.h>

void plot_mass() {
    gStyle->SetOptStat(0);

    const char* arquivos[4] = {"higgs_mass.root", "bkg_qcd.root", "bkg_z.root", "bkg_ttbar.root"};
    const char* nomes[4] = {"sinal gg #rightarrow H #rightarrow b#bar{b}", "QCD b#bar{b}", "Z #rightarrow b#bar{b}", "t#bar{t}"};
    int cores[4] = {kRed, kBlue, kGreen+2, kMagenta};

    TH1F* h[4];
    TCanvas* c = new TCanvas("c", "massa bb", 800, 600);
    c->SetFillColor(kWhite);
    TLegend* leg = new TLegend(0.6, 0.65, 0.88, 0.88);

    for (int i = 0; i < 4; i++) {
        TFile* f = TFile::Open(arquivos[i]);
        TTree* t = (TTree*)f->Get("events");

        h[i] = new TH1F(Form("h%d", i), "Massa invariante do par b#bar{b};m_{b#bar{b}} [GeV];Eventos normalizados", 50, 0, 250);
        t->Draw(Form("mbb >> h%d", i), "", "goff");
        h[i]->SetDirectory(0);
        h[i]->Scale(1.0 / h[i]->Integral());

        h[i]->SetLineColor(cores[i]);
        h[i]->SetLineWidth(2);
        leg->AddEntry(h[i], nomes[i], "l");
        f->Close();
    }

    h[0]->SetMaximum(0.3);
    h[0]->Draw("hist");
    for (int i = 1; i < 4; i++) h[i]->Draw("hist same");
    leg->Draw();

    c->SaveAs("massa_sinal_bkg.png");

    TFile* fs = TFile::Open("higgs_mass.root");
    TTree* ts = (TTree*)fs->Get("events");
    TCanvas* c2 = new TCanvas("c2", "mH", 800, 600);
    TH1F* hH = new TH1F("hH", "Massa das filhas diretas do Higgs;m_{H} [GeV];Eventos", 100, 124, 126);
    ts->Draw("mH >> hH", "mH > 0");
    hH->SetLineColor(kBlack);
    hH->SetFillColor(kYellow);
    c2->SaveAs("massa_higgs.png");
}
