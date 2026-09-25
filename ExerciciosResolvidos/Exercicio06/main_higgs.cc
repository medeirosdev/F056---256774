#include "Pythia8/Pythia.h"

#include "TFile.h"
#include "TTree.h"
#include "TLorentzVector.h"

#include <iostream>
#include <string>

using namespace Pythia8;

// uso: ./main_higgs arquivo.cmnd saida.root
int main(int argc, char* argv[]) {

    if (argc < 3) {
        std::cout << "uso: ./main_higgs arquivo.cmnd saida.root" << std::endl;
        return 1;
    }
    std::string cardName = argv[1];
    std::string outName = argv[2];

    Pythia pythia;
    pythia.readFile(cardName);
    int nEvents = pythia.mode("Main:numberOfEvents");

    if (!pythia.init()) {
        std::cout << "erro no init do pythia" << std::endl;
        return 1;
    }

    TFile outFile(outName.c_str(), "RECREATE");
    TTree tree("events", "Eventos");

    // mH  = massa da soma das filhas diretas do Higgs (so tem no sinal, -1 nos bkg)
    // mbb = massa do par b bbar de maior pT no estado final (todos)
    float mH = -1.;
    float mbb = -1.;
    float bPt = 0., bbarPt = 0.;
    float bEta = 0., bbarEta = 0.;

    tree.Branch("mH", &mH, "mH/F");
    tree.Branch("mbb", &mbb, "mbb/F");
    tree.Branch("bPt", &bPt, "bPt/F");
    tree.Branch("bbarPt", &bbarPt, "bbarPt/F");
    tree.Branch("bEta", &bEta, "bEta/F");
    tree.Branch("bbarEta", &bbarEta, "bbarEta/F");

    int nSalvos = 0;

    for (int iEvent = 0; iEvent < nEvents; ++iEvent) {
        if (!pythia.next()) continue;

        Event& event = pythia.event;

        // procura o Higgs (o ultimo da cadeia, que e o que decai)
        int iHiggs = -1;
        for (int i = 0; i < event.size(); ++i) {
            if (event[i].id() == 25) iHiggs = i;
        }

        mH = -1.;
        if (iHiggs >= 0) {
            Vec4 pH(0., 0., 0., 0.);
            int nFilhas = 0;
            for (int i = 0; i < event.size(); ++i) {
                if (event[i].mother1() == iHiggs && abs(event[i].id()) == 5) {
                    pH += event[i].p();
                    nFilhas++;
                }
            }
            if (nFilhas == 2) mH = pH.mCalc();
        }

        TLorentzVector b, bbar;
        double bPtMax = -1., bbarPtMax = -1.;
        for (int i = 0; i < event.size(); ++i) {
            if (!event[i].isFinal()) continue;
            if (event[i].id() == 5 && event[i].pT() > bPtMax) {
                b.SetPxPyPzE(event[i].px(), event[i].py(), event[i].pz(), event[i].e());
                bPtMax = event[i].pT();
            }
            if (event[i].id() == -5 && event[i].pT() > bbarPtMax) {
                bbar.SetPxPyPzE(event[i].px(), event[i].py(), event[i].pz(), event[i].e());
                bbarPtMax = event[i].pT();
            }
        }
        if (bPtMax < 0 || bbarPtMax < 0) continue;

        mbb = (b + bbar).M();
        bPt = b.Pt();
        bbarPt = bbar.Pt();
        bEta = b.Eta();
        bbarEta = bbar.Eta();

        tree.Fill();
        nSalvos++;
    }

    outFile.cd();
    tree.Write();
    outFile.Close();

    pythia.stat();

    std::cout << "card: " << cardName << "  saida: " << outName << std::endl;
    std::cout << "eventos salvos: " << nSalvos << " de " << nEvents << std::endl;
    std::cout << "sigma (pb): " << pythia.info.sigmaGen() * 1e9 << std::endl;

    return 0;
}
