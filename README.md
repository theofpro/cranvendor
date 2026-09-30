# cranvendor

Small proof of concept for finding third-party libraries that CRAN packages bundle in their sources (C/C++ under `src/`, JavaScript under `inst/`), reading their version, and checking that version against OSV.

Why I started this: 12 of the 14 advisories in the [R Consortium Advisory Database](https://github.com/RConsortium/r-advisory-database) are about bundled code, not R code (libxls in readxl, yajl in jsonlite, cmark-gfm in commonmark, plotly.js in plotly, and so on). CRAN policy asks maintainers to include library sources in the package, which is fine, but nobody seems to keep a list of what is bundled where. osv-scanner only looks for vendored code in folders called `vendor`, `third_party`, `deps` etc., so it doesn't see the usual `src/<lib>/` layout of R packages.

This is the pilot for a grant proposal to the R Consortium ISC. It's rough on purpose.

## Run it

Python 3.10+ and git, nothing else.

```
python scan.py readxl jsonlite commonmark   # current CRAN versions
python scan.py --top 300 > top300.csv        # most downloaded packages
python retro.py                              # test on past advisories
```

`scan.py` downloads each tarball, extracts only `src/`, `inst/`, `tools/`, `configure*` and NEWS, scans and throws everything away. It writes a CSV with the library, the version and where the version came from (macro, config.h or NEWS).

## Does it work on known cases?

`retro.py` takes the last affected CRAN version for every advisory caused by bundled code, scans it, queries OSV and checks if the CVEs of the advisory come back. Output of my last run:

| Advisory | Package | Library | Version found | CVEs matched |
|---|---|---|---|---|
| RSEC-2023-0 | readxl 1.0.0 | libxls | 1.4.0 | 6 of 7 |
| RSEC-2023-1 | readxl 1.2.0 | libxls | 1.4.0 | 4 of 4 |
| RSEC-2023-2 | readxl 1.4.1 | libxls | 1.6.2 | 1 of 1 |
| RSEC-2023-3 | jsonlite 1.8.7 | yajl | 2.1.1 (no such upstream tag) | 0 of 1 |
| RSEC-2023-4 | igraph 1.2.2 | igraph | 1.2.2 (no such upstream tag) | 0 of 1 |
| RSEC-2023-5 | haven 1.1.0 | ReadStat | not found | 0 of 3 |
| RSEC-2023-6 | commonmark 1.7 | cmark-gfm | 0.28.3.gfm.19 | 1 of 1 |
| RSEC-2023-7 | commonmark 1.7 | cmark-gfm | 0.28.3.gfm.19 | 2 of 2 |
| RSEC-2023-8 | commonmark 1.9.1 | cmark-gfm | 0.29.0.gfm.6 | 7 of 7 |
| RSEC-2025-1 | plotly 4.11.0 | plotly.js | 2.11.1 | 1 of 1 |
| RSEC-2026-0 | widgetframe 0.3.0 | pym.js | 1.3.1 | 1 of 1 |

So the library is found every time, and 8 of 11 advisories get their CVEs back. The misses: jsonlite ships a patched yajl labelled 2.1.1, which isn't an upstream tag (2.1.0 would match). For igraph it reads the R package version instead of the C core one. haven's ReadStat has no version macro at all.

## Known limits

- Version macros can be stale (commonmark updated cmark-gfm but the header still says gfm.6).
- A patched copy looks vulnerable (jsonlite fixed CVE-2023-33460 in its yajl copy).
- Partial copies look like full ones (digest only ships zlib's crc32.c).
- OSV's git data is empty for some libraries I tried (libxml2, libuv, pcre2, bzip2, lz4, zstd, libyaml). An NVD fallback is planned.

Because of that, nothing it prints about a current package should be read as "this package is vulnerable" without checking by hand. Real findings go to the maintainer privately first.

Apache-2.0.
