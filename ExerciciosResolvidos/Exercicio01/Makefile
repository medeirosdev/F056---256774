DOC = relatorio


all: $(DOC).pdf

$(DOC).pdf: $(DOC).tex referencias.bib
	pdflatex $(DOC).tex
	bibtex $(DOC)
	pdflatex $(DOC).tex
	pdflatex $(DOC).tex
AUX_FILES = $(wildcard *.aux *.log *.bbl *.blg *.out)

clean:
	rm -f $(AUX_FILES)

.PHONY: all clean
