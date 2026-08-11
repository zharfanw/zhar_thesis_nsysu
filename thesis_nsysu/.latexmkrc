$pdf_mode = 5;        # build PDF via XeLaTeX (thesis.tex requires fontspec, which pdflatex cannot run)
$postscript_mode = $dvi_mode = 0;
$bibtex_use = 2;      # always rerun bibtex when citations or the .bib file change
$xelatex = 'xelatex -synctex=1 -interaction=nonstopmode -file-line-error %O %S';
