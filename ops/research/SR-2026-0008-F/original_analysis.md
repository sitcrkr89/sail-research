# Original Analysis — SR-2026-0008-F
## Correction-Style Teardown: WO2020088180A1 Maps to WuXiUP™, Not WuXiUI™

**Compiled**: 2026-07-29 · **Consumes**: `evidence_matrix.md` (rows C1–C22) + archived snapshots
**Traceability convention**: every number carries a matrix anchor `[C#]`; every non-sourced input carries an assumption ID `[A#]` defined in §4. No other numbers are used. This document is technical analysis, not legal advice.

**Thesis under test (owner-approved reframe)**: Patent WO2020088180A1 — continuous-harvest, no-bleed intensified perfusion — is architecturally aligned with WuXi Biologics' **WuXiUP™** continuous bioprocessing platform, **not** with **WuXiUI™**, which is an ultra-intensified intermittent-perfusion **fed-batch** (UI-IPFB). The free sample SR-2026-0008 conflated the two.

---

## 1. Patent claim-scope teardown

### 1.1 Independent-claim inventory (verbatim, from archived claims snapshot `sources/patent-wo2020088180a1-claims.txt`)

The publication has 50 claims and exactly **three independent claims**:

**Claim 1 (method)** — "*A method for producing a biological substance comprising: (a) culturing a cell culture comprising a cell culture medium and cells, (b) perfusing the cell culture in a bioreactor with a basal medium and a feed medium, and (c) harvesting the biological substance, wherein the basal medium and the feed medium are fed to the cell culture at different rates, the cell culture is continuously passed through a separation system, and the cells are retained in the bioreactor without bleeding.*"

**Claim 41 (product-by-process)** — "*A biological substance produced by any one of claims 1-40.*"

**Claim 42 (system)** — "*A system for producing a biological substance comprising: (a) a module for perfusing a cell culture in a bioreactor with a basal medium and a feed medium; and (b) a module for continuously harvesting the biological substance, comprising a hollow fiber filter having a pore size or a molecular weight cut-off (MWCO) larger than the molecular weight of the biological substance.*"

### 1.2 Element-by-element: what the claims legally cover vs. what each platform actually is

| # | Claim element (verbatim anchor) | Legal scope (plain reading) | ATF/TFF implementation constraint | WuXiUI™ (UI-IPFB) match? | WuXiUP™ match? |
|---|---|---|---|---|---|
| E1 | "perfusing the cell culture … with a basal medium and a feed medium … **at different rates**" (claim 1(b)) | Differential basal/feed perfusion is a **required** element; a process feeding a single medium, or both at locked rates, does not literally read on it | Requires two independent flow paths/controllers into the ATF/TFF loop; feed typically 0.1–20% of basal rate (claims 12–15) | Partial — UI-IPFB uses intermittent perfusion cycles "to replenish key nutrients" [C12], but company does not describe differential basal/feed metering for WuXiUI | Yes — WuXiUP is an "intensified perfusion culture process" [C21]; differential feeding is standard perfusion practice |
| E2 | "the cell culture is **continuously passed through a separation system**" (claim 1) | The production culture itself circulates through the retention device for the **whole culture**, not intermittently | ATF/TFF sized for continuous recirculation at production scale; filter fouling becomes the culture-duration-limiting failure mode | **No** — WuXiUI's defining step is "intermittent-perfusion fed-batch" [C11][C12]; perfusion cycles are episodic, and the ATF is shareable "N-1 to N" [C12], i.e., primarily a seed/intensification device | **Yes** — WuXiUP "adopts continuous harvest to greatly reduce the product residence time" [C21] |
| E3 | "the cells are retained in the bioreactor **without bleeding**" (claim 1) | No cell purge for the entire culture. This is the claim's namesake limitation and its clearest bright-line test | Retention device must sustain viability at peak VCD with zero bleed; microsparger O₂ delivery 0.2–0.5 VVM (claims 22–23) and temperature shift to 28–33 °C before peak VCD (claims 17–19) are the supporting levers disclosed | **No** — nothing in WuXiUI materials claims bleed-free operation; a fed-batch with cell concentration steps [C12] is architecturally indifferent to the no-bleed limitation | **Yes** — continuous harvest with cell retention is WuXiUP's stated core [C21]; the patent's no-bleed claim is exactly what makes continuous harvest without biomass loss possible |
| E4 | "harvesting the biological substance" + claim 42(b) "**continuously harvesting** … hollow fiber filter … MWCO larger than the molecular weight of the biological substance" | Product leaves the bioreactor **during** culture through a filter that passes product and retains cells | Hollow-fiber pore 0.08–0.5 µm (claims 5–7, 46–49) must pass a ~150 kDa mAb while retaining ~10–20 µm cells; sieving decay over 2–3 weeks is the key process risk | **No** — WuXiUI harvests at batch end like any fed-batch; its 2,000 L GMP run reports a single final "DS yield of 70%" [C15], a batch-harvest metric | **Yes** — WuXiUP's continuous harvest is explicit [C21] and its performance metric is accumulative ("105 g/L over 20 days" [C22]) — a continuous-harvest framing |
| E5 | "subjecting the harvested biological substance to a **continuous product capture** process using between 2 and 16 chromatography columns" (claims 36–40) | Optional dependent element: multi-column continuous capture directly coupled to harvest | Requires PCC/SMB capture hardware; patent examples use 3-column MabSelect PrismA [C9] | **No** — the WuXiUI launch PR promises "minimum changes to the downstream process" [C11]; its 2,000 L run used an "enhanced downstream technology platform" with doubled capacity, not continuous capture [C15] | **Yes** — WuXiUP "couples continuous upstream process with continuous direct product capture using multicolumn chromatography system operating in a periodic countercurrent (PCC) mode" [C21]; 92% Protein A resin reduction reported [C22] |
| E6 | "achieves an **accumulative volumetric productivity (Pv)** of about 10/15/20 g/L or more" (claims 33–35) | Productivity recited as a method **result limitation** — accumulative Pv, i.e., cumulative mass harvested per liter over the run, not final batch titer | Only meaningful under continuous harvest; in a batch process accumulative Pv = final titer | Weak — WuXiUI quotes **titers** (18 g/L [C15]; 25 g/L [C13]; 24.5 g/L [C14]); these are batch titers, not the claim's accumulative-Pv framing | **Yes** — WuXiUP metrics are accumulative by construction (105 g/L/20 days [C22]; "5–15X greater productivity" [C21]) |

### 1.3 Teardown conclusions

1. **The bright-line elements are E2–E4**: continuous passage, no bleed, continuous harvest. All three are absent from every company description of WuXiUI [C11][C12][C14][C15] and present in the company description of WuXiUP [C21][C22]. A UI-IPFB fed-batch would not literally infringe/practice claim 1; a continuous WuXiUP run reads on every independent-claim element.
2. **Marketing vs. claim scope**: the free sample's phrase "the patent behind WuXiUI" attributes claim scope to the wrong brand. The patent protects a *continuous* architecture; WuXiUI's marketed value proposition (3–6× fed-batch productivity, "minimum changes to the downstream process" [C11]) is valuable precisely because it **avoids** continuous operation — the opposite design philosophy.
3. **The patent itself confirms the WuXiUP coupling**: dependent claims 36–40 (continuous multi-column capture) mirror WuXiUP's PCC capture [C21] element-for-element, including the 3-column MabSelect PrismA example [C9].
4. **Enforcement-relevant note** [C10]: the WO publication is "Ceased" (PCT phase ended — normal), but national-phase grants are in force (CN111406105B Active; also KR, JP). Any real-world assertion of this family against a competitor's continuous process would run through the granted claims, whose scope is the continuous/no-bleed architecture analyzed above — not fed-batch intensification.
5. **Residual uncertainty (stated, not hidden)**: WuXi may hold separate, unlocated patents covering UI-IPFB specifically; our search found none [C18 negative result]. Absence of a located WuXiUI patent is evidence about our source universe, not proof none exists.

---

## 2. WuXiUI™ vs. WuXiUP™ — the distinction as original synthesis

This comparison exists in no single source; it is assembled here from matrix anchors. It is the correction the free sample needed.

| Dimension | **WuXiUI™** (Ultra-Intensified **Fed-Batch**) | **WuXiUP™** (Ultra-High Productivity **Continuous**) |
|---|---|---|
| Process class | Intermittent-perfusion fed-batch (UI-IPFB) [C11][C12][C14] | Intensified perfusion with continuous harvest [C21] |
| Defining intensification step | N-1 perfusion seed + cell concentration (2–4× in 1.5–3 h) → inoculation at 20–80×10⁶ cells/mL, up to 3.5×10⁸ cells/mL [C12] | Cells retained continuously without bleed; product harvested throughout culture [C21; patent E2–E4] |
| Harvest mode | Batch (final DS yield 70% reported per batch [C15]) | Continuous; "greatly reduce the product residence time" [C21] |
| Downstream coupling | Deliberately unchanged — "minimum changes to the downstream process" [C11]; enhanced batch DSP (50% time reduction, 30–50% materials reduction [C15]) | Continuous direct product capture, multicolumn PCC [C21]; 92% Protein A resin reduction [C22] |
| Headline productivity claim | 3–6× vs traditional fed-batch [C11]; avg 3.5×, up to 35 g/L with MagniCHO [C12] | 5–15× vs traditional fed-batch [C21]; avg 7-fold across >50 molecules [C22] |
| Signature published result | 24.5 g/L Mabcalin bispecific, 16-day UI-IPFB, 6.3× (peer-reviewed, Zhang 2024) [C14] | 105 g/L accumulative over 20 days, fully continuous end-to-end at 50 L [C22] |
| Scale evidence | 2,000 L GMP run completed, 18 g/L, 4× [C15]; marketed scale-out to 12,000 L [C12] | 1,000–2,000 L SUB ≈ 10,000–20,000 L stainless productivity [C21]; >20,000 L commercial capacity at 200–2,000 L [C21] |
| Patent alignment (this analysis §1) | **None found** — no claim element set reads on UI-IPFB [C18 negative result] | **WO2020088180A1** — every independent-claim element matches [§1.2] |
| Third-party naming | Trade press (PR-derived) calls WuXiUI "ultra-intensified fed-batch" [C11 rows] | Third-party academic paper refers to "intensified perfusion modes (WuXiUP process)" [C18 corroborating negative] |

**Synthesis conclusions**

1. The two brands are *complementary*, not synonyms: WuXiUP page itself describes N-1 perfusion seed intensification feeding "regular fed-batch culture" as a *separate, simpler* option [C21] — i.e., the company internally frames the WuXiUI concept as the fallback for clients who do not want full continuous operation.
2. The conflation in the free sample was predictable: both platforms use perfusion hardware (ATF), both quote large fold-improvements, and WuXi marketing discusses them adjacently. But the engineering dividing line — **batch harvest vs. continuous harvest** — is unambiguous in the sources.
3. Evidence-governance consequence for the correction-style report: patent-derived performance figures (9.41×/6.56× [C6][C7], >20 g/L accumulative Pv up to 250 L [C9]) are evidence about **WuXiUP-class** capability, and must not be cited as WuXiUI substantiation. WuXiUI substantiation is: launch PR [C11][C13], platform page [C12], 2,000 L PR [C15], Zhang 2024 [C14], canine case study [C16] — each with the independence caveats in the matrix.

---

## 3. Batch-economics model (WuXiUI 2,000 L GMP reference case)

**Purpose**: derive per-batch and per-year DS output for the disclosed WuXiUI 2,000 L GMP run vs. its conventional fed-batch comparator, and test the internal consistency of the company's 60–80% COGS-reduction claim [C17]. This is an order-of-magnitude consistency model, not a cost audit. **The 18 / 24.5 / 25 g/L figures are kept strictly distinct** (see §3.5).

### 3.1 Inputs (every value anchored or labeled)

| Input | Value | Anchor |
|---|---|---|
| Bioreactor working volume, V | 2,000 L | [C15] |
| WuXiUI titer at 2,000 L GMP, t_UI | 18 g/L | [C15] |
| Reported productivity multiple | 4× vs conventional fed-batch | [C15] |
| Implied TFB comparator titer, t_TFB | 18 / 4 = **4.5 g/L** (derived from the 4× claim) | [C15] + derivation D1 (§4) |
| DS yield (WuXiUI run) | 70% | [C15] |
| Typical culture duration | 14 days | [C11] |
| Batch turnaround (harvest, CIP/SIP-free changeover for SUB, setup) | 5 days (range 3–7 tested) | **[A1] assumption** — no source discloses turnaround |
| TFB DS yield (comparator) | 70% (set equal to WuXiUI for conservatism) | **[A2] assumption** — company reports 70% only for the WuXiUI run [C15] |
| Operating days per year | 365 | **[A3] assumption** (continuous campaign availability; maintenance not disclosed) |
| DSP: processing time −50%; materials/consumables −30–50% | as reported | [C15] |
| Company COGS claim | 60–80% reduction vs TFB in SUBs | [C17]; Zhang 2024 models up to 71% for the Mabcalin UI-IPFB case [C14] |

### 3.2 Per-batch arithmetic

- WuXiUI crude harvest mass/batch = 18 g/L × 2,000 L = **36,000 g = 36 kg**
- WuXiUI DS/batch = 36 kg × 70% = **25.2 kg DS/batch**
- TFB crude harvest mass/batch = 4.5 g/L × 2,000 L = **9 kg** [D1]
- TFB DS/batch = 9 kg × 70% = **6.3 kg DS/batch** [A2]
- Mass ratio per batch = 25.2 / 6.3 = **4.0×** (recovers the reported multiple — consistency check passed)

### 3.3 Annualized throughput (single 2,000 L train)

Cycle time = 14 d culture + turnaround. Batches/year = 365 / cycle; annual DS = batches × 25.2 kg.

| Turnaround [A1] | Cycle | Batches/year | WuXiUI DS/year | TFB DS/year (same cycle) |
|---|---|---|---|---|
| 3 d | 17 d | 21.5 | ~541 kg | ~135 kg |
| **5 d (base)** | **19 d** | **19.2** | **~484 kg** | **~121 kg** |
| 7 d | 21 d | 17.4 | ~438 kg | ~110 kg |

Read: one 2,000 L WuXiUI train delivers roughly **0.44–0.54 tonnes DS/year** under these assumptions; the marketed 12,000 L scale-out (6 × 2,000 L) [C12] would, at equal titer and yield [A4 assumption: linear scale-out, consistent with company's "readily scalable" claim C12], deliver ~**2.9 t/year** per block.

### 3.4 COGS consistency check (not an independent COGS estimate)

Per-kg cost decomposition for a SUB train ≈ (fixed facility + labor + batch consumables) / annual kg + DSP variable costs.

- Upstream/facility term: per-batch costs approximately constant between WuXiUI and TFB [A5 assumption: same suite, same headcount, media cost increase from intensification not disclosed and excluded]; 4× kg/batch → **~75% reduction** in the per-kg facility+batch term.
- DSP term: 50% time reduction and 30–50% materials reduction [C15] → further per-kg reduction on the DSP share.
- Result: a 60–80% total COGS reduction [C17] is **internally consistent** with the disclosed 4× mass gain plus the disclosed DSP savings, provided intensification does not add undisclosed per-batch costs that consume >15–20 points of the facility-term saving. Zhang 2024's peer-reviewed 71% figure [C14] sits inside the claimed band and is the only independently reviewed number in this model.
- **Explicit non-finding**: no public cost model exists [matrix negative result #6]; [A1]–[A5] are this report's assumptions, and the 60–80% figure remains a company estimate.

### 3.5 The three titer figures — kept distinct (anti-conflation register)

| Figure | What it actually is | Anchor |
|---|---|---|
| **18 g/L** | WuXiUI **2,000 L GMP** run titer (4× vs TFB), batch harvest | [C15] |
| **24.5 g/L** | **Mabcalin™ bispecific** (Pieris molecule class), 16-day UI-IPFB development run, peer-reviewed; 6.3× over its 3.9 g/L TFB baseline | [C14] |
| **25 g/L** | WuXiUI **launch-PR example**, unnamed bispecific, 14 days, 5×; PR-only | [C13] |
| (contrast) **105 g/L** | **WuXiUP** accumulative output over 20 days at 50 L continuous — *not a batch titer, not WuXiUI* | [C22] |

No source states the 24.5 g/L and 25 g/L figures refer to the same molecule; the model uses only the 18 g/L figure, because it is the only one tied to a GMP manufacturing scale.

---

## 4. Assumption and derivation register

| ID | Statement | Basis |
|---|---|---|
| D1 | TFB comparator titer = 4.5 g/L | Derived: 18 g/L ÷ reported 4× [C15]. Cross-check: the canine case study's pre-WuXiUI commercial cell line was "~4.5 g/L" [C16] — coincidentally identical, strengthening plausibility, but not used as the anchor |
| A1 | Batch turnaround 5 d (range 3–7 d) | Unsourced; sensitivity shown in §3.3 |
| A2 | TFB DS yield = WuXiUI DS yield = 70% | Conservative equal-yield assumption; company reports 70% for WuXiUI only [C15] |
| A3 | 365 operating days/year | Idealized availability; no maintenance data disclosed |
| A4 | Linear scale-out to 6 × 2,000 L | Follows company's "readily scalable to 2000 L – 12,000 L" marketing [C12]; not independently demonstrated |
| A5 | Per-batch fixed costs equal between WuXiUI and TFB; intensification media costs excluded | Simplification for the consistency check in §3.4 only |

## 5. Limitations

1. WuXiUP↔patent mapping is architectural and textual (claim elements vs. company self-description); no company document explicitly says "WO2020088180A1 covers WuXiUP" — the linkage is ours, marked as original analysis. The WuXiUI↔patent *non*-linkage is additionally supported by a recorded negative result [C18].
2. All WuXiUI performance numbers originate from the company or its co-authored paper; independence caveats per matrix rows C11–C17 apply. The 2,000 L run is company-announced only.
3. The economics model tests internal consistency of company claims; it cannot validate them. Turnaround, yields, and cost splits are labeled assumptions.
4. Patent legal-status reading ("Ceased" = PCT phase end, grants in force) is bibliographic analysis from register records [C10], not a freedom-to-operate opinion.
