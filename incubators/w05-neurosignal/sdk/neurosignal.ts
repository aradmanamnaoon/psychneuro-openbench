/** Lightweight no-dependency TypeScript client for private local, versioned synthetic API. */
export interface DemoRequest {
  seed: number;
  samples: number;
  chunk_size: number;
  idempotency_key: string;
}
export interface DemoResult {
  contract_version: '1.0';
  synthetic_only: true;
  source_sha256: string;
  spectrum_sha256: string;
  dominant_frequency_hz: number;
  stream_oracle_max_abs_error_volts: number;
  disclaimer: string;
}
export interface JobResponse {
  id: string;
  status: 'queued'|'running'|'failed'|'succeeded'|'cancelled';
  revision: number;
}
export class NeuroSignalClient {
  constructor(private readonly origin: string, private readonly token: string,
              private readonly tenant: string) {
    if (!/^https?:\/\//.test(origin) || !tenant || !token) throw new Error('Invalid private client configuration');
  }
  async demo(req: DemoRequest): Promise<DemoResult> {
    return this.request<DemoResult>('/v1/demo', 'POST', req);
  }
  async submit(req: DemoRequest): Promise<JobResponse> {
    return this.request<JobResponse>('/v1/jobs', 'POST', req);
  }
  async status(jobId: string): Promise<JobResponse> {
    if (!/^[a-f0-9]{32}$/.test(jobId)) throw new Error('Invalid job ID');
    return this.request<JobResponse>(`/v1/jobs/${jobId}`, 'GET');
  }
  private async request<T>(path: string, method: 'GET'|'POST', body?: DemoRequest): Promise<T> {
    const response = await fetch(new URL(path, this.origin), {
      method, cache: 'no-store',
      headers: {'Authorization': `Bearer ${this.token}`, 'X-Tenant': this.tenant,
                'Content-Type': 'application/json'},
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}: ${await response.text()}`);
    return await response.json() as T;
  }
}
