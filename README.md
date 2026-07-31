# Sail Research

Sail Research is a decision-grade evidence desk for Korea bottleneck industries—semiconductors, biopharma, and power infrastructure—serving global strategy, competitive intelligence, and diligence teams.

**Visual system:** Light Institutional (paper ground, ink type, navy accent)—designed to read as attachable intelligence, not a tech-startup landing page.

## Public structure

- `index.html` — GTM homepage (position, ICP, coverage, evidence explorer, offers, digest, scope CTA)
- `product.html` — offer ladder (Public Brief → Decision Memo → Tracker → Engagement)
- `for.html` — who it’s for / not for
- `about.html` — desk, independence, policies
- `scope.html` — structured scope form (mailto handoff)
- `digest.html` — Evidence Digest request
- `research/index.html` — searchable report library
- `research/methodology.html` — evidence, review, and corrections contract
- `reports/` — published reports and templates
- `assets/site.css` — global professional design system

## Editorial contract

Every public report must:

1. state its evidence grade and verification boundary;
2. separate verified fact from analysis or model priors;
3. retain counter-evidence and open verification gaps;
4. provide the most direct public source links available;
5. record material corrections and whether they changed the thesis or grade;
6. pass a human release gate.

## Interactive experience

- **Decision Lens** — switches decision question and next action by core sector
- **Evidence Explorer** — verified fact / interpretation / open gap
- **Signal Matrix** — coverage, watch conditions, honest buildout status
- **Scope form** — qualified commercial intake with 2-business-day SLA messaging

## Local preview

```bash
python3 -m http.server 8000
```

Open `http://localhost:8000/`.

## Quality checks

```bash
python3 scripts/validate_site.py
```

## Publishing a report

Start from `reports/_TEMPLATE.html`, add the report card to `research/index.html`, update the latest-publication date on the homepage and library, update `sitemap.xml`, and run the quality check before review.
