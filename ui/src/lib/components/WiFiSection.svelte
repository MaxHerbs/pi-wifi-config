<script lang="ts">
	import type { WiFiConfig } from '../../client';

	interface Props {
		config: WiFiConfig;
		disabled: boolean;
	}

	let { config = $bindable(), disabled }: Props = $props();

	const countries = [
		{ code: 'GB', name: 'United Kingdom' },
		{ code: 'US', name: 'United States' },
		{ code: 'DE', name: 'Germany' },
		{ code: 'FR', name: 'France' },
		{ code: 'ES', name: 'Spain' },
		{ code: 'IT', name: 'Italy' },
		{ code: 'NL', name: 'Netherlands' },
		{ code: 'BE', name: 'Belgium' },
		{ code: 'AT', name: 'Austria' },
		{ code: 'CH', name: 'Switzerland' },
		{ code: 'IE', name: 'Ireland' },
		{ code: 'AU', name: 'Australia' },
		{ code: 'NZ', name: 'New Zealand' },
		{ code: 'CA', name: 'Canada' },
		{ code: 'JP', name: 'Japan' },
		{ code: 'SE', name: 'Sweden' },
		{ code: 'NO', name: 'Norway' },
		{ code: 'DK', name: 'Denmark' },
		{ code: 'FI', name: 'Finland' },
		{ code: 'PL', name: 'Poland' },
		{ code: 'PT', name: 'Portugal' },
		{ code: 'CZ', name: 'Czech Republic' },
		{ code: 'HU', name: 'Hungary' },
		{ code: 'RO', name: 'Romania' },
		{ code: 'BG', name: 'Bulgaria' },
		{ code: 'GR', name: 'Greece' },
		{ code: 'SK', name: 'Slovakia' },
		{ code: 'SI', name: 'Slovenia' },
		{ code: 'HR', name: 'Croatia' },
		{ code: 'LT', name: 'Lithuania' },
		{ code: 'LV', name: 'Latvia' },
		{ code: 'EE', name: 'Estonia' },
		{ code: 'LU', name: 'Luxembourg' },
		{ code: 'MT', name: 'Malta' },
		{ code: 'CY', name: 'Cyprus' },
		{ code: 'ZA', name: 'South Africa' },
		{ code: 'BR', name: 'Brazil' },
		{ code: 'MX', name: 'Mexico' },
		{ code: 'AR', name: 'Argentina' },
		{ code: 'IN', name: 'India' },
		{ code: 'SG', name: 'Singapore' },
		{ code: 'HK', name: 'Hong Kong' },
		{ code: 'KR', name: 'South Korea' },
		{ code: 'TW', name: 'Taiwan' },
		{ code: 'TH', name: 'Thailand' },
		{ code: 'MY', name: 'Malaysia' },
		{ code: 'PH', name: 'Philippines' },
		{ code: 'ID', name: 'Indonesia' },
		{ code: 'VN', name: 'Vietnam' }
	];
</script>

<div class="grid gap-4">
	<div>
		<label for="wifi-ssid" class="mb-1 block text-sm font-medium text-gray-700"
			>Network Name (SSID)</label
		>
		<input
			id="wifi-ssid"
			type="text"
			bind:value={config.ssid}
			{disabled}
			placeholder="Enter WiFi network name"
			class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-400 focus:outline-none disabled:bg-gray-100"
		/>
	</div>

	<div>
		<label for="wifi-password" class="mb-1 block text-sm font-medium text-gray-700">Password</label>
		<input
			id="wifi-password"
			type="text"
			bind:value={config.password}
			{disabled}
			placeholder="Enter WiFi password"
			class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-400 focus:outline-none disabled:bg-gray-100"
		/>
	</div>

	<div>
		<label for="wifi-country" class="mb-1 block text-sm font-medium text-gray-700"
			>Country Code</label
		>
		<select
			id="wifi-country"
			bind:value={config.country}
			{disabled}
			class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-400 focus:outline-none disabled:bg-gray-100"
		>
			{#each countries as country (country.code)}
				<option value={country.code}>{country.name} ({country.code})</option>
			{/each}
		</select>
	</div>
</div>
