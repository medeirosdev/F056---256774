#include <iostream>

#include "SimpleMET.h"

int main() {
    SimpleMET met1;
    met1.Add(20.0, 0.0);
    met1.Add(-20.0, 0.0);

    std::cout << "Teste 1 - dois objetos opostos" << std::endl;
    std::cout << "  Value = " << met1.Value() << " (esperado ~0)" << std::endl;
    std::cout << "  Ex = " << met1.Ex() << ", Ey = " << met1.Ey() << std::endl;
    std::cout << std::endl;
    SimpleMET met2;
    met2.Add(30.0, 0.0);
    met2.Add(0.0, 40.0);

    std::cout << "Teste 2 - dois objetos perpendiculares" << std::endl;
    std::cout << "  Value = " << met2.Value() << " (esperado 50)" << std::endl;
    std::cout << "  Ex = " << met2.Ex() << ", Ey = " << met2.Ey() << std::endl;
    std::cout << "  Phi = " << met2.Phi() << " rad" << std::endl;
    std::cout << std::endl;


    SimpleMET met3(5.0, 0.0);
    met3.Add(10.0, 0.0);
    met3.Add(0.0, 10.0);

    std::cout << "Teste 3 - MET inicial nao nula + dois objetos" << std::endl;
    std::cout << "  Value = " << met3.Value() << std::endl;
    std::cout << "  Ex = " << met3.Ex() << ", Ey = " << met3.Ey() << std::endl;
    std::cout << "  Phi = " << met3.Phi() << " rad" << std::endl;

    return 0;
}
