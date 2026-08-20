#nome
DOC = relatorio

all: $(DOC).pdf

$(DOC).pdf: $(DOC).tex referencias.bib
	pdflatex $(DOC).tex
	bibtex $(DOC)
	pdflatex $(DOC).tex
	pdflatex $(DOC).tex

#rever depois
AUX_FILES = $(wildcard *.aux *.log *.bbl *.blg *.out)

#limpa
clean:
	rm -f $(AUX_FILES)

.PHONY: all clean
