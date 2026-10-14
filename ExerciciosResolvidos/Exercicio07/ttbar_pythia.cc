#include "Pythia8/Pythia.h"

#include "TFile.h"
#include "TH1F.h"

#include <iostream>
#include <string>

using namespace Pythia8;

// uso: ./ttbar_pythia qq        -> so q qbar -> t tbar (o que o enunciado pede)
//      ./ttbar_pythia total     -> q qbar + g g -> t tbar (pra comparar com o MadGraph)
//      ./ttbar_pythia total 100000   -> mesma coisa com outro numero de eventos
int main(int argc, char* argv[]) {

    std::string modo = "qq";
    if (argc > 1) modo = argv[1];
    int nEvents = 10000;
    if (argc > 2) nEvents = std::stoi(argv[2]);
    if (modo != "qq" && modo != "total") {
        std::cout << "uso: ./ttbar_pythia [qq|total]" << std::endl;
        return 1;
    }

    Pythia pythia;

    // Configuracao do feixe
    pythia.readString("Beams:idA = 2212");
    pythia.readString("Beams:idB = 2212");
    pythia.readString("Beams:eCM = 13000.");

    // q qbar -> t tbar
    pythia.readString("Top:qqbar2ttbar = on");
    // g g -> t tbar (dominante no LHC)
    if (modo == "total") pythia.readString("Top:gg2ttbar = on");

    // fixo a semente pra poder reproduzir
    pythia.readString("Random:setSeed = on");
    pythia.readString("Random:seed = 12345");
    pythia.readString("Next:numberCount = 2000");

    // Inicializacao
    if (!pythia.init()) {
        std::cout << "erro no init do pythia" << std::endl;
        return 1;
    }

    // histogramas (parte opcional)
    std::string outName = "ttbar_" + modo + ".root";
    if (nEvents != 10000) outName = "ttbar_" + modo + "_" + std::to_string(nEvents) + ".root";
    TFile outFile(outName.c_str(), "RECREATE");
    TH1F hPtTop("hPtTop", "p_{T} do top;p_{T} [GeV];eventos", 50, 0., 500.);
    TH1F hEtaTop("hEtaTop", "#eta do top;#eta;eventos", 50, -5., 5.);
    TH1F hMtt("hMtt", "massa invariante t#bar{t};m_{t#bar{t}} [GeV];eventos", 60, 300., 1500.);

    int nAceitos = 0;
    for (int iEvent = 0; iEvent < nEvents; ++iEvent) {
        if (!pythia.next()) continue;
        ++nAceitos;

        // pega a ultima copia do t e do tbar (depois do recuo do ISR, antes de decair)
        Event& event = pythia.event;
        int iTop = -1, iAntiTop = -1;
        for (int i = 0; i < event.size(); ++i) {
            if (event[i].id() == 6) iTop = i;
            if (event[i].id() == -6) iAntiTop = i;
        }
        if (iTop < 0 || iAntiTop < 0) continue;

        hPtTop.Fill(event[iTop].pT());
        hEtaTop.Fill(event[iTop].eta());
        hMtt.Fill((event[iTop].p() + event[iAntiTop].p()).mCalc());
    }

    pythia.stat();

    // sigmaGen e sigmaErr vem em mb. 1 mb = 1e9 pb
    double sigma = pythia.info.sigmaGen() * 1e9;
    double erro = pythia.info.sigmaErr() * 1e9;

    std::cout << std::endl;
    std::cout << "========== resultado (" << modo << ") ==========" << std::endl;
    std::cout << "eventos gerados = " << nAceitos << " de " << nEvents << std::endl;
    std::cout << "sigmaGen = " << pythia.info.sigmaGen() << " +- " << pythia.info.sigmaErr() << " mb" << std::endl;
    std::cout << "sigma    = " << sigma << " +- " << erro << " pb" << std::endl;
    std::cout << "massa do top usada (6:m0) = " << pythia.particleData.m0(6) << " GeV" << std::endl;
    std::cout << "PDF:pSet = " << pythia.settings.word("PDF:pSet") << std::endl;
    std::cout << "==========================================" << std::endl;

    outFile.Write();
    outFile.Close();

    return 0;
}
