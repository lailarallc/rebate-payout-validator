<script>
	// Every number on this page is computed from the build artifact (summary.json /
	// flagged.json). None is typed by hand.
	import S from '$lib/data/summary.json';
	import { onMount } from 'svelte';

	const v = S.verdict;
	const cls = S.classes;
	const byClass = Object.fromEntries(cls.map((c) => [c.class, c]));

	// ---------------------------------------------------------------- formatting
	const nf = new Intl.NumberFormat('en-US');
	const dollars = (c) => '$' + nf.format(Math.round(Math.abs(c) / 100));
	const cents = (c) =>
		(c < 0 ? '−' : '') +
		'$' +
		new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(Math.abs(c) / 100);
	const signed = (c) => (c > 0 ? '+' : c < 0 ? '−' : '') + cents(Math.abs(c)).replace('−', '');
	const millions = (c) => (c >= 1e8 ? '$' + (c / 1e8).toFixed(2) + ' million' : dollars(c));
	const compact = (c) => {
		const d = Math.abs(c) / 100;
		if (d >= 1e6) return '$' + (d / 1e6).toFixed(1) + 'M';
		if (d >= 1e3) return '$' + Math.round(d / 1e3) + 'K';
		return '$' + Math.round(d);
	};
	const pct = (a, b) => ((100 * a) / b).toFixed(1) + '%';
	const count = (n) => nf.format(n);

	// rule number -> rulebook anchor
	const SECTION = {
		A1: 'a1-who-can-earn', A2: 'a2-what-earns-and-how-much', A3: 'a3-when-the-install-must-happen',
		A4: 'a4-when-the-claim-must-be-filed', A5: 'a5-what-documentation-is-required',
		A6: 'a6-one-bonus-per-unit', A7: 'a7-substitutions', A8: 'a8-reduced-payment-for-late-documentation',
		A9: 'a9-paying-earned-bonuses', B3: 'b3-qualifying-volume', B4: 'b4-tiers-and-rates', B5: 'b5-growth-bonus'
	};
	const ruleHref = (rule) => '/rules#' + (SECTION[rule.slice(0, 2)] ?? '');

	// ---------------------------------------------------------------- verdict charts
	function breakdown(field) {
		const shown = cls.filter((c) => c.shown && c[field] > 0).sort((a, b) => b[field] - a[field]);
		const other = cls.filter((c) => !c.shown && c[field] > 0);
		const rows = shown.map((c) => ({ label: c.label, rule: c.rule, value: c[field], n: c.primary_count }));
		if (other.length)
			rows.push({
				label: 'Other (rules with fewer than ' + S.min_display + ' decisions)',
				rule: other.map((c) => c.rule).join(', '),
				value: other.reduce((s, c) => s + c[field], 0),
				n: other.reduce((s, c) => s + c.primary_count, 0)
			});
		const max = Math.max(...rows.map((r) => r.value));
		return rows.map((r) => ({ ...r, w: (100 * r.value) / max }));
	}
	const overRows = breakdown('over_cents');
	const underRows = breakdown('under_cents');

	const fam = S.families;
	const paidClaims = S.universe.paid_claims;
	const rebateShare = pct(fam.tier.paid_cents, v.approved_cents);

	// ---------------------------------------------------------------- program view
	const groups = [
		{ key: 'submitted', title: 'Submitted by members, approved by Galewick', note: 'The claim itself broke a rule, and the processor paid it anyway.' },
		{ key: 'calculated', title: "Calculated by Galewick", note: "The member did nothing wrong; Galewick's own arithmetic or decision was off." }
	].map((g) => {
		const rows = cls.filter((c) => c.origin === g.key);
		return {
			...g,
			rows: rows.filter((c) => c.shown).sort((a, b) => b.over_cents + b.under_cents - (a.over_cents + a.under_cents)),
			other: rows.filter((c) => !c.shown),
			over: rows.reduce((s, c) => s + c.over_cents, 0),
			under: rows.reduce((s, c) => s + c.under_cents, 0),
			records: rows.reduce((s, c) => s + c.primary_count, 0)
		};
	});
	const sub = groups[0];
	const calc = groups[1];

	// ---------------------------------------------------------------- claims view
	let flagged = $state([]);
	let loaded = $state(false);
	let failed = $state(false);
	let program = $state('all');
	let direction = $state('all');
	let klass = $state('all');
	let query = $state('');
	let page = $state(0);
	let open = $state(null);
	const PAGE = 25;

	onMount(async () => {
		try {
			const r = await fetch('/data/flagged.json');
			flagged = await r.json();
			loaded = true;
		} catch (e) {
			failed = true;
		}
	});

	const filtered = $derived(
		flagged.filter(
			(f) =>
				(program === 'all' || f.t === program) &&
				(direction === 'all' || (direction === 'over' ? f.d > 0 : f.d < 0)) &&
				(klass === 'all' || f.k.includes(+klass)) &&
				(query === '' ||
					(f.id + ' ' + f.m + ' ' + f.n).toLowerCase().includes(query.trim().toLowerCase()))
		)
	);
	const sorted = $derived([...filtered].sort((a, b) => Math.abs(b.d) - Math.abs(a.d)));
	const pages = $derived(Math.max(1, Math.ceil(sorted.length / PAGE)));
	const rows = $derived(sorted.slice(page * PAGE, page * PAGE + PAGE));
	const fOver = $derived(filtered.filter((f) => f.d > 0).reduce((s, f) => s + f.d, 0));
	const fUnder = $derived(-filtered.filter((f) => f.d < 0).reduce((s, f) => s + f.d, 0));

	function resetPage() {
		page = 0;
		open = null;
	}
</script>

<svelte:head>
	<title>Payout Math — Lailara LLC</title>
</svelte:head>

<div class="lailara-container">
<!-- ============================================================ VERDICT -->
<section class="view" id="verdict" aria-labelledby="verdict-title">
	<div class="ll-column">
		<p class="eyebrow">Payout Math · Galewick Climate Systems · {S.params.program_year} program year</p>
		<h1 id="verdict-title" class="verdict">
			<span class="ll-headline-number">{dollars(v.over_cents)}</span>
			<span class="verdict-line">of {millions(v.approved_cents)} approved for payout should never have been approved.</span>
		</h1>
		<p class="second">
			<span class="ll-headline-number">{dollars(v.under_cents)}</span>
			<span class="verdict-line">was earned under Galewick's own rules and never paid.</span>
		</p>
		<p class="lede">
			Galewick paid {count(paidClaims)} contractor install bonuses and {count(S.universe.statements)} quarterly
			distributor rebates in its {S.params.program_year} program. Payout Math re-derived every one from the
			<a href="/rules">published program rules</a>. {count(v.flagged_records)} payout decisions were wrong:
			{count(fam.spiff.flagged_records)} on install-bonus claims and {count(fam.tier.flagged_records)} on rebate
			statements. Overpayments and underpayments are counted separately and never netted — a contractor
			who was underpaid is not made whole by another contractor's overpayment.
		</p>
	</div>

	<div class="stats">
		<div class="stat">
			<span class="ll-benchmark-value">{count(v.flagged_records)}</span>
			<span class="stat-label">payout decisions that break a rule</span>
		</div>
		<div class="stat">
			<span class="ll-benchmark-value">{count(v.multi_defect_records)}</span>
			<span class="stat-label">of them break more than one — a claim for a substituted model also mismatches its invoice (A5.2)</span>
		</div>
		<div class="stat">
			<span class="ll-benchmark-value">{rebateShare}</span>
			<span class="stat-label">of dollars paid went to distributor rebates — {count(fam.tier.flagged_records)} of {count(S.universe.statements)} statements were wrong</span>
		</div>
	</div>

	<div class="charts">
		{#each [{ title: 'Where the overpayment came from', rows: overRows, total: v.over_cents }, { title: 'Where the underpayment came from', rows: underRows, total: v.under_cents }] as ch}
			<figure class="chart">
				<figcaption class="chart-title">{ch.title}</figcaption>
				<p class="chart-sub">{dollars(ch.total)} by the rule each decision broke first</p>
				<ol class="bars">
					{#each ch.rows as r}
						<li>
							<div class="bar-label"><span>{r.label}</span> <a class="rule" href={ruleHref(r.rule)}>{r.rule}</a></div>
							<svg class="bar" viewBox="0 0 100 14" preserveAspectRatio="none" aria-hidden="true">
								<rect x="0" y="0" width={Math.max(r.w, 0.6)} height="14" rx="0.4" />
							</svg>
							<div class="bar-value">{dollars(r.value)} <span class="muted">· {count(r.n)} {r.n === 1 ? 'decision' : 'decisions'}</span></div>
						</li>
					{/each}
				</ol>
			</figure>
		{/each}
	</div>
	<p class="footnote">
		A decision that breaks several rules is counted once, under the first rule it breaks in a fixed order:
		eligibility, then evidence, then arithmetic. Bars sum to the totals above. Rules with fewer than
		{S.min_display} decisions are grouped as “Other”. Records as of {S.universe.as_of}; {count(S.universe.in_process_claims)}
		claims still inside the {S.params.claim_processing_days}-day processing window are not counted. Received dates are
		business-day intake dates: a claim submitted on a weekend counts as received the next business day.
	</p>
</section>

<!-- ============================================================ CLAIMS -->
<section class="view" id="claims" aria-labelledby="claims-title">
	<div class="ll-column">
		<h2 id="claims-title" class="ll-section-title">The claims</h2>
		<p class="body">
			Every payout decision that breaks a rule, with the rule, the evidence, and the dollars. Underpayments sit in the
			same table with the opposite sign. Each line can be checked by hand against the <a href="/rules">rules</a>.
		</p>
	</div>

	<div class="filters" role="group" aria-label="Filter the claims">
		<label>Program
			<select bind:value={program} onchange={resetPage}>
				<option value="all">Both programs</option>
				<option value="c">Contractor install bonus</option>
				<option value="s">Distributor volume rebate</option>
			</select>
		</label>
		<label>Direction
			<select bind:value={direction} onchange={resetPage}>
				<option value="all">Over- and underpaid</option>
				<option value="over">Overpaid</option>
				<option value="under">Underpaid</option>
			</select>
		</label>
		<label>Rule broken
			<select bind:value={klass} onchange={resetPage}>
				<option value="all">Any rule</option>
				{#each cls as c}
					<option value={String(c.class)}>{c.rule} · {c.label}</option>
				{/each}
			</select>
		</label>
		<label class="search">Member or record
			<input type="search" bind:value={query} oninput={resetPage} placeholder="e.g. A001234 or Supply" />
		</label>
	</div>

	{#if failed}
		<p class="body">The claims list could not be loaded.</p>
	{:else if !loaded}
		<p class="body muted">Loading {count(v.flagged_records)} records…</p>
	{:else}
		<p class="result-line">
			{count(filtered.length)} {filtered.length === 1 ? 'decision' : 'decisions'} ·
			<span class="over">{dollars(fOver)} overpaid</span> ·
			<span class="under">{dollars(fUnder)} underpaid</span>
		</p>
		<div class="table-wrap">
			<table class="claims">
				<thead>
					<tr>
						<th scope="col">Record</th>
						<th scope="col">Member</th>
						<th scope="col">Rule broken</th>
						<th scope="col" class="num">Paid</th>
						<th scope="col" class="num">Earned</th>
						<th scope="col" class="num">Difference</th>
					</tr>
				</thead>
				<tbody>
					{#each rows as f (f.id)}
						{@const c = byClass[f.pk]}
						<tr class="row" class:open={open === f.id}>
							<td><button class="rec" aria-expanded={open === f.id} onclick={() => (open = open === f.id ? null : f.id)}>{f.id}</button></td>
							<td><span class="member">{f.n}</span> <span class="muted">{f.m}</span></td>
							<td>
								<a class="rule" href={ruleHref(c.rule)}>{c.rule}</a> {c.label}
								{#if f.k.length > 1}<span class="more">+{f.k.length - 1} more</span>{/if}
							</td>
							<td class="num">{cents(f.p)}</td>
							<td class="num">{cents(f.e)}</td>
							<td class="num" class:over={f.d > 0} class:under={f.d < 0}>{signed(f.d)}</td>
						</tr>
						{#if open === f.id}
							<tr class="evidence-row">
								<td colspan="6">
									<ul class="evidence">
										{#each f.k as k, i}
											<li><a class="rule" href={ruleHref(byClass[k].rule)}>{byClass[k].rule}</a> <strong>{byClass[k].label}.</strong> {f.ev[i]}</li>
										{/each}
									</ul>
								</td>
							</tr>
						{/if}
					{/each}
				</tbody>
			</table>
		</div>
		<div class="pager">
			<button onclick={() => { page = Math.max(0, page - 1); open = null; }} disabled={page === 0}>Previous</button>
			<span>Page {page + 1} of {pages}</span>
			<button onclick={() => { page = Math.min(pages - 1, page + 1); open = null; }} disabled={page >= pages - 1}>Next</button>
		</div>
		<p class="footnote">Sorted by size of the difference. Select a record number to see every rule it breaks and the evidence for each.</p>
	{/if}
</section>

<!-- ============================================================ PROGRAM -->
<section class="view" id="program" aria-labelledby="program-title">
	<div class="ll-column">
		<h2 id="program-title" class="ll-section-title">The program</h2>
		<p class="body">
			{pct(sub.records, v.flagged_records)} of wrong decisions started with something a member submitted. They
			account for {dollars(sub.over + sub.under)} of the {dollars(v.over_cents + v.under_cents)} paid wrongly in
			either direction. The other {dollars(calc.over + calc.under)} — {pct(calc.over + calc.under, v.over_cents + v.under_cents)}
			— came from Galewick's own calculations. A member-submitted error averaged {dollars((sub.over + sub.under) / sub.records)};
			a Galewick calculation error averaged {dollars((calc.over + calc.under) / calc.records)}, and
			{dollars(fam.tier.over_cents + fam.tier.under_cents)} of the total sits on {count(fam.tier.flagged_records)} distributor
			rebate statements.
		</p>
	</div>

	{#each groups as g}
		<h3 class="group-title">{g.title}</h3>
		<p class="group-note">{g.note} {count(g.records)} decisions · {dollars(g.over)} overpaid · {dollars(g.under)} underpaid.</p>
		<div class="table-wrap">
			<table class="program">
				<thead>
					<tr>
						<th scope="col">Rule</th>
						<th scope="col">What went wrong</th>
						<th scope="col" class="num">Decisions (first rule broken)</th>
						<th scope="col" class="num">Decisions (rule broken at all)</th>
						<th scope="col" class="num">Overpaid</th>
						<th scope="col" class="num">Underpaid</th>
					</tr>
				</thead>
				<tbody>
					{#each g.rows as c}
						<tr>
							<td><a class="rule" href={ruleHref(c.rule)}>{c.rule}</a></td>
							<td>{c.label}</td>
							<td class="num">{count(c.primary_count)}</td>
							<td class="num">{count(c.present_count)}</td>
							<td class="num">{c.over_cents ? dollars(c.over_cents) : '—'}</td>
							<td class="num">{c.under_cents ? dollars(c.under_cents) : '—'}</td>
						</tr>
					{/each}
					{#if g.other.length}
						<tr class="other">
							<td>{g.other.map((c) => c.rule).join(', ')}</td>
							<td>Other (fewer than {S.min_display} decisions each)</td>
							<td class="num">{count(g.other.reduce((s, c) => s + c.primary_count, 0))}</td>
							<td class="num">{count(g.other.reduce((s, c) => s + c.present_count, 0))}</td>
							<td class="num">{dollars(g.other.reduce((s, c) => s + c.over_cents, 0))}</td>
							<td class="num">{dollars(g.other.reduce((s, c) => s + c.under_cents, 0))}</td>
						</tr>
					{/if}
				</tbody>
			</table>
		</div>
	{/each}
	<p class="footnote">
		“First rule broken” counts each decision once and sums to the verdict. “Rule broken at all” is informational:
		a decision that breaks two rules appears in both rows.
	</p>
</section>

<!-- ============================================================ METHOD -->
<section class="view" id="method" aria-labelledby="method-title">
	<div class="ll-column">
		<h2 id="method-title" class="ll-section-title">How this was built</h2>
		<p class="body">
			Galewick Climate Systems is an invented HVAC manufacturer. Its {count(S.universe.claims)} claims and
			{count(S.universe.statements)} rebate statements are synthetic and generated from a fixed seed. The kinds of
			error come from nineteen years of incentive-program operations. How often each one occurs follows a stated
			scale, because no published source breaks claim errors down by type. Each kind of error is seeded at
			exactly its rate times the number of claims or rebate statements, so the counts repeat by design. Every rule value in the
			<a href="/rules">rulebook</a> is a seeded draw from a range with a stated basis, not a number anyone chose.
		</p>
		<p class="body">
			The validator reads only what Galewick's systems would hold — claims, documents, invoices, credits,
			statements — and the published rules. It never sees which errors were planted, and it finds every one of
			them and nothing else.
		</p>
		{#each S.bounds as b}
			<p class="footnote">
				<strong>{b.result === 'PASS' ? 'Within' : 'Outside'} a published range.</strong>
				{b.what}: {(b.measured_bp / 100).toFixed(1)}%, against {b.low_bp / 100}–{b.high_bp / 100}% reported by {b.source}.
				{#if b.result !== 'PASS'}The error rates were not adjusted to close the gap.{/if}
			</p>
		{/each}
	</div>
</section>
</div>

<style>
	.lede a,
	.body a {
		color: var(--ll-chicago-20);
		text-underline-offset: 2px;
	}
	.lede a:hover,
	.body a:hover {
		color: var(--ll-chicago-10);
	}
	.view {
		padding: 0 0 var(--ll-section-gap);
		margin-bottom: var(--ll-section-gap);
		border-bottom: 1px solid var(--ll-london-85);
	}
	.view:last-of-type {
		border-bottom: 0;
	}
	.eyebrow {
		font-family: var(--ll-sans);
		font-size: 14px;
		font-weight: 600;
		letter-spacing: 0.04em;
		text-transform: uppercase;
		color: var(--ll-red-42);
		margin: 0 0 12px;
	}
	.verdict,
	.second {
		margin: 0;
		font-weight: 400;
	}
	.verdict .ll-headline-number,
	.second .ll-headline-number {
		display: block;
		color: var(--ll-london-5);
	}
	.second {
		margin-top: 24px;
	}
	.verdict-line {
		display: block;
		font-family: var(--ll-serif);
		font-size: 28px;
		line-height: 1.25;
		color: var(--ll-london-5);
		margin-top: 4px;
	}
	.lede,
	.body {
		font-size: 17px;
		line-height: 1.6;
		color: var(--ll-london-20);
		margin: 24px 0 0;
	}
	.muted {
		color: var(--ll-london-35);
	}
	.stats {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 24px;
		margin: 40px 0 0;
		padding: 24px 0;
		border-top: 1px solid var(--ll-london-85);
		border-bottom: 1px solid var(--ll-london-85);
	}
	.stat {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}
	.stat .ll-benchmark-value {
		color: var(--ll-london-5);
	}
	.stat-label {
		font-size: 15px;
		line-height: 1.4;
		color: var(--ll-london-35);
	}
	.charts {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 48px;
		margin-top: 40px;
	}
	.chart {
		margin: 0;
	}
	.chart-title {
		font-family: var(--ll-serif);
		font-size: 22px;
		font-weight: 700;
		line-height: 1.3;
		color: var(--ll-london-5);
	}
	.chart-sub {
		font-size: 14px;
		color: var(--ll-london-35);
		margin: 4px 0 16px;
	}
	.bars {
		list-style: none;
		margin: 0;
		padding: 0;
	}
	.bars li {
		padding: 8px 0;
		border-bottom: 1px solid var(--ll-london-90);
	}
	.bar-label {
		font-size: 14px;
		color: var(--ll-london-20);
		margin-bottom: 4px;
	}
	.bar {
		display: block;
		width: 100%;
		height: 14px;
	}
	.bar rect {
		fill: var(--ll-chicago-20);
	}
	.bar-value {
		font-size: 14px;
		font-weight: 600;
		color: var(--ll-london-5);
		margin-top: 4px;
	}
	.bar-value .muted {
		font-weight: 400;
	}
	.rule {
		font-size: 12px;
		font-weight: 600;
		letter-spacing: 0.02em;
		color: var(--ll-chicago-20);
		text-decoration: none;
		border: 1px solid var(--ll-chicago-85);
		border-radius: var(--ll-radius);
		padding: 0 4px;
		white-space: nowrap;
	}
	.rule:hover {
		background: var(--ll-chicago-95);
	}
	.footnote {
		font-size: 13px;
		font-style: italic;
		line-height: 1.5;
		color: var(--ll-london-35);
		max-width: var(--ll-content-measure);
		margin: 24px 0 0;
	}
	.filters {
		display: flex;
		flex-wrap: wrap;
		gap: 16px;
		margin: 24px 0 16px;
	}
	.filters label {
		display: flex;
		flex-direction: column;
		gap: 4px;
		font-size: 14px;
		color: var(--ll-london-35);
	}
	.filters select,
	.filters input {
		font-family: var(--ll-sans);
		font-size: 15px;
		color: var(--ll-london-5);
		background: var(--ll-paper);
		border: 1px solid var(--ll-london-70);
		border-radius: var(--ll-radius);
		padding: 8px 10px;
		min-width: 200px;
	}
	.filters .search input {
		min-width: 240px;
	}
	.result-line {
		font-size: 15px;
		color: var(--ll-london-20);
		margin: 0 0 8px;
	}
	.table-wrap {
		overflow-x: auto;
	}
	table {
		border-collapse: collapse;
		width: 100%;
		font-size: 14px;
	}
	th {
		text-align: left;
		font-weight: 600;
		color: var(--ll-london-5);
		border-bottom: 1px solid var(--ll-london-20);
		padding: 8px 12px 8px 0;
		vertical-align: bottom;
	}
	td {
		border-bottom: 1px solid var(--ll-london-85);
		padding: 8px 12px 8px 0;
		vertical-align: top;
		color: var(--ll-london-20);
	}
	.num {
		text-align: right;
		font-variant-numeric: tabular-nums;
		white-space: nowrap;
	}
	.over {
		color: var(--ll-tokyo-40, #b82d4a);
	}
	.under {
		color: var(--ll-hk-25);
	}
	td.over,
	td.under {
		font-weight: 600;
	}
	.rec {
		font: inherit;
		font-variant-numeric: tabular-nums;
		color: var(--ll-chicago-20);
		background: none;
		border: 0;
		padding: 0;
		cursor: pointer;
		text-decoration: underline;
		text-underline-offset: 2px;
	}
	.member {
		color: var(--ll-london-5);
	}
	.more {
		font-size: 12px;
		color: var(--ll-london-35);
		margin-left: 4px;
		white-space: nowrap;
	}
	.row.open td {
		border-bottom-color: transparent;
	}
	.evidence-row td {
		background: var(--ll-london-95);
		padding: 12px;
	}
	.evidence {
		margin: 0;
		padding: 0;
		list-style: none;
		display: grid;
		gap: 6px;
	}
	.pager {
		display: flex;
		align-items: center;
		gap: 16px;
		margin-top: 16px;
		font-size: 14px;
		color: var(--ll-london-35);
	}
	.pager button {
		font-family: var(--ll-sans);
		font-size: 14px;
		font-weight: 600;
		color: var(--ll-chicago-20);
		background: var(--ll-paper);
		border: 1px solid var(--ll-chicago-20);
		border-radius: var(--ll-radius);
		padding: 6px 14px;
		cursor: pointer;
	}
	.pager button:disabled {
		color: var(--ll-london-70);
		border-color: var(--ll-london-70);
		cursor: default;
	}
	.group-title {
		font-family: var(--ll-sans);
		font-size: 17px;
		font-weight: 600;
		color: var(--ll-london-5);
		margin: 40px 0 4px;
	}
	.group-note {
		font-size: 15px;
		color: var(--ll-london-35);
		margin: 0 0 12px;
		max-width: var(--ll-content-measure);
	}
	tr.other td {
		color: var(--ll-london-35);
	}
	button:focus-visible,
	a:focus-visible,
	select:focus-visible,
	input:focus-visible {
		outline: 2px solid var(--ll-chicago-40);
		outline-offset: 2px;
	}
	@media (max-width: 640px) {
		.verdict-line {
			font-size: 22px;
		}
		.lede,
		.body {
			font-size: 15px;
		}
		.stats {
			grid-template-columns: 1fr;
			gap: 16px;
		}
		.charts {
			grid-template-columns: 1fr;
			gap: 40px;
		}
		.chart-title {
			font-size: 18px;
		}
		.filters label,
		.filters select,
		.filters input,
		.filters .search input {
			width: 100%;
			min-width: 0;
		}
		.filters label {
			flex: 1 1 100%;
		}
	}
</style>
