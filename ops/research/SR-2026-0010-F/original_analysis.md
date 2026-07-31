# SR-2026-0010-F — Task 2: Original Analysis
## HBM4E 16-High Qualification Race — Qualification Timeline & Bonding-Method Teardown

Analysis date: 2026-07-31 · Evidence base: `evidence_matrix.md` (37 rows, 6 axes) + snapshots s01–s19 · All row IDs (V-S*, V-H*, V-M*, C-N*, I-*, B-*, F-*) refer to the evidence matrix.

**Traceability convention.** Every quantitative or dated claim in this document carries a matrix row anchor in brackets, e.g. `[V-M2]`. Anything not anchored is labeled `[ASSUMPTION An]` and listed in §6. Evidence classes (A/B/C/NEG) are inherited from the matrix; no claim here is graded higher than its matrix row.

---

## 0. Core finding

**There is no 16-high HBM4E qualification race in the evidence — there is a 16-high development race answering a demand-side request, and a completed 12-high HBM4 qualification race that is being misread as its 16-high counterpart.**

- No source — vendor primary, customer official, or independent — contains a 16-high HBM4E (or 16-high HBM4) qualification, yield, or ramp date for any vendor `[V-S3, V-H6, V-M4, C-N3, I-5 — all NEG]`.
- The only 16-high hardware artifact with a vendor primary is Micron's HBM4 48GB 16H **sample shipment** (March 2026) `[V-M2]`. Samsung's 64GB 16-layer HBM4E is a "planned lineup" expansion only `[V-S2]`; SK hynix's 16-high HBM4E has no announced SKU at all `[V-H6, NEG]`.
- The demand side is real but uncommitted: NVIDIA requested 16-Hi supply for Q4 2026 delivery (December 2025), with performance evaluation possibly starting before Q3 2026 and **no contracts signed** `[V-H8]`; as of July 2026, customer–maker 16-high discussions "remain limited" `[I-4]`.
- Jensen Huang's "all three vendors have been qualified" (2026-06-05) covers **12-high HBM4 only**; the same reporting frames 16-high as "racing to qualify for Vera Rubin Ultra," a late-2027 platform `[C-N2, C-N3]`.

---

## 1. Step 1 — Qualification-timeline synthesis

### 1.1 Per-vendor: claimed milestone vs evidenced status

#### Samsung

| Claimed milestone | Evidenced status | Anchor (class) |
|---|---|---|
| HBM4 mass production + commercial shipment, Feb 2026 | Vendor primary; press corroboration dates shipment 2026-02-12; press (Jan 2026, unattributed industry sources) says Samsung passed NVIDIA/AMD final quality tests | `[V-S6 (B)]`, `[V-S8 (C)]`, `[C-N2 (B)]` |
| HBM4 "designed for NVIDIA Vera Rubin" | Vendor design-in claim only; NVIDIA-side confirmation exists solely as press-carried CEO remarks | `[V-S7 (B)]`, `[C-N1 (NEG)]` |
| HBM4E 12H 48GB samples shipping, announced 2026-05-29; MP "aligned with customer schedules" | Vendor primary, corroborated by TrendForce (agg: News1); no MP date given | `[V-S1 (B)]` |
| HBM4E 64GB **16-layer** in lineup | **Planned expansion only**, "in accordance with customer requirements"; no sample, no date | `[V-S2 (B, planned-only)]` |
| HBM4E 16H sample / qualification / ramp date | **None published by Samsung or any outlet** as of 2026-07-31 | `[V-S3 (NEG)]` |
| HBM4E 16H yield | **None disclosed anywhere.** Closest figures (~10% hybrid-bonded HBM4 *prototype* yield; 1c DRAM "nearing 80% MP target") are single-outlet unattributed secondary — unverified | `[V-S4 (NEG)]`, `[I-5 (NEG)]` |
| HBM4E 16H customer adoption | **None.** No named customer, qualification, or adoption; 16-high customer–maker talks "remain limited" | `[V-S5 (NEG)]`, `[I-4 (C)]` |

**Reading.** Samsung is the only vendor with an HBM4E-generation sampling primary (12-high, May 2026) `[V-S1]`, but at 16-high it has no artifact, no date, and no customer in evidence. Its December 2025 "top-tier evaluation" in SiP testing `[V-S1 context, s11]` and February 2026 commercial shipment `[V-S6]` make it the earliest *evidenced* qualifier at 12-high HBM4.

#### SK hynix

| Claimed milestone | Evidenced status | Anchor (class) |
|---|---|---|
| HBM4 development complete, world-first MP system readied, 2025-09-12 | Vendor primary; press-corroborated | `[V-H1 (B)]` |
| First to supply HBM4 samples to major customers (March 2025); 12-layer HBM4 showcased | Vendor primary; the 16-layer device displayed alongside was **HBM3E, not HBM4(E)** | `[V-H2 (B)]` |
| 16-high HBM4 shown at CES 2026, 48GB, >2TB/s, 30µm wafers inside JEDEC 775µm | Secondary only (Etnews/EE Times via TrendForce); **display ≠ sample shipment** | `[I-2 (C)]`, `[V-H4 (C)]` |
| NVIDIA final qualification of HBM4 (12-high) | **Not completed as of mid-March 2026** (final samples delivered for verification); completed by 2026-06-05 per Huang | `[I-3 (C)]` → `[C-N2 (B)]` |
| 16H HBM4E sample / qualification / ramp dates | **Product does not exist as an announced SKU.** HBM4E samples planned 2H26 in a 12H context, possibly pulled forward | `[V-H6 (NEG)]` |
| 16H yield | **No figures from vendor or press** | `[V-H7 (NEG)]` |
| 16H customer adoption | Demand-side signal only: NVIDIA Q4 2026 16-Hi delivery request; no contracts | `[V-H8 (C)]` |

**Reading.** SK hynix holds the strongest *demonstrated* 16-high stack (CES 2026) `[I-2]` and the largest 12-high allocation estimate (~60–70%, unattributed) `[C-N4]`, but its 12-high qualification closed *last* of the three (window mid-March → 2026-06-05) `[I-3, C-N2]`, and its 16-high HBM4E remains a hypothesis-grade record `[V-H6]`.

#### Micron

| Claimed milestone | Evidenced status | Anchor (class) |
|---|---|---|
| HBM4 36GB 12H high-volume production; volume shipment Q1 CY2026; designed for Vera Rubin | Vendor primary (GTC 2026 press release); press-corroborated | `[V-M1 (B)]` |
| **HBM4 48GB 16H samples shipped to customers, March 2026** | Vendor primary — **the only primary 16-high sample-shipment statement from any vendor**; no independent primary confirmation | `[V-M2 (B)]` |
| HBM4 12H/16H customer qualification, ramp quarter, yield, base-die node | **None disclosed.** Huang's June statement is platform-level and 12-high-scoped; HBM4E ramp targeted 2027 (secondary) | `[V-M4 (NEG)]`, `[C-N2]`, `[V-M4 / s11 (C)]` |

**Reading.** Micron is the only vendor with a 16-high artifact in customer hands per a primary source — but it is **HBM4, not HBM4E**, and a sample shipment is not a qualification `[ASSUMPTION A4]`. Micron's 16H capacity claim (+33% per placement vs 36GB 12H) `[V-M2]` is vendor-self-reported.

### 1.2 Derived qualification order

**12-high HBM4 (the only tier with qualification evidence):**

1. **Samsung** — final quality tests passed per January 2026 press `[V-S8 (C)]`; commercial shipment 2026-02-12 `[V-S6, C-N2-context]`.
2. **Micron** — volume shipment Q1 CY2026 `[V-M1]`; no dated qualification-completion evidence exists, so its position rests on the shipment claim `[ASSUMPTION A1]`.
3. **SK hynix** — not qualified mid-March 2026 `[I-3]`; qualified by 2026-06-05 `[C-N2]`. Window: **mid-March → early June 2026**.

All three qualified by 2026-06-05, 12-high only `[C-N2]`. Ordering between Samsung and Micron is soft: Samsung's anchor is a January press claim of passed tests; Micron's is a Q1 volume-shipment claim with no qualification date `[ASSUMPTION A1]`.

**16-high HBM4E: no qualification order is derivable.** No vendor has a 16-high HBM4E qualification event in evidence `[V-S3, V-H6, V-M4, C-N3 — NEG]`. What the evidence supports is an **artifact-maturity ordering**, which is a different thing:

1. **Micron** — 16H HBM4 samples in customer hands (March 2026) `[V-M2 (B)]`.
2. **SK hynix** — 16-high HBM4 stack publicly demonstrated (CES 2026), process claimed ready to 16-high `[I-2, V-H4 (C)]`.
3. **Samsung** — no 16-high artifact evidenced; 64GB 16H is planned-lineup language only `[V-S2]`.

This ordering must not be reported as a qualification ranking: it mixes classes (one B, two C) and artifact types (shipment vs display vs plan).

### 1.3 Derived ramp windows

| Tier | Evidence-supported window | Anchors |
|---|---|---|
| 12-high HBM4 | In production at all three vendors as of June 2026; first Vera Rubin systems Q3 2026 | `[C-N2]`, `[V-S6]`, `[V-M1]`, `[V-H1]` |
| 12-high HBM4E | Samsung sampling since 2026-05-29, MP "aligned with customer schedules" (undated) `[V-S1]`; SK hynix samples planned 2H26, possibly pulled forward `[V-H6 / s11 (C)]`; Micron MP ramp targeted 2027 `[V-M4 / s11 (C)]` | as cited |
| 16-high (HBM4 or HBM4E) | **No evidenced ramp window for any vendor.** Demand-side target: Q4 2026 delivery request, no contracts `[V-H8]`; platform pull: Vera Rubin Ultra, late 2027 `[C-N3]` | — |

**Derived 16-high ramp estimate: volume no earlier than 2027** `[ASSUMPTION A3]` — synthesis of the late-2027 Vera Rubin Ultra timing `[C-N3]`, Micron's 2027 HBM4E ramp target `[V-M4 / s11]`, and the forecast that hybrid bonding's earliest adoption is 16-high HBM4E with 12-high HBM4E remaining mainstream `[I-4]`. The Q4 2026 NVIDIA request `[V-H8]` is treated as an unmet or partially-met aspiration, not a committed ramp, because no contracts were signed and talks "remain limited" as of July 2026 `[V-H8, I-4]` `[ASSUMPTION A2]`.

Naming caveat: whether 16-high product ships as "HBM4" or "HBM4E" is itself unresolved — an industry official quoted in December 2025 said the name could change with performance and MP timing `[V-H9 (C)]`. This analysis therefore treats the "16-high qualification race" as covering both names `[ASSUMPTION A6]`.

---

## 2. Step 2 — Bonding-method evidence map (16-high)

### 2.1 The evidenced split

Two independent secondary chains agree that through HBM4 (12- and 16-high), **both Korean vendors stayed on thermo-compression-class bonding**: SK hynix on (Advanced) MR-MUF, Samsung and Micron on TC-NCF `[V-M3, V-S9 / s12, s18]`. Hybrid bonding's earliest likely adoption is now forecast at **16-high HBM4E** `[I-4 (C, forecast-grade)]`.

### 2.2 Per vendor: marketing language vs process evidence

**Samsung**

- *Marketing language:* Samsung's own releases describe "optimized packaging structures" and "in-house advanced packaging expertise" without naming any bonding method `[V-S1, V-S6]`. Nothing in Samsung marketing evidences a process choice.
- *Process evidence:* No Samsung primary retrieved states a bonding method for HBM4E. The dataset record claiming "HCB / hybrid copper bonding" for HBM4E 12H (>20% lower heat resistance vs TCB) has **no primary support** `[V-S9 (NEG)]`. Secondary: Samsung used conventional TC bonding for HBM4 `[I-4]`; targets hybrid bonding for 16-layer HBM4E by ~2028 `[V-S9 / s12 (C)]` with hybrid-bonded HBM4 *prototypes* at NVIDIA at ~10% yield (single-outlet, unattributed — unverified) `[V-S4 / s12 (C)]`; has introduced Besi development tools and SEMES hybrid bonders (SEMES "less mature") `[s14 (C, snapshot-level context)]`.
- *Net:* 16-high HBM4E bonding method at Samsung is **undecided in the evidence**; TC-class is the evidenced present, hybrid bonding the reported 2028 target.

**SK hynix**

- *Marketing language:* 2024 newsroom interview — hybrid bonding "being considered for HBM products with 16 layers or more"; both Advanced MR-MUF and hybrid bonding under review `[V-H3 (B)]`. This is a technology-review statement, not a product commitment (matrix note).
- *Process evidence:* Vendor primary confirms **Advanced MR-MUF for HBM4** `[V-H1 (B)]`. For 16-high specifically: SK hynix evaluated fluxless bonding in Q4 2025, rejected it as premature, and **retained Advanced MR-MUF for HBM4 and HBM4E 12- and 16-high**, per DealSite reporting of overseas investor briefings `[V-H4 (C, named-report basis)]` — secondary, not vendor-published. Separately: 12-high hybrid-bonding HBM validation complete per a named SK hynix technical leader (The Elec), yields undisclosed `[V-H5 (C)]`; first MP-intent hybrid-bonding equipment ordered (AMAT/Besi inline, ~KRW 20B; approx. USD 15M per s14's own conversion) `[V-H5 / s14 (C)]`. Above 20 layers, next-gen bonding seen as "unavoidable" `[V-H4 / s13]`.
- *Net:* **MR-MUF is the evidenced 16-high process** (class C for the 16-high-specific retention; class B for HBM4 generally). Hybrid bonding is a validated-but-deferred parallel track.

**Micron**

- *Marketing language:* None retrieved on bonding.
- *Process evidence:* Product page (partially retrieved) describes TSV DRAM dies + TSV logic die stacking; **no hybrid bonding disclosed** `[V-M3 (B)]`. Secondary places Micron on the **TC-NCF** path for current HBM4 `[V-M3 / s18 (C)]`. Nothing names a bonding method for the 16H samples `[V-M2]`.
- *Net:* TC-class (reported TC-NCF) is the evidenced present; 16-high method undisclosed by Micron.

### 2.3 Why the deferral is credible (technical cross-check)

Vendor-neutral grounding `[B-1 (technical reference)]`: hybrid bonding removes bumps/underfill and enables <10µm pitch, but is highly sensitive to defects, voids, and overlay error, requires <50nm-class alignment, and D2W surfaces roughen with die thinning — metrology and warpage are the gating challenges. This is consistent with (a) reported ~10% Samsung hybrid-prototype yields `[V-S4 / s12, unverified C]`, (b) SK hynix's "premature" verdict on fluxless bonding `[V-H4]`, and (c) the industry-wide slip of hybrid bonding to 16-high HBM4E `[I-4]`. Mechanical constraints are corroborated by two independent secondary chains: 50µm → ~30µm die thinning, JEDEC 775µm package cap, ~10µm bond-line that must shrink `[B-2]`.

**Marketing-vs-process summary:** no vendor's *own* publication claims hybrid bonding in any shipping or sampled HBM product. Every hybrid-bonding claim in the file is either (i) a vendor "under review / considered" statement `[V-H3]`, or (ii) secondary reporting `[V-S9-chain, V-H4, V-H5, I-4]`. Every *evidenced* production process through HBM4 16-high is TC-class (MR-MUF or TC-NCF).

---

## 3. Step 3 — Traceability ledger (every number in this document)

| # | Figure / date as used | Matrix anchor | Class |
|---|---|---|---|
| 1 | Samsung HBM4E 12H 48GB samples, announced 2026-05-29; 14Gbps stable / 16Gbps scalable; up to 3.6TB/s; +16% energy efficiency; >14% thermal-resistance improvement | V-S1 | B |
| 2 | Samsung HBM4E lineup expansion: 32GB (8-layer), 64GB (16-layer), planned only | V-S2 | B (planned-only) |
| 3 | Samsung HBM4 MP + commercial shipment Feb 2026 (2026-02-12 per press); 11.7Gbps (up to 13Gbps); 3.3TB/s; 1c DRAM + 4nm base die; 2,048 I/O; +40% power efficiency; 24–36GB 12H; 16-layer to 48GB | V-S6, C-N2-context | B |
| 4 | SK hynix HBM4 development complete / MP system, 2025-09-12; >10Gbps; 2,048 I/O; +40% power efficiency; Advanced MR-MUF; 1bnm | V-H1 | B |
| 5 | SK hynix first HBM4 samples to major customers, March 2025; 16-layer display = HBM3E | V-H2 | B |
| 6 | SK hynix 16-high HBM4 at CES 2026; 48GB; >2TB/s; 30µm wafers; JEDEC 775µm | I-2, V-H4 | C |
| 7 | SK hynix HBM4 NVIDIA qualification: not complete mid-March 2026 → qualified by 2026-06-05 | I-3, C-N2 | C → B |
| 8 | Huang 2026-06-05 "all three qualified / in production"; Q3 2026 system shipments; scope = 12-high HBM4 | C-N2, C-N3 | B (press-carried) |
| 9 | NVIDIA 16-Hi delivery request Q4 2026 (Dec 2025); performance evaluation possibly before Q3 2026; no contracts | V-H8 | C |
| 10 | Customer–maker 16-high talks "remain limited" (July 2026); 12-high HBM4E stays mainstream; hybrid bonding earliest at 16-high HBM4E | I-4 | C (forecast) |
| 11 | Micron HBM4 36GB 12H volume shipment Q1 CY2026; >2.8TB/s; >11Gbps; +20% power efficiency | V-M1 | B |
| 12 | Micron HBM4 48GB 16H samples shipped March 2026; +33% capacity per placement vs 36GB 12H | V-M2 | B |
| 13 | Micron HBM4E MP ramp targeted 2027; SK hynix HBM4E samples planned 2H26 | V-M4 / s11, V-H6 / s11 | C |
| 14 | Vera Rubin Ultra platform, late 2027; 16-high "racing to qualify" | C-N3 | B/C |
| 15 | NVIDIA HBM4 allocation estimate ~60–70% SK hynix / 25–30% Samsung / remainder Micron (not NVIDIA-published); Counterpoint 54/28/18 | C-N4 | C |
| 16 | Samsung hybrid-bonded HBM4 prototype yield ~10%; 1c DRAM "nearing 80% MP target" | V-S4 / s12 | C — **unverified, single-outlet unattributed** |
| 17 | Samsung hybrid-bonding 16-layer HBM4E target ~2028 | V-S9 / s12 | C |
| 18 | SK hynix fluxless evaluation Q4 2025, rejected; MR-MUF retained through HBM4/HBM4E 16-high | V-H4 | C |
| 19 | SK hynix 12-high hybrid-bonding validation complete; AMAT/Besi inline bonder ~KRW 20B (approx. USD 15M per s14's own conversion) | V-H5 / s14 | C |
| 20 | Die thinning 50µm → ~30µm; JEDEC HBM4 cap 775µm (HBM3E 720/725µm); bond-line ~10µm | B-2 | C (two independent chains) |
| 21 | Hybrid bonding: <10µm pitch; <50nm alignment; W2W most mature; D2W rougher | B-1 | B (technical reference) |
| 22 | HBM5 height discussion ~900–1000µm | I-4 / s15 | C |
| 23 | JEDEC may relax HBM5 height; Samsung HPB / SK hynix iHBM tested for HBM5 | I-4 / s15 | C |
| 24 | "16-Hi may be named HBM4E; name could change" | V-H9 | C |

Unanchored quantities in this document: none. Derived windows and interpretations are registered below as assumptions.

---

## 4. Assumption register

- **A1 — Samsung-before-Micron ordering at 12-high.** Samsung's anchor is a January 2026 press claim of passed final tests `[V-S8, C]`; Micron has no dated qualification-completion evidence, only Q1 CY2026 volume shipment `[V-M1]`. The ordering assumes shipment implies prior qualification.
- **A2 — NVIDIA's Q4 2026 16-Hi request treated as target, not commitment.** Basis: no contracts signed, evaluation only "possibly" before Q3 2026 `[V-H8]`, talks "remain limited" `[I-4]`.
- **A3 — 16-high volume no earlier than 2027.** Synthesis of late-2027 Vera Rubin Ultra `[C-N3]`, Micron 2027 HBM4E ramp `[V-M4 / s11]`, and hybrid-bonding timing `[I-4]`. Forecast, not evidence.
- **A4 — Samples ≠ qualification.** Micron's 16H sample shipment `[V-M2]` is treated as an engineering-sample milestone; no qualification inference is drawn from it.
- **A5 — Aggregator attribution.** TrendForce articles are credited to their underlying outlets (Etnews, The Elec, DealSite, ZDNet, Newsis, Korea Herald, Sisa Journal) as recorded per matrix row; no independent weight is given to the aggregation layer.
- **A6 — Naming.** "16-high qualification race" is analyzed across both "16-Hi HBM4" and "16-high HBM4E" names, per the unresolved naming signal `[V-H9]`.

---

## 5. Cross-checks, conflicts, and negative results that bound this analysis

- **s10 internal error:** Tech Times cites a JEDEC height limit of "approximately 720 micrometers" for 16-high; the matrix flags this `[sic]` — the evidenced HBM4 cap is 775µm `[B-2, I-4]`. This analysis uses 775µm throughout.
- **I-3 vs C-N2:** the March 2026 "not qualified" report is superseded by Huang's June 2026 statement; together they define SK hynix's 12-high qualification window rather than contradicting each other.
- **s03 vs s01:** Samsung's February release projected HBM4E sampling in 2H 2026; the May 2026 sample shipment superseded it (matrix note, s03). Used here as evidence the HBM4E timeline pulled forward at 12-high — which makes the *absence* of any 16-high date more informative, not less.
- **Yield:** the only numeric yield figures in the entire evidence base (~10% Samsung hybrid prototype; ~80% 1c target) are single-outlet unattributed secondary `[V-S4, I-5]`. They are reported above as context and must not appear in the final report as verified yields.
- **MDPI peer-reviewed thermal figure (~47% lower thermal resistance, 16-Hi hybrid vs microbump)** could not be captured (SNAPSHOT_UNAVAILABLE, Akamai block) `[B-3]`. Excluded from this analysis pending manual capture.

---

## 6. Bottom line for the final report

1. Frame 16-high as **demand-side only**: an NVIDIA request (Q4 2026) `[V-H8]` with no vendor qualification, yield, or ramp date in evidence `[V-S3, V-H6, V-M4, C-N3, I-5]`.
2. If a "race order" must be printed, print the **artifact-maturity order** (Micron > SK hynix > Samsung, §1.2) with its class caveats — never a qualification order.
3. 12-high HBM4 qualification order: Samsung → Micron → SK hynix, all qualified by 2026-06-05 `[V-S8, V-M1, I-3, C-N2]` with A1 caveat.
4. Bonding: TC-class everywhere in evidence through HBM4 16-high (MR-MUF at SK hynix, TC-NCF reported at Samsung/Micron); hybrid bonding's earliest adoption is 16-high HBM4E `[I-4]`; the dataset's Samsung-HCB and SK hynix-hybrid framings are unsupported by primaries `[V-S9, V-H3, V-H4]`.
