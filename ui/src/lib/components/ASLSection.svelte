<script lang="ts">
	import type { AslConfig } from '../../client';

	interface Props {
		config: AslConfig;
		disabled: boolean;
	}

	let { config = $bindable(), disabled }: Props = $props();
</script>

<div class="grid gap-4">
	<div class="grid grid-cols-2 gap-4">
		<div>
			<label for="asl-node" class="mb-1 block text-sm font-medium text-gray-700">Node Number</label>
			<input
				id="asl-node"
				type="text"
				bind:value={config.node_number}
				{disabled}
				placeholder="Enter node number"
				class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-400 focus:outline-none disabled:bg-gray-100"
			/>
		</div>

		<div>
			<label for="asl-callsign" class="mb-1 block text-sm font-medium text-gray-700">Callsign</label
			>
			<input
				id="asl-callsign"
				type="text"
				bind:value={config.callsign}
				{disabled}
				placeholder="Enter callsign"
				class="w-full rounded-lg border border-gray-300 px-3 py-2 uppercase focus:ring-2 focus:ring-blue-400 focus:outline-none disabled:bg-gray-100"
			/>
		</div>
	</div>

	<div class="grid grid-cols-2 gap-4">
		<div>
			<label for="asl-node-password" class="mb-1 block text-sm font-medium text-gray-700"
				>Node Password</label
			>
			<input
				id="asl-node-password"
				type="text"
				bind:value={config.node_password}
				{disabled}
				placeholder="Enter node password"
				class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-400 focus:outline-none disabled:bg-gray-100"
			/>
		</div>

		<div>
			<label for="asl-login-password" class="mb-1 block text-sm font-medium text-gray-700"
				>Login Password</label
			>
			<input
				id="asl-login-password"
				type="text"
				bind:value={config.login_password}
				{disabled}
				placeholder="Enter login password"
				class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-400 focus:outline-none disabled:bg-gray-100"
			/>
		</div>
	</div>
</div>
