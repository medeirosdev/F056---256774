#include <cstdlib>
#include <iostream>

//,aom
int main(int argc, char *argv[]) {
    if (argc < 2) {
        std::cerr << "uso: " << argv[0] << " <numero>" << std::endl;
        return 1;
    }

    int n = std::atoi(argv[1]);
    std::cout << "Hello world " << n << std::endl;

    return 0;
}
