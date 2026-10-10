const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const handlers = {};
const removed = [];
const fetched = [];
const cached = [];
const context = {
  URL, console,
  self: {
    location: {origin: 'https://cognito.test'},
    addEventListener: (name, fn) => handlers[name] = fn,
    skipWaiting: async () => {}, clients: {claim: async () => {}}
  },
  caches: {
    keys: async () => ['ulc-icam-v1.0.1', 'unrelated-app', 'ulc-icam-public-v2'],
    delete: async name => removed.push(name),
    open: async () => ({addAll: async urls => cached.push(...urls)}),
    match: async request => ({offline: typeof request === 'string'})
  },
  fetch: async request => {fetched.push(request.url); return {online: true};}
};
vm.runInNewContext(fs.readFileSync('static/sw.js', 'utf8'), context);
(async () => {
  await new Promise(resolve => handlers.install({waitUntil: p => p.then(resolve)}));
  assert(cached.includes('/offline.html'));
  assert(!cached.includes('/dashboard'));
  await new Promise(resolve => handlers.activate({waitUntil: p => p.then(resolve)}));
  assert.deepEqual(removed, ['ulc-icam-v1.0.1']);
  let promise;
  const request = {url: 'https://cognito.test/student/my_grades', method: 'GET', mode: 'navigate'};
  handlers.fetch({request, respondWith: p => promise = p});
  assert.equal((await promise).online, true);
  assert.deepEqual(fetched, [request.url]);
  promise = null;
  handlers.fetch({request: {...request, method: 'POST'}, respondWith: p => promise = p});
  assert.equal(promise, null);
  context.fetch = async () => {throw Error('offline');};
  handlers.fetch({request, respondWith: p => promise = p});
  assert.equal((await promise).offline, true);
  console.log('Service worker: 7 assertions passed');
})().catch(error => {console.error(error); process.exitCode = 1;});
