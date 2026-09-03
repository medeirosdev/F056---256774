#include "SimpleMET.h"

#include <cmath>

SimpleMET::SimpleMET() : mex_(0.0), mey_(0.0) {}

SimpleMET::SimpleMET(double ex, double ey) : mex_(ex), mey_(ey) {}



double SimpleMET::Value() const {
    return std::sqrt(mex_ * mex_ + mey_ * mey_);
}

double SimpleMET::Ex() const {
    return mex_;
}


double SimpleMET::Ey() const {
    return mey_;
}


double SimpleMET::Phi() const {
    return std::atan2(mey_, mex_);
}




void SimpleMET::Add(double px, double py) {
    mex_ -= px;
    mey_ -= py;
}
