# Sail Research

Decision-grade evidence desk for Korea bottleneck industries—semiconductors, biopharma, and power—for global strategy, CI, and diligence teams.

**Visual system:** Dark forest surfaces, off-white type, and brass accents, with responsive institute navigation and report-table scrolling.

## Public structure

- `index.html` — Desk pulse, search, watch rail, core research board, coverage, grades, scope CTA
- `research/index.html` — Filterable report board (table)
- `research/methodology.html` — Sources & methodology (capture, grades, boundaries)
- `governance.html` / `corrections.html` — release controls and public correction history
- `product.html` / `for.html` / `about.html` / `scope.html` / `digest.html`
- `reports/` — Evidence briefs (`assets/report.css`)
- `assets/site.css` — shared design system

## Editorial contract

1. State evidence grade and verification boundary  
2. Separate verified fact from analysis  
3. Keep counter-evidence and open gaps  
4. Cite the most direct public sources  
5. Note material corrections  
6. Keep routine-brief automation distinct from the owner review required for Full Reports

`ops/publications.json` is the canonical current-state registry. `ops/publication_log.md` remains an append-only event log. Evidence strength, claim state, and publication status are separate enums defined in `ops/editorial_taxonomy.json`; the public grade definitions are generated from that taxonomy rather than maintained as duplicate prose.

Generated public blocks are bounded by HTML markers. Edit the registry, then render and check:

```bash
python3 scripts/render_publication_surfaces.py --write
python3 scripts/render_publication_surfaces.py --check
python3 scripts/sync_report_metadata.py --write
python3 scripts/sync_report_metadata.py --check
```

Metadata sync also applies visible archive notices to legacy reports. Social previews use the checked 1200×630 `assets/social-card.png`; the SVG remains the editable source artwork.

The existing delegated publisher predates this registry contract. It must be updated in its own authorized operational change before any site push; otherwise preflight should fail closed on stale surfaces.

## Local preview

```bash
python3 -m http.server 8000
```

## Quality checks

```bash
python3 scripts/validate_site.py
python3 -m unittest discover -s tests -v
python3 scripts/run_all_preflights.py
semgrep --config .semgrep.yml --error --metrics=off --no-git-ignore scripts *.html research reports
```
