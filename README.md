# Sail Research

Decision-grade evidence desk for Korea bottleneck industries—semiconductors, biopharma, and power—for global strategy, CI, and diligence teams.

**Visual system:** Light gray surfaces + **navy body text** (high contrast). Structure patterned after Korean-market reference desks (search-first home, pulse bar, watch rail, table board)—without quote feeds or investment signals.

## Public structure

- `index.html` — Desk pulse, search, watch rail, core research board, coverage, grades, scope CTA
- `research/index.html` — Filterable report board (table)
- `research/methodology.html` — Sources & methodology (capture, grades, boundaries)
- `product.html` / `for.html` / `about.html` / `scope.html` / `digest.html`
- `reports/` — Evidence briefs (`assets/report.css`)
- `assets/site.css` — shared design system

## Editorial contract

1. State evidence grade and verification boundary  
2. Separate verified fact from analysis  
3. Keep counter-evidence and open gaps  
4. Cite the most direct public sources  
5. Note material corrections  
6. Human release gate  

## Local preview

```bash
python3 -m http.server 8000
```

## Quality checks

```bash
python3 scripts/validate_site.py
```
