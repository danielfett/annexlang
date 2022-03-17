Annex Language
--------------

The Annex language is a markup language for protocols. Its current
(only) feature is to create protocol descriptions that can be used in
LaTeX documents.

Annex is based on YAML. As of now, there is no further description of
the language except for the example files which make use of most
language features.

To convert a file from Annex to TeX, just run

    annex-convert infile.yml outfile.tex

If you use a chart generated with Annex in your publication, please
include a notice (e.g., "Chart generated with Annex.") somewhere. 

See docs/ for some documentation and examples.