# cranvendor

Finds third-party C/C++ and JS libraries bundled in CRAN package sources, reads their version and looks them up in OSV.

Proof of concept for an R Consortium ISC proposal.

```
python scan.py readxl jsonlite
python scan.py --top 300 > top300.csv
python retro.py
```

`retro.py` reruns it on past RSEC advisories caused by bundled code. Last run: library found 11/11, advisory CVEs back for 8/11.

Results on current packages are not checked by hand, don't treat them as vulnerabilities.

Apache-2.0
