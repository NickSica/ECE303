(TeX-add-style-hook
 "report"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-class-options
                     '(("article" "12pt" "titlepage")))
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("hyperref" "linktoc=all")))
   (TeX-run-style-hooks
    "latex2e"
    "article"
    "art12"
    "hyperref"
    "listings"
    "graphicx"
    "xcolor")
   (LaTeX-add-labels
    "fig:lab_2"
    "eq:ocr3a"
    "fig:lab_3"))
 :latex)

