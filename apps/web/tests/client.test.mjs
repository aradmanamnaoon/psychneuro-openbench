import test from 'node:test';
import assert from 'node:assert/strict';
import { W04Client, W04ApiError } from '../dist/client.js';

const hex = 'a'.repeat(64);
const token = 'private-test-token-never-logged';

function withFetch(stub, testFn) {
  const original = globalThis.fetch;
  globalThis.fetch = stub;
  return Promise.resolve().then(testFn).finally(() => { globalThis.fetch = original; });
}

test('origin policy blocks credentials, off-loopback cleartext, path and browser cross-origin', () => {
  for (const origin of [
    'http://external.example', 'ftp://example.org', 'https://user:pass@example.org',
    'https://example.org/private', 'https://example.org?token=abc',
    'https://example.org/#secret',
  ]) {
    assert.throws(() => new W04Client(origin, () => token), W04ApiError, origin);
  }
  assert.doesNotThrow(() => new W04Client('http://127.0.0.1:18080', () => token));
  assert.doesNotThrow(() => new W04Client('https://api.example.org', () => token));
  const original = globalThis.window;
  try {
    globalThis.window = {location: {origin: 'https://other.example'}};
    assert.throws(() => new W04Client('https://api.example.org', () => token),
      error => error instanceof W04ApiError && error.code === 'W04_CROSS_ORIGIN');
    assert.doesNotThrow(() => new W04Client('https://other.example', () => token));
  } finally {
    if (original === undefined) delete globalThis.window;
    else globalThis.window = original;
  }
});

test('GET uses no-store, omits browser credentials and passes token only as a header', async () => {
  let calls = 0;
  await withFetch(async (url, opts) => {
    calls++;
    assert.equal(url.toString(), `http://127.0.0.1:18080/w04/v2/runs/${hex}`);
    assert.equal(opts.headers['X-Internal-Token'], token);
    assert.equal(opts.method, 'GET');
    assert.equal(opts.credentials, 'omit');
    assert.equal(opts.redirect, 'error');
    assert.equal(opts.cache, 'no-store');
    assert.doesNotMatch(url.toString(), /token/);
    return {ok: true, json: async () => ({run_id: hex})};
  }, async () => {
    assert.deepEqual(await new W04Client('http://127.0.0.1:18080', () => token).getRun(hex), {run_id: hex});
  });
  assert.equal(calls, 1);
});

test('POST sends JSON without URL secrets or retries', async () => {
  const body = {generator_seed: 73, split_seed: 42, n_participants: 36, trials_per_participant: 12};
  let calls = 0;
  await withFetch(async (url, opts) => {
    calls++;
    assert.equal(url.pathname, '/w04/v2/runs');
    assert.equal(opts.method, 'POST');
    assert.equal(opts.headers['Content-Type'], 'application/json');
    assert.deepEqual(JSON.parse(opts.body), body);
    return {ok: true, json: async () => ({run_id: hex})};
  }, async () => {
    await new W04Client('https://api.example.org', () => token).createRun(body);
  });
  assert.equal(calls, 1);
});

test('invalid ids and missing token fail before network request', async () => {
  await withFetch(() => { throw new Error('Network must not be invoked'); }, async () => {
    const client = new W04Client('https://api.example.org', () => token);
    for (const invalid of ['../etc/passwd', 'A'.repeat(64), 'aa', 'a'.repeat(63)]) {
      assert.throws(() => client.getRun(invalid), error =>
        error instanceof W04ApiError && error.code === 'W04_INVALID');
    }
    await assert.rejects(new W04Client('https://api.example.org', () => '').getRun(hex),
      error => error instanceof W04ApiError && error.code === 'W04_NO_TOKEN');
  });
});

test('server detail is never surfaced; only allowlisted machine errors survive', async () => {
  for (const [detail, expected] of [
    [{code: 'W04_FORBIDDEN', message: `secret ${token}`}, 'W04_FORBIDDEN'],
    [{code: 'RAW_UPSTREAM_TOKEN', message: token}, 'W04_HTTP_403'],
    ['trace with secret', 'W04_HTTP_403'],
  ]) {
    await withFetch(async () => ({ok: false, status: 403, json: async () => ({detail})}), async () => {
      await assert.rejects(new W04Client('https://api.example.org', () => token).getRun(hex), error => {
        assert.equal(error.code, expected);
        assert.equal(error.message, 'Private API request denied');
        assert.doesNotMatch(error.message, /secret|trace|token/);
        return true;
      });
    });
  }
});

test('worker client submits canonical job contract, without implicit retries', async () => {
  const request = {schema_version: 'w04-job-submit-5', idempotency_key: 'safe-retry-73',
    experiment: {generator_seed: 73, split_seed: 42, n_participants: 36, trials_per_participant: 12}};
  let calls = 0;
  await withFetch(async (url, opts) => {
    calls++;
    assert.equal(url.pathname, '/w04/v3/jobs');
    assert.equal(opts.method, 'POST');
    assert.equal(opts.credentials, 'omit');
    assert.equal(opts.headers['X-Internal-Token'], token);
    assert.deepEqual(JSON.parse(opts.body), request);
    assert.doesNotMatch(url.toString(), /safe-retry|token/);
    return {ok: true, json: async () => ({schema_version: 'w04-job-2', id: hex, state: 'queued'})};
  }, async () => {
    assert.equal((await new W04Client('https://api.example.org', () => token).enqueueJob(request)).state, 'queued');
  });
  assert.equal(calls, 1);
});

test('worker control endpoints are bounded and invalid idempotency fails before fetch', async () => {
  const calls = [];
  const client = new W04Client('https://api.example.org', () => token);
  await withFetch(async (url, opts) => {
    calls.push([url.pathname, opts.method]);
    return {ok: true, json: async () => ({id: hex, state: 'cancelled'})};
  }, async () => {
    await client.getJob(hex);
    await client.cancelJob(hex);
    await client.resumeJob(hex);
    await client.getWorkerReceipt(hex);
    assert.throws(() => client.getWorkerReceipt('../evil'), W04ApiError);
    assert.throws(() => client.enqueueJob({schema_version:'w04-job-submit-5',
      idempotency_key:'../../etc', experiment: {}}), W04ApiError);
  });
  assert.deepEqual(calls, [
    ['/w04/v3/jobs/' + hex, 'GET'],
    ['/w04/v3/jobs/' + hex + '/cancel', 'POST'],
    ['/w04/v3/jobs/' + hex + '/resume', 'POST'],
    ['/w04/v3/jobs/' + hex + '/receipt', 'GET'],
  ]);
});
