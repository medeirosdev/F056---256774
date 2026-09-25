import ROOT
from array import array

N = 1000
mean = 0.0
sigma = 1.0

f = ROOT.TFile("dados.root", "RECREATE")
tree = ROOT.TTree("tree", "Num aleat gaussianos")

x = array("d", [0.0])
tree.Branch("x", x, "x/D")

rnd = ROOT.TRandom3(0)
for i in range(N):
    x[0] = rnd.Gaus(mean, sigma)
    tree.Fill()

f.cd()
tree.Write()
f.Close()

print("gerou", N, "numeros em dados.root")
