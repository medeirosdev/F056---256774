// desenha pT, eta e m_ttbar do top comparando so qqbar com qqbar + gg
// uso: root -l -b -q plot_ttbar.C
void plot_ttbar() {
    gStyle->SetOptStat(0);

    TFile* fqq = TFile::Open("ttbar_qq.root");
    TFile* ftot = TFile::Open("ttbar_total.root");
    if (!fqq || !ftot) {
        std::cout << "rode antes: make run" << std::endl;
        return;
    }

    const char* nomes[3] = {"hPtTop", "hEtaTop", "hMtt"};

    TCanvas* c = new TCanvas("c", "ttbar", 1500, 500);
    c->Divide(3, 1);

    for (int i = 0; i < 3; ++i) {
        c->cd(i + 1);
        gPad->SetLeftMargin(0.14);
        TH1F* hqq = (TH1F*)fqq->Get(nomes[i]);
        TH1F* htot = (TH1F*)ftot->Get(nomes[i]);

        // normalizo pela area pra comparar so a forma
        hqq->Scale(1. / hqq->Integral());
        htot->Scale(1. / htot->Integral());
        hqq->GetYaxis()->SetTitle("fracao de eventos");

        hqq->SetLineColor(kBlue);
        hqq->SetLineWidth(2);
        htot->SetLineColor(kRed);
        htot->SetLineWidth(2);

        double ymax = std::max(hqq->GetMaximum(), htot->GetMaximum());
        hqq->SetMaximum(1.2 * ymax);
        hqq->Draw("hist");
        htot->Draw("hist same");

        if (i == 0) {
            TLegend* leg = new TLegend(0.45, 0.72, 0.88, 0.88);
            leg->AddEntry(hqq, "q#bar{q} #rightarrow t#bar{t}", "l");
            leg->AddEntry(htot, "q#bar{q} + gg #rightarrow t#bar{t}", "l");
            leg->Draw();
        }
    }

    c->SaveAs("ttbar_distribuicoes.png");
}
