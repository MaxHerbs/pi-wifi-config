<script lang="ts">
	import type { FavouriteItem } from '../../client';

	interface Props {
		items: FavouriteItem[];
		disabled: boolean;
	}

	let { items = $bindable(), disabled }: Props = $props();

	function updateItem(index: number, field: 'name' | 'node_number', value: string) {
		items[index] = { ...items[index], [field]: value };
	}
</script>

<div class="grid gap-3">
	{#each items as item, index (index)}
		<div class="grid grid-cols-2 gap-3">
			<div>
				<label for="fav-name-{index}" class="mb-1 block text-sm font-medium text-gray-700">
					Name {index + 1}
				</label>
				<input
					id="fav-name-{index}"
					type="text"
					value={item.name}
					oninput={(e) => updateItem(index, 'name', e.currentTarget.value)}
					{disabled}
					placeholder="Favourite name"
					class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-400 focus:outline-none disabled:bg-gray-100"
				/>
			</div>
			<div>
				<label for="fav-node-{index}" class="mb-1 block text-sm font-medium text-gray-700">
					Node Number
				</label>
				<input
					id="fav-node-{index}"
					type="text"
					value={item.node_number}
					oninput={(e) => updateItem(index, 'node_number', e.currentTarget.value)}
					{disabled}
					placeholder="Node number"
					class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-400 focus:outline-none disabled:bg-gray-100"
				/>
			</div>
		</div>
	{/each}
</div>
