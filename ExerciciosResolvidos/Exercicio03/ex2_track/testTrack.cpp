#include <iostream>

#include "SimTrack.h"

int main() {
    SimTrack track1(10.0, 3.0, 4.0, 8.0, 11, 23);
    SimTrack track2(50.0, 0.0, 0.0, 50.0, 211, 111);

    SimTrack *tracks[2] = {&track1, &track2};

    for (int i = 0; i < 2; ++i) {
        std::cout << "Traco " << (i + 1) << ":" << std::endl;
        std::cout << "  Pt  = " << tracks[i]->Pt() << " GeV" << std::endl;
        std::cout << "  Eta = " << tracks[i]->Eta() << std::endl;
        std::cout << "  ParticleId = " << tracks[i]->ParticleId() << std::endl;
        std::cout << "  ParentId   = " << tracks[i]->ParentId() << std::endl;
        std::cout << std::endl;
    }

    return 0;
}
