import ROOT

ROOT.gROOT.SetBatch(True)

f = ROOT.TFile("dados.root", "READ")
tree = f.Get("tree")

h = ROOT.TH1F("h", "dist. gerada;Valor gerado;num de entradas", 50, -5, 5)
h.SetDirectory(0)

for evento in tree:
    h.Fill(evento.x)

h.SetLineColor(ROOT.kBlack)
h.SetLineStyle(1)
h.SetLineWidth(3)
h.SetFillColor(ROOT.kYellow)

c = ROOT.TCanvas("c", "hist", 800, 600)
c.SetFillColor(ROOT.kWhite)

h.Fit("gaus")
h.Draw()

fit = h.GetFunction("gaus")
print("media do ajuste:", fit.GetParameter(1))
print("sigma do ajuste:", fit.GetParameter(2))

c.SaveAs("fit_pyroot.png")

f.Close()
