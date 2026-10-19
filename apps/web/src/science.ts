/** Accessible scientific summaries for original fictional-participant runs.
 * Presentation-only; the server remains the authoritative verifier.
 */
export interface AggregateRun {
  readonly run_id: string;
  readonly outer_balanced_accuracy: number;
  readonly dummy_outer_balanced_accuracy: number;
  readonly test_balanced_accuracy: number;
  readonly n_train_groups: number;
  readonly n_test_groups: number;
  readonly split_sha256: string;
  readonly provenance_root: string;
}
export interface ScoreRow { readonly label: string; readonly value: string; readonly meaning: string; }
export interface ComparisonSummary {
  readonly rows: readonly ScoreRow[];
  readonly difference: number;
  readonly caveat: string;
}
const SHA = /^[0-9a-f]{64}$/;
const finiteScore = (value: number): boolean => Number.isFinite(value) && value >= 0 && value <= 1;

export function validateAggregate(run: AggregateRun): void {
  if (!SHA.test(run.run_id) || !SHA.test(run.split_sha256) || !SHA.test(run.provenance_root)) {
    throw new Error('Invalid SHA-256 identifier in aggregate');
  }
  if (![run.outer_balanced_accuracy, run.dummy_outer_balanced_accuracy, run.test_balanced_accuracy].every(finiteScore)) {
    throw new Error('Invalid balanced accuracy');
  }
  if (![run.n_train_groups, run.n_test_groups].every(v => Number.isSafeInteger(v) && v > 0 && v <= 80)) {
    throw new Error('Invalid fictional participant group count');
  }
}
export function compareAggregates(left: AggregateRun, right: AggregateRun): ComparisonSummary {
  validateAggregate(left);
  validateAggregate(right);
  const difference = left.outer_balanced_accuracy - right.outer_balanced_accuracy;
  const rows: ScoreRow[] = [
    {label:'Run A: grouped outer balanced accuracy', value:left.outer_balanced_accuracy.toFixed(3), meaning:'Held-out fictional groups across cross-validation folds'},
    {label:'Run A: same-fold dummy comparator', value:left.dummy_outer_balanced_accuracy.toFixed(3), meaning:'Reference prediction system on the same grouped folds'},
    {label:'Run B: grouped outer balanced accuracy', value:right.outer_balanced_accuracy.toFixed(3), meaning:'Independent fictional experiment; folds may differ'},
    {label:'Run B: same-fold dummy comparator', value:right.dummy_outer_balanced_accuracy.toFixed(3), meaning:'Not a clinical baseline'},
    {label:'Difference A minus B', value:difference.toFixed(3), meaning:'Descriptive difference, not a statistical significance estimate'},
  ];
  const same = left.run_id === right.run_id;
  return {rows, difference, caveat: same
    ? 'Identical run identifiers: this is a self-comparison, not independent replication.'
    : 'These are separate fictional-participant runs. Do not infer a paired effect, confidence interval, diagnostic ability, or population generalization.'};
}

/** Text graph alternative. Metadata is data, never interpreted as HTML. */
export function graphText(nodes: readonly {kind: string; sha256: string; parents: readonly string[]}[]): string[] {
  if (nodes.length !== 4) throw new Error('Unexpected provenance graph size');
  const seen = new Set<string>();
  return nodes.map((node, index) => {
    if (!SHA.test(node.sha256) || !node.parents.every(parent => SHA.test(parent) && seen.has(parent))) {
      throw new Error('Invalid provenance ordering or predecessor');
    }
    if (node.kind !== ['source', 'split', 'model', 'benchmark'][index]) {
      throw new Error('Unexpected provenance node kind');
    }
    seen.add(node.sha256);
    return `${index + 1}. ${node.kind}: ${node.sha256}; parents: ${node.parents.join(', ') || 'none'}`;
  });
}
