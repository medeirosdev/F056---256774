DOC = relatorio

all: $(DOC).pdf

$(DOC).pdf: $(DOC).tex $(wildcard ../figuras/*.png)
	pdflatex -interaction=nonstopmode $(DOC).tex
	pdflatex -interaction=nonstopmode $(DOC).tex

AUX_FILES = $(wildcard *.aux *.log *.out *.toc)

clean:
	rm -f $(AUX_FILES)

.PHONY: all clean
