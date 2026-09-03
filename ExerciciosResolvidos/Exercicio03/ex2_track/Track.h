#ifndef TRACK_H
#define TRACK_H

class Track {
public:
    Track(double e, double px, double py, double pz);
    virtual ~Track();
    double E() const;
    double Px() const;
    double Py() const;
    double Pz() const;

    double Pt() const;
    double Eta() const;
private:
    double e_;
    double px_;
    double py_;
    double pz_;
};

#endif
