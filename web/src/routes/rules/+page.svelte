<script>
	// The published rulebook, rendered at build time from rules/galewick-program-rules.md
	// by scripts/build_site_data.py. The Markdown file is the source; this page only shows it.
	import rules from '$lib/data/rules.html?raw';
</script>

<svelte:head>
	<title>Galewick program rules — Payout Math — Lailara LLC</title>
	<meta name="description" content="The published 2025 program rules Payout Math validates every Galewick payout against." />
	<link rel="canonical" href="https://payoutmath.lailarallc.com/rules" />
</svelte:head>

<div class="lailara-container">
	<p class="back"><a href="/">← Back to Payout Math</a> · <a href="/rules/galewick-program-rules.md" data-sveltekit-reload>Plain-text version</a></p>
	<article class="rules">
		{@html rules}
	</article>
</div>

<style>
	.back {
		font-size: 15px;
		margin: 0 0 24px;
	}
	.back a,
	.rules :global(a) {
		color: var(--ll-chicago-20);
	}
	.rules {
		max-width: var(--ll-body-max-width-wide);
	}
	.rules :global(h1) {
		font-family: var(--ll-serif);
		font-size: 28px;
		line-height: 1.25;
		color: var(--ll-london-5);
		margin: 0 0 16px;
	}
	.rules :global(h2) {
		font-family: var(--ll-serif);
		font-size: 22px;
		color: var(--ll-london-5);
		margin: 48px 0 12px;
		padding-top: 24px;
		border-top: 1px solid var(--ll-london-85);
		scroll-margin-top: calc(var(--ll-nav-height) + 16px);
	}
	.rules :global(h3) {
		font-family: var(--ll-sans);
		font-size: 17px;
		font-weight: 600;
		color: var(--ll-london-5);
		margin: 28px 0 8px;
		scroll-margin-top: calc(var(--ll-nav-height) + 16px);
	}
	.rules :global(p),
	.rules :global(li) {
		font-size: 17px;
		line-height: 1.6;
		color: var(--ll-london-20);
		max-width: var(--ll-content-measure);
	}
	.rules :global(blockquote) {
		margin: 16px 0;
		padding: 4px 0 4px 16px;
		border-left: 3px solid var(--ll-london-85);
	}
	.rules :global(blockquote p) {
		font-size: 15px;
		color: var(--ll-london-35);
	}
	.rules :global(code) {
		font-size: 14px;
		background: var(--ll-london-95);
		padding: 1px 4px;
		border-radius: var(--ll-radius);
	}
	.rules :global(hr) {
		border: 0;
		border-top: 1px solid var(--ll-london-85);
		margin: 40px 0;
	}
	.rules :global(.table-wrap) {
		overflow-x: auto;
		margin: 16px 0 24px;
	}
	.rules :global(table) {
		border-collapse: collapse;
		font-size: 14px;
		min-width: 100%;
	}
	.rules :global(th) {
		text-align: left;
		font-weight: 600;
		color: var(--ll-london-5);
		border-bottom: 1px solid var(--ll-london-20);
		padding: 8px 12px 8px 0;
	}
	.rules :global(td) {
		border-bottom: 1px solid var(--ll-london-85);
		padding: 8px 12px 8px 0;
		vertical-align: top;
		color: var(--ll-london-20);
	}
	@media (max-width: 640px) {
		.rules :global(p),
		.rules :global(li) {
			font-size: 15px;
		}
		.rules :global(h1) {
			font-size: 24px;
		}
		.rules :global(h2) {
			font-size: 18px;
		}
	}
</style>
