#include "SimTrack.h"

SimTrack::SimTrack(double e, double px, double py, double pz, int pdgId,
                    int parentPdgId)
    : Track(e, px, py, pz), pdgId_(pdgId), parentPdgId_(parentPdgId) {}
int SimTrack::ParticleId() const {
    return pdgId_;
}

int SimTrack::ParentId() const {
    return parentPdgId_;
}
