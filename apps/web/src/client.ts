/** Versioned W04 internal API client. No token persistence or implicit retries. */
export type Hex64 = string;
export interface ExperimentRequest {
  generator_seed: number; split_seed: number;
  n_participants: number; trials_per_participant: number;
}
export interface RunResult {
  schema_version: "w03-engine-1"; run_id: Hex64; provenance_root: Hex64;
  source_sha256: Hex64; split_sha256: Hex64;
  rights: "internal-synthetic-only";
  n_train_groups: number; n_test_groups: number;
  outer_balanced_accuracy: number; dummy_outer_balanced_accuracy: number;
  test_balanced_accuracy: number; selected_c: number;
}
export interface Comparison {
  schema_version: "w04-comparison-2"; left: RunResult; right: RunResult;
  balanced_accuracy_difference: number; interpretation: string;
}
export interface SplitSummary {
  schema_version: "w04-split-2"; run_id: Hex64;
  train_groups: number; test_groups: number; split_sha256: Hex64;
  partition: "participant-disjoint-verified-by-W03";
}
export interface ProvenanceNode {
  kind: "source" | "split" | "model" | "benchmark";
  sha256: Hex64; parents: Hex64[]; metadata: Record<string, unknown>;
}
export interface ProvenanceGraph {
  schema_version: "w04-graph-2"; root: Hex64;
  nodes: ProvenanceNode[]; verified: boolean; warning: string;
}
export interface VerifiedArtifact {
  schema_version: "w04-envelope-1"; dataset_id: string;
  run_id: Hex64; provenance_root: Hex64; receipt_sha256: Hex64;
  rights_decision: "internal-aggregate-only"; payload: Record<string, unknown>;
}
export class W04ApiError extends Error {
  constructor(readonly status: number, readonly code: string, message: string) {
    super(message); this.name = "W04ApiError";
  }
}
/** Caller owns token lifetime; never put it in URLs or browser storage. */
export class W04Client {
  constructor(private readonly origin: string, private readonly token: () => string) {}
  private async request<T>(path: string, body?: unknown): Promise<T> {
    const key = this.token();
    if (!key) throw new W04ApiError(0, "W04_NO_TOKEN", "Missing internal operator token");
    const response = await fetch(new URL(path, this.origin), {
      method: body === undefined ? "GET" : "POST", credentials: "omit",
      cache: "no-store", redirect: "error",
      headers: { "X-Internal-Token": key, ...(body === undefined ? {} : { "Content-Type": "application/json" }) },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
    if (!response.ok) {
      // Never mirror response bodies or tokens into logs.
      throw new W04ApiError(response.status, "W04_HTTP_" + response.status, "Private API request denied");
    }
    return await response.json() as T;
  }
  private id(runId: string): string {
    if (!/^[0-9a-f]{64}$/.test(runId)) throw new W04ApiError(0, "W04_INVALID", "Invalid run ID");
    return runId;
  }
  createRun(request: ExperimentRequest): Promise<RunResult> { return this.request("/w04/v2/runs", request); }
  getRun(id: string): Promise<RunResult> { return this.request("/w04/v2/runs/" + this.id(id)); }
  getSplit(id: string): Promise<SplitSummary> { return this.request("/w04/v2/runs/" + this.id(id) + "/split"); }
  getGraph(id: string): Promise<ProvenanceGraph> { return this.request("/w04/v2/runs/" + this.id(id) + "/graph"); }
  compare(left: string, right: string): Promise<Comparison> {
    return this.request("/w04/v2/compare?left=" + this.id(left) + "&right=" + this.id(right));
  }
  exportArtifact(id: string): Promise<VerifiedArtifact> { return this.request("/w04/v2/runs/" + this.id(id) + "/artifact"); }
  verifyArtifact(value: VerifiedArtifact): Promise<{run_id:string;provenance_root:string}> {
    return this.request("/w04/v2/artifacts/verify", value);
  }
  importArtifact(value: VerifiedArtifact): Promise<{run_id:string;provenance_root:string}> {
    return this.request("/w04/v2/artifacts/import", value);
  }
}
