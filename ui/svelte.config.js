import adapter from '@sveltejs/adapter-static';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter({
			pages: '../server/src/server/build',
			assets: '../server/src/server/build',
			fallback: undefined,
			precompress: false,
			strict: true
		})
	}
};

export default config;
