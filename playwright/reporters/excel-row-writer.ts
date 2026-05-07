/**
 * excel-row-writer.ts — custom Playwright reporter that writes test results
 *                       to BOURACKA-TESTPLAN-v0.4.x.xlsx → 07_TestRunResults.
 *
 * Per CP-SUPIN-04 STEP 28. Replaces the JSON-only stub from CP-SUPIN-02.
 *
 * Each test's onTestEnd event:
 *   - Resolves TC code from test title (e.g. "TC-CP-001 — bring-up smoke")
 *   - Computes result row: tc_code, run_id, env, viewport, framework,
 *     status, duration_ms, retry, started_at, error_message, screenshot, trace
 *   - Buffers; on onEnd writes results.json AND spawns
 *     `py tools/append_test_run_result.py results.json`
 *   - Python helper UPSERTs into 07_TestRunResults (key: tc_code+run_id+retry)
 *
 * If Python helper / openpyxl unavailable, degrades gracefully to
 * JSON-only output (no fatal error, just a console warning).
 *
 * Also writes a status-badge SVG for README embedding.
 */
import type { Reporter, TestCase, TestResult, FullConfig } from "@playwright/test/reporter";
import { spawnSync } from "node:child_process";
import { writeFileSync, mkdirSync, existsSync } from "node:fs";
import { join } from "node:path";

interface ResultRow {
  tc_code: string;
  test_title: string;
  run_id: string;
  env: string;
  viewport: string;
  framework: string;
  status: "passed" | "failed" | "timedOut" | "skipped" | "interrupted";
  duration_ms: number;
  retry: number;
  started_at: string;
  ended_at: string;
  error_message: string;
  screenshot_ref: string;
  trace_ref: string;
}

class ExcelRowWriter implements Reporter {
  private runId: string;
  private outDir: string;
  private rows: ResultRow[] = [];
  private bouRackaBase: string;

  constructor() {
    this.runId = `RUN-${new Date().toISOString().replace(/[:.]/g, "").slice(0, 15)}`;
    this.outDir = join(process.cwd(), "test-results", this.runId);
    this.bouRackaBase = process.env.BOURACKA_BASE ?? "https://demo.bouracka.cz";
    mkdirSync(this.outDir, { recursive: true });
  }

  onBegin(_config: FullConfig, _suite: any) {
    console.log(`[excel-row-writer] run id: ${this.runId}`);
    console.log(`[excel-row-writer] target: ${this.bouRackaBase}`);
  }

  onTestEnd(test: TestCase, result: TestResult) {
    const project = test.parent?.project()?.name ?? "unknown";
    const viewport = this.viewportFromProject(project);
    const tcCode = this.extractTcCode(test.title);

    const screenshot = result.attachments.find(
      (a) => a.contentType === "image/png" && a.name.includes("test-failed")
    );
    const trace = result.attachments.find((a) => a.contentType === "application/zip");

    const row: ResultRow = {
      tc_code: tcCode,
      test_title: test.title,
      run_id: this.runId,
      env: this.bouRackaBase,
      viewport,
      framework: "playwright",
      status: result.status as ResultRow["status"],
      duration_ms: result.duration,
      retry: result.retry,
      started_at: new Date(result.startTime).toISOString(),
      ended_at: new Date(result.startTime.valueOf() + result.duration).toISOString(),
      error_message: result.errors.length > 0
        ? (result.errors[0].message ?? "").slice(0, 500)
        : "",
      screenshot_ref: screenshot?.path ?? "",
      trace_ref: trace?.path ?? "",
    };
    this.rows.push(row);
  }

  async onEnd() {
    const jsonPath = join(this.outDir, "results.json");
    writeFileSync(jsonPath, JSON.stringify(this.rows, null, 2), "utf-8");
    console.log(`[excel-row-writer] wrote JSON: ${jsonPath}`);

    const helper = join(process.cwd(), "tools", "append_test_run_result.py");
    if (existsSync(helper)) {
      const r = spawnSync("py", [helper, jsonPath], {
        stdio: "inherit",
        shell: false,
      });
      if (r.status === 0) {
        console.log(`[excel-row-writer] Excel upsert OK`);
      } else {
        console.warn(
          `[excel-row-writer] Excel upsert failed (exit ${r.status}); JSON preserved`
        );
      }
    } else {
      console.warn(
        `[excel-row-writer] tools/append_test_run_result.py not found; JSON-only`
      );
    }

    this.writeStatusBadge();
  }

  private extractTcCode(title: string): string {
    const m = title.match(/\b(TC-CP-[A-Z0-9-]+)\b/);
    return m ? m[1] : "TC-UNKNOWN";
  }

  private viewportFromProject(name: string): string {
    const m = name.match(/(\d+)$/);
    if (m) return `${m[1]}x*`;
    if (name.includes("desktop")) return "desktop";
    return name;
  }

  private writeStatusBadge() {
    const total = this.rows.length;
    const passed = this.rows.filter((r) => r.status === "passed").length;
    const failed = this.rows.filter(
      (r) => r.status === "failed" || r.status === "timedOut"
    ).length;
    const colour = failed === 0 ? "#22c55e" : passed > failed ? "#eab308" : "#ef4444";
    const label = `${passed}/${total} passed`;

    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="200" height="20" role="img">
  <rect width="110" height="20" fill="#555"/>
  <rect x="110" width="90" height="20" fill="${colour}"/>
  <text x="55" y="14" fill="#fff" font-family="Verdana,sans-serif" font-size="11" text-anchor="middle">bouracka tests</text>
  <text x="155" y="14" fill="#fff" font-family="Verdana,sans-serif" font-size="11" text-anchor="middle">${label}</text>
</svg>`;
    const badgePath = join(this.outDir, "..", "status-badge.svg");
    writeFileSync(badgePath, svg, "utf-8");
    console.log(`[excel-row-writer] status badge: ${badgePath}`);
  }
}

export default ExcelRowWriter;
