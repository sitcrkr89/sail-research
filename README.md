# Sail Research

Sail Research is an evidence-first public research desk focused on Korean industry signals that matter to global strategy teams. The site publishes primary-source-led work on semiconductors, biopharma, and AI-native research systems.

## Public structure

- `index.html` — research-led landing page
- `research/index.html` — searchable report library and coverage map
- `research/methodology.html` — evidence, review, and corrections contract
- `reports/` — published reports and the publication template
- `assets/` — shared public assets

## Editorial contract

Every public report must:

1. state its evidence grade and verification boundary;
2. separate verified fact from analysis or model priors;
3. retain counter-evidence and open verification gaps;
4. provide the most direct public source links available;
5. record material corrections and whether they changed the thesis or grade;
6. pass a human release gate.

## Local preview

```bash
python3 -m http.server 8000
```

Open `http://localhost:8000/`.

## Quality checks

```bash
python3 scripts/validate_site.py
```

The validator checks metadata, heading structure, local links, report navigation, card counts, and known publication defects. The legacy methodology page is explicitly exempt from the new canonical/Open Graph checks until its public copy is migrated. GitHub Actions runs the same check for every pull request and push to `main`.

## Publishing a report

Start from `reports/_TEMPLATE.html`, add the report card to `research/index.html`, update the latest-publication date, update `sitemap.xml`, and run the quality check before review. Publication is not authorized by automation alone.
