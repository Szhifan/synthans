# Building the ACL template

The files in this directory are from the [official ACL style repository](https://github.com/acl-org/acl-style-files), `master` commit `d5adc823ff0f80f98c80405ca0ab66c68e684409` (downloaded 2026-10-20). Start editing `acl_latex.tex`; keep `acl.sty` and `acl_natbib.bst` beside it.

With a TeX installation, build the main template from this directory:

```sh
latexmk -pdf acl_latex.tex
```

Use this command for the editor's build recipe as well. It runs BibTeX and repeats
LaTeX until citations and review-mode line-number positions are resolved. A single
pdfLaTeX pass can leave question marks in citations and line numbers over the text.
If an earlier failed build left an empty bibliography, regenerate it before rebuilding:

```sh
bibtex acl_latex
latexmk -pdf acl_latex.tex
```

The main template was also compiled successfully here with Tectonic 0.17.0:

```sh
tectonic acl_latex.tex
```

The resulting `acl_latex.pdf` is included. The build emitted layout warnings, but no errors.

The separate `acl_lualatex.tex` example uses Hindi and Arabic text and requires the system fonts **Lohit Devanagari** and **Noto Sans Arabic**. Its build was attempted with Tectonic in this environment and stopped because Lohit Devanagari is not installed. Once both fonts are available, compile it with XeLaTeX or LuaLaTeX.
