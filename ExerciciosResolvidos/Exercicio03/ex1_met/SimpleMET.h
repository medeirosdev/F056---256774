#ifndef SIMPLEMET_H
#define SIMPLEMET_H

class SimpleMET {
public:
    SimpleMET();
    SimpleMET(double ex, double ey);
    double Value() const;
    double Ex() const;
    double Ey() const;
    double Phi() const;

    void Add(double px, double py);
private:
    double mex_;
    double mey_;
};

#endif
