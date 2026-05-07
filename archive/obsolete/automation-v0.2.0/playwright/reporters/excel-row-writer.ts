/**
 * excel-row-writer — Playwright reporter.
 *
 * Writes one row per test execution into BOURACKA-TESTPLAN-v0.1.xlsx →
 * sheet `07_TestRunResults`. Honours the MI-M-T-import-ready ItemBase
 * column block from scope §5.2.
 *
 * Skeleton: this v0.1 stub captures the contract. Full implementation
 * lands in CP-SUPIN-03 once the env-config + workbook-path resolution +
 * concurrent-write strategy is decided (likely: write per-worker JSON
 * lines into runs/<date>-<tester>/results.jsonl, then a single
 * post-run script merges into the workbook to avoid xlsx-write
 * contention).
 */
import type {
  Reporter,
  TestCase,
  TestResult,
  FullConfig,
  Suite,
} from "@playwright/test/reporter";

interface RowDraft {
  test_run_ref: string;
  test_case_ref: string;          // TC-CP-NNN extracted from test title
  env_ref: string;                // ENV-TST / ENV-DMO / ENV-PUB
  framework: "playwright";
  verdict: "pass" | "fail" | "skip" | "blocked" | "partial";
  actual: string;
  evidence_path: string;
  duration_ms: number;
  viewport: string;
  step_failed_kind: "control_point" | "trigger_point" | "data_collection_point" | "assertion" | "n/a";
}

function tcRefFromTitle(title: string): string {
  const m = title.match(/TC-CP-\d+/);
  return m ? m[0] : "TC-UNK";
}

function envFromProjectName(name: string): string {
  if (name.startsWith("tst-demo")) return "ENV-DMO";
  if (name.startsWith("tst")) return "ENV-TST";
  if (name.startsWith("public")) return "ENV-PUB";
  return "ENV-UNK";
}

function viewportFromProjectName(name: string): string {
  const m = name.match(/mobile-(\d+)/);
  if (m) return `${m[1]}px`;
  if (name.endsWith("-desktop")) return "desktop";
  return "unknown";
}

function verdictFromStatus(status: TestResult["status"]): RowDraft["verdict"] {
  switch (status) {
    case "passed": return "pass";
    case "failed": return "fail";
    case "skipped": return "skip";
    case "interrupted": return "blocked";
    case "timedOut": return "fail";
    default: return "partial";
  }
}

function stepKindGuess(error: TestResult["error"] | undefined): RowDraft["step_failed_kind"] {
  if (!error) return "n/a";
  const msg = error.message ?? "";
  if (/expect|assert|toHave|toBe|toContain/i.test(msg)) return "assertion";
  if (/click|fill|press|goto|navigate/i.test(msg)) return "trigger_point";
  if (/locator|getByRole|innerText|boundingBox|attribute/i.test(msg)) return "data_collection_point";
  return "control_point";
}

export default class ExcelRowWriter implements Reporter {
  private runId = `RUN-${new Date().toISOString().replace(/[:.]/g, "-")}`;
  private rows: RowDraft[] = [];

  onBegin(_config: FullConfig, _suite: Suite) {
    process.stderr.write(`[excel-row-writer] run ${this.runId} starting\n`);
  }

  onTestEnd(test: TestCase, result: TestResult) {
    const row: RowDraft = {
      test_run_ref: this.runId,
      test_case_ref: tcRefFromTitle(test.title),
      env_ref: envFromProjectName(test.parent.project()?.name ?? ""),
      framework: "playwright",
      verdict: verdictFromStatus(result.status),
      actual: result.error?.message?.slice(0, 200) ?? "ok",
      evidence_path: result.attachments
        .map((a) => a.path)
        .filter(Boolean)
        .join(";"),
      duration_ms: result.duration,
      viewport: viewportFromProjectName(test.parent.project()?.name ?? ""),
      step_failed_kind: stepKindGuess(result.error),
    };
    this.rows.push(row);
  }

  async onEnd() {
    // CP-SUPIN-02 skeleton — write JSONL beside the run; CP-SUPIN-03 will
    // merge JSONL → BOURACKA-TESTPLAN-v0.1.xlsx via a post-run script.
    const fs = await import("node:fs/promises");
    const path = await import("node:path");
    const out = path.resolve(process.cwd(), "../runs", this.runId);
    await fs.mkdir(out, { recursive: true });
    const jsonl = this.rows.map((r) => JSON.stringify(r)).join("\n");
    await fs.writeFile(path.join(out, "results.jsonl"), jsonl, "utf8");
    process.stderr.write(`[excel-row-writer] wrote ${this.rows.length} rows to ${out}/results.jsonl\n`);
  }
}
