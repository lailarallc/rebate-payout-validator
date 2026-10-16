<script>
	// Lailara brand frame (vendored lailara-frame.css v1.5.1). Header + main + dark footer.
	let { children } = $props();
</script>

<div class="lailara-page">
	<header class="lailara-header">
		<nav class="lailara-nav-inner">
			<a href="https://lailarallc.com" class="lailara-wordmark" target="_blank" rel="noopener">Lailara LLC</a>
			<span class="lailara-tool-name">Payout Math</span>
		</nav>
	</header>

	<main class="lailara-main">
		{@render children()}
	</main>

	<footer class="lailara-footer">
		<div class="lailara-footer-inner">
			<p>Built by <a href="https://lailarallc.com" target="_blank" rel="noopener">Lailara LLC</a> — data hygiene and analytics consulting for specialty food brands scaling into national retail.</p>
			<p class="lailara-footer-note">
				Galewick Climate Systems is invented. Every claim, contractor, distributor, and rule on this site is synthetic; the method is real.
			</p>
		</div>
	</footer>
</div>
