#include "Track.h"

#include <cmath>
#include <limits>

Track::Track(double e, double px, double py, double pz)
    : e_(e), px_(px), py_(py), pz_(pz) {}

Track::~Track() {}

double Track::E() const {
    return e_;
}
double Track::Px() const {
    return px_;
}

double Track::Py() const {
    return py_;
}

double Track::Pz() const {
    return pz_;
}


double Track::Pt() const {
    return std::sqrt(px_ * px_ + py_ * py_);
}

double Track::Eta() const {
    double pt = Pt();
    if (pt == 0.0) {
        return (pz_ >= 0.0) ? std::numeric_limits<double>::infinity()
                             : -std::numeric_limits<double>::infinity();
    }

    double p = std::sqrt(px_ * px_ + py_ * py_ + pz_ * pz_);
    double theta = std::acos(pz_ / p);
    return -std::log(std::tan(theta / 2.0));
}
