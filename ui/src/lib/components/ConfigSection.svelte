<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		title: string;
		enabled: boolean;
		children: Snippet;
		onToggle: (enabled: boolean) => void;
	}

	let { title, enabled, children, onToggle }: Props = $props();
</script>

<section
	class="rounded-lg border border-gray-200 bg-white p-6 shadow-sm {enabled ? '' : 'opacity-60'}"
>
	<div class="mb-4 flex items-center gap-3">
		<input
			type="checkbox"
			checked={enabled}
			onchange={(e) => onToggle(e.currentTarget.checked)}
			class="h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
		/>
		<h2 class="text-xl font-semibold text-gray-800">{title}</h2>
	</div>
	<div class={enabled ? '' : 'pointer-events-none'}>
		{@render children()}
	</div>
</section>
