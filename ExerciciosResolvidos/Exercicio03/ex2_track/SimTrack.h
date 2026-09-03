#ifndef SIMTRACK_H
#define SIMTRACK_H

#include "Track.h"

class SimTrack : public Track {
public:
    SimTrack(double e, double px, double py, double pz, int pdgId,
              int parentPdgId);
    int ParticleId() const;
    int ParentId() const;
private:
    int pdgId_;
    int parentPdgId_;
};

#endif
