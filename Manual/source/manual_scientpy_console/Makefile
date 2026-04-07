TEX      = ScientoPy_user_manual
OUTDIR   = ../../
LATEX    = pdflatex --shell-escape

.PHONY: all pdf dvi clean

all: pdf

pdf: $(TEX).tex
	$(LATEX) $(TEX).tex
	$(LATEX) $(TEX).tex
	cp $(TEX).pdf $(OUTDIR)

dvi: $(TEX).tex
	latex $(TEX).tex
	latex $(TEX).tex

clean:
	rm -f $(TEX).aux $(TEX).log $(TEX).out $(TEX).toc $(TEX).dvi $(TEX).pdf
