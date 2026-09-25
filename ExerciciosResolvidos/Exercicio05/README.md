# F056 - Exercício 05: Interface entre C++, ROOT e Python

Mesmo exercício do 04 (gerar 1000 números gaussianos numa TTree e depois plotar e ajustar),
agora feito de mais dois jeitos: C++ compilado contra o ROOT e PyROOT.

Usei o ROOT 6.40 do ambiente conda (`conda activate rootenv`).

## Como rodar

C++:
```
make
./generate
./plot_and_fit      # gera fit_cpp.png
```

PyROOT:
```
python3 generate.py
python3 plot_and_fit.py    # gera fit_pyroot.png
```

Os dois escrevem/leem o mesmo `dados.root` (TTree `tree`, branch `x`), igual ao exercício 04.

## Parte 1 - root-config

Na minha máquina:

```
$ root-config --cflags
-pthread -std=c++20 -m64 -fsized-deallocation -I/home/medeiros/miniforge3/envs/rootenv/include

$ root-config --libs
-L/home/medeiros/miniforge3/envs/rootenv/lib -lCore -lImt -lRIO -lNet -lHist -lGraf -lGraf3d
-lGpad -lROOTVecOps -lTree -lTreePlayer -lRint -lPostscript -lMatrix -lPhysics -lMathCore
-lThread -lROOTNTuple -lROOTNTupleUtil -lMultiProc -lROOTDataFrame
-Wl,-rpath,/home/medeiros/miniforge3/envs/rootenv/lib -pthread -lm -ldl -rdynamic
```

O `--cflags` passa onde estão os headers (`-I...`) e o padrão de C++ que o ROOT foi compilado,
e o `--libs` passa onde estão as bibliotecas e quais linkar (libCore, libTree, libHist...).
O g++ precisa disso porque ele não sabe sozinho onde o ROOT está instalado, sem isso ele não acha
o `TFile.h` e depois dá undefined reference na hora de linkar. Dentro do `root` o interpretador (Cling)
já vem com tudo isso carregado, por isso no macro nem precisava dos includes.

Obs: o `-std=c++20` do root-config vem depois do `-std=c++17` do Makefile, então no fim compila em c++20
(o ROOT 6.40 pede isso).

## Parte 2 - PyROOT

Diferenças que eu notei do C++ pro Python:

- não declara tipo de nada (`h = ROOT.TH1F(...)` em vez de `TH1F *h = new TH1F(...)`)
- tudo vem de dentro do módulo: `ROOT.TFile`, `ROOT.kYellow`, `ROOT.kBlack`...
- `->` vira `.`
- não tem `new` nem ponteiro, e não precisa de cast no `f.Get("tree")`
- o branch precisa de um buffer que o ROOT consiga escrever, então usei `array("d", [0.0])`
  e `x[0] = ...` no lugar do `double x` + `&x`
- pra ler dá pra fazer `for evento in tree:` e usar `evento.x`, sem `SetBranchAddress`
- tem que colocar `ROOT.gROOT.SetBatch(True)` senão ele tenta abrir janela

O resto é tradução direta, um pra um: `SetLineColor`, `SetLineWidth`, `SetFillColor`, `Fit("gaus")`,
`GetFunction("gaus")`, `GetParameter(1)`, `SaveAs`... os nomes e argumentos são os mesmos.

Como o PyROOT funciona: o Python não reimplementa o ROOT, o `import ROOT` carrega as mesmas bibliotecas
compiladas `libCore.so`, `libHist.so` etc. que o programa da Parte 1 linka. O cppyy usa o Cling
pra ler os headers/dicionários e gera na hora os bindings, então quando eu chamo `h.Fit("gaus")`
no Python quem executa é o `TH1::Fit` em C++ mesmo.

## Parte 3 - Comparação

Tempos com `time` (1000 eventos, na minha máquina):

| versão | generate | plot_and_fit | escrever |
|---|---|---|---|
| macro ROOT (`root -l -b -q`) | 0.68 s | 0.47 s | rápido (já tinha feito) |
| C++ compilado | 0.40 s | 0.43 s | mais chato, precisa de main, includes e Makefile |
| PyROOT | 1.22 s | 1.28 s | mais rápido de escrever |

Com 1000 números quase todo o tempo é carregar as bibliotecas do ROOT, então não muda muito.
O compilado foi o mais rápido de executar e o PyROOT o mais lento (o `import ROOT` demora e o loop
`for evento in tree` é em Python). Pra escrever o Python foi o mais rápido, é mais curto.

O que mudou além da sintaxe:
- macro -> C++ compilado: precisou de `int main()` com `return`, incluir todos os headers
  e compilar/linkar com o root-config. Também coloquei `h->SetDirectory(0)` porque senão o histograma
  pertence ao arquivo e some quando fecha o `file`.
- C++ -> PyROOT: o branch precisa do `array` porque não tem como passar um `&x` de um float do Python,
  a leitura da árvore fica bem mais simples com o `for`, e tem que usar modo batch pra não abrir janela.
  A memória fica por conta do Python (não tem `new`/`delete`).

Erro de tipo:
- no C++ compilado o g++ pega antes de rodar, se eu passar um tipo errado ou chamar um método que não
  existe ele nem compila.
- no macro o Cling também compila antes de executar, então pega na hora que carrega o macro, mas é
  no mesmo momento que roda (e ele deixa passar mais coisa).
- no PyROOT só aparece em tempo de execução, quando a linha é executada, porque o Python não tem
  tipo estático. Ex: se tivesse escrito `"gausss"` só ia dar erro na hora do `GetFunction` retornar `None`.
