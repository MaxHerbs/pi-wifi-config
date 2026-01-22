<script lang="ts">
	import { onMount } from 'svelte';
	import type {
		FavouriteItem,
		WiFiConfig,
		AslConfig,
		ConfigurationRequest,
		SectionResult
	} from '../client';
	import { defaultGetConfigurationGet, defaultUpdateConfigurationPost } from '../client';
	import ConfigSection from '$lib/components/ConfigSection.svelte';
	import FavouritesSection from '$lib/components/FavouritesSection.svelte';
	import WiFiSection from '$lib/components/WiFiSection.svelte';
	import ASLSection from '$lib/components/ASLSection.svelte';

	// Section enabled states
	let favouritesEnabled = $state(false);
	let wifiEnabled = $state(false);
	let aslEnabled = $state(false);

	// Form data
	let favourites = $state<FavouriteItem[]>([
		{ name: '', node_number: '' },
		{ name: '', node_number: '' },
		{ name: '', node_number: '' },
		{ name: '', node_number: '' },
		{ name: '', node_number: '' },
		{ name: '', node_number: '' }
	]);

	let wifi = $state<WiFiConfig>({
		ssid: '',
		password: '',
		country: 'GB'
	});

	let asl = $state<AslConfig>({
		node_number: '',
		node_password: '',
		callsign: '',
		login_password: ''
	});

	// UI states
	let loading = $state(false);
	let submitting = $state(false);
	let results = $state<Record<string, SectionResult> | null>(null);

	let anyEnabled = $derived(favouritesEnabled || wifiEnabled || aslEnabled);

	onMount(async () => {
		await loadConfiguration();
	});

	async function loadConfiguration() {
		loading = true;
		try {
			const response = await defaultGetConfigurationGet();
			if (response.data) {
				// Load favourites
				if (response.data.favourites?.items) {
					favourites = response.data.favourites.items;
					// Ensure we have 6 items
					while (favourites.length < 6) {
						favourites.push({ name: '', node_number: '' });
					}
				}

				// Load WiFi (password always empty from server)
				if (response.data.wifi) {
					wifi = {
						ssid: response.data.wifi.ssid ?? '',
						password: '',
						country: response.data.wifi.country ?? 'GB'
					};
				}

				// ASL status doesn't have useful data, passwords always empty
			}
		} catch (err) {
			console.error('Failed to load configuration:', err);
		} finally {
			loading = false;
		}
	}

	async function handleSubmit(event: Event) {
		event.preventDefault();
		if (!anyEnabled) return;

		submitting = true;
		results = null;

		const request: ConfigurationRequest = {
			update_favourites: favouritesEnabled,
			update_wifi: wifiEnabled,
			update_asl: aslEnabled
		};

		if (favouritesEnabled) {
			request.favourites = { items: favourites };
		}

		if (wifiEnabled) {
			request.wifi = wifi;
		}

		if (aslEnabled) {
			request.asl = asl;
		}

		try {
			const response = await defaultUpdateConfigurationPost({
				body: request
			});

			if (response.data) {
				results = response.data.results;
			}
		} catch (err) {
			console.error('Failed to update configuration:', err);
			results = {
				error: {
					success: false,
					message: 'Request failed',
					error: String(err)
				}
			};
		} finally {
			submitting = false;
		}
	}
</script>

<main class="min-h-screen bg-gray-100 p-6">
	<div class="mx-auto max-w-2xl">
		<h1 class="mb-8 text-center text-3xl font-bold text-blue-700">G1LRO RLN Z2 Configuration</h1>

		{#if loading}
			<div class="text-center text-gray-600">Loading configuration...</div>
		{:else}
			<form onsubmit={handleSubmit} class="space-y-6">
				<ConfigSection
					title="Favourites"
					enabled={favouritesEnabled}
					onToggle={(v) => (favouritesEnabled = v)}
				>
					<FavouritesSection bind:items={favourites} disabled={!favouritesEnabled} />
				</ConfigSection>

				<ConfigSection title="WiFi Setup" enabled={wifiEnabled} onToggle={(v) => (wifiEnabled = v)}>
					<WiFiSection bind:config={wifi} disabled={!wifiEnabled} />
				</ConfigSection>

				<ConfigSection title="ASL Settings" enabled={aslEnabled} onToggle={(v) => (aslEnabled = v)}>
					<ASLSection bind:config={asl} disabled={!aslEnabled} />
				</ConfigSection>

				<button
					type="submit"
					disabled={!anyEnabled || submitting}
					class="w-full rounded-lg bg-blue-600 px-6 py-3 text-lg font-semibold text-white transition-colors duration-200 hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-400"
				>
					{#if submitting}
						Applying Changes...
					{:else}
						Apply Selected Changes
					{/if}
				</button>
			</form>

			{#if results}
				<div class="mt-6 space-y-3">
					<h2 class="text-lg font-semibold text-gray-800">Results</h2>
					{#each Object.entries(results) as [section, result] (section)}
						<div
							class="rounded-lg border p-4 {result.success
								? 'border-green-200 bg-green-50'
								: 'border-red-200 bg-red-50'}"
						>
							<div class="flex items-center gap-2">
								{#if result.success}
									<span class="text-green-600">&#10003;</span>
								{:else}
									<span class="text-red-600">&#10007;</span>
								{/if}
								<span class="font-medium capitalize">{section}</span>
							</div>
							<p class="mt-1 text-sm text-gray-700">{result.message}</p>
							{#if result.error}
								<p class="mt-1 text-sm text-red-600">{result.error}</p>
							{/if}
						</div>
					{/each}
				</div>
			{/if}
		{/if}
	</div>
</main>
