/**
 * spec-loader.ts — runtime spec loader (R-CONTRACT-1)
 *
 * Per CP-SUPIN-03 STEP 4.1 + Opus review §6.5.
 *
 * Reads BOURACKA-TESTPLAN-v0.2.xlsx via SheetJS at test-runtime;
 * resolves parameters per 02b_TC_Parameters; resolves assertions
 * per 02c_TC_Assertions × 02d_AssertionLibrary; returns a typed
 * ResolvedTestCase that the test runner consumes to drive
 * Playwright/Cypress code.
 *
 * The workbook is the LIVE EXECUTION CONTRACT; SPEC.md is the human
 * companion, NOT the source of truth for execution.
 */
import * as XLSX from 'xlsx';
import * as fs from 'node:fs';
import * as path from 'node:path';

/* ──────────────────────────────────────────────────────────────────────── */
/* Types                                                                    */
/* ──────────────────────────────────────────────────────────────────────── */

export type FurpsDim = 'F' | 'U' | 'R' | 'P' | 'S' | '+D' | '+I' | '+N' | '+L' | '+P_phys';
export type ParamSourceKind = 'literal' | 'fixture-ref' | 'env-config' | 'derived' | 'from-mock-response';
export type StepKind = 'trigger_point' | 'data_collection_point' | 'control_point' | 'assertion';

export interface ResolvedParameter {
  paramId: string;
  name: string;
  kind: string;            // string | integer | decimal | boolean | json | regex
  sourceKind: ParamSourceKind;
  sourceRef: string;
  resolvedValue: string | number | boolean | object | null;
  fromMock: boolean;       // when true, resolve at runtime from mock response
}

export interface ResolvedAssertion {
  stepId: string;
  libraryCode: string;     // LIB-AS-FUNC-001 etc.
  furpsDim: FurpsDim;
  expected: string;
  playwrightSnippet: string;
  cypressSnippet: string;
}

export interface ResolvedStep {
  id: string;
  kind: StepKind;
  titleCs: string;
  titleEn: string;
  selector: string;
  input: string;           // may be a param-ref token like "param[TC-CP-005-P-01]"
  expected: string;
  furps: FurpsDim[];
  envDivergence: Record<string, string>;
  integrationTouchpoint: string | null;
  recovery: 'none' | 'retry-up-to-N' | 'manual-fallback';
  notes: string;
}

export interface ResolvedTestCase {
  itemCode: string;
  nameCs: string;
  nameEn: string;
  ttRef: string;
  type: 'happy' | 'failure' | 'regression' | 'smoke';
  priority: 'A' | 'B' | 'C' | 'D';
  furpsDimensions: FurpsDim[];
  requirementRef: string;
  impulseRef: string;
  diligence: string;
  stateMachineTerminalState: string;
  stateErrorSubreason: string;
  parameters: ResolvedParameter[];
  assertions: ResolvedAssertion[];
  steps: ResolvedStep[];
  envCoverage: string[];
  viewportSpec: string[];
  frameworkTargets: string[];
  devSpecPath: string;     // → specs/TC-CP-NNN-SPEC.md (Tier B companion)
}

/* ──────────────────────────────────────────────────────────────────────── */
/* Loader                                                                   */
/* ──────────────────────────────────────────────────────────────────────── */

const ROOT = path.resolve(__dirname, '..', '..');
const XLSX_PATH = path.join(ROOT, 'BOURACKA-TESTPLAN-v0.2.xlsx');

function loadWorkbook(): XLSX.WorkBook {
  if (!fs.existsSync(XLSX_PATH)) {
    throw new Error(`spec-loader: workbook not found at ${XLSX_PATH}`);
  }
  return XLSX.readFile(XLSX_PATH);
}

function sheetToRows<T = Record<string, unknown>>(wb: XLSX.WorkBook, sheetName: string): T[] {
  const ws = wb.Sheets[sheetName];
  if (!ws) throw new Error(`spec-loader: sheet '${sheetName}' not found`);
  return XLSX.utils.sheet_to_json<T>(ws, { defval: '' });
}

/* ──────────────────────────────────────────────────────────────────────── */
/* Parameter + assertion resolution                                         */
/* ──────────────────────────────────────────────────────────────────────── */

function resolveParameters(wb: XLSX.WorkBook, tcCode: string, env: string): ResolvedParameter[] {
  const params = sheetToRows<Record<string, string>>(wb, '02b_TC_Parameters')
    .filter(r => r['test_case_ref'] === tcCode);

  return params.map(p => {
    const sourceKind = p['source_kind'] as ParamSourceKind;
    const sourceRef = p['source_ref'];
    const defaultVal = p['default_value'];
    let resolved: string | number | boolean | object | null = defaultVal;
    let fromMock = false;

    switch (sourceKind) {
      case 'literal':
        resolved = sourceRef;
        break;
      case 'fixture-ref':
        resolved = resolveFixtureRef(sourceRef);
        break;
      case 'env-config':
        resolved = resolveEnvConfig(sourceRef, env);
        break;
      case 'derived':
        resolved = defaultVal; // computed at test-runtime in test code
        break;
      case 'from-mock-response':
        resolved = defaultVal; // bound at test-runtime when mock responds
        fromMock = true;
        break;
    }

    return {
      paramId: p['param_id'],
      name: p['param_name'],
      kind: p['param_kind'],
      sourceKind,
      sourceRef,
      resolvedValue: resolved,
      fromMock,
    };
  });
}

function resolveFixtureRef(ref: string): string | object {
  // Form: "fixtures/shared/test-drivers.json::tester_jeden.phone"
  const [filePart, keyPart] = ref.split('::');
  const fixturePath = path.join(ROOT, filePart);
  if (!fs.existsSync(fixturePath)) return ref;
  const content = JSON.parse(fs.readFileSync(fixturePath, 'utf8'));
  if (!keyPart) return content;
  return keyPart.split('.').reduce<unknown>((acc, k) => {
    if (acc && typeof acc === 'object' && k in (acc as Record<string, unknown>)) {
      return (acc as Record<string, unknown>)[k];
    }
    return undefined;
  }, content) as string | object;
}

function resolveEnvConfig(ref: string, env: string): string {
  // Form: "env/{env}.json::base_url"
  const [filePart, keyPart] = ref.replace('{env}', env).split('::');
  const envPath = path.join(ROOT, filePart);
  if (!fs.existsSync(envPath)) return ref;
  const content = JSON.parse(fs.readFileSync(envPath, 'utf8'));
  return keyPart ? (content[keyPart] ?? '') : JSON.stringify(content);
}

function resolveAssertions(wb: XLSX.WorkBook, tcCode: string): ResolvedAssertion[] {
  const tcAssertions = sheetToRows<Record<string, string>>(wb, '02c_TC_Assertions')
    .filter(r => r['test_case_ref'] === tcCode);
  const library = sheetToRows<Record<string, string>>(wb, '02d_AssertionLibrary');
  const libByCode: Record<string, Record<string, string>> = {};
  for (const lib of library) libByCode[lib['library_code']] = lib;

  return tcAssertions.map(a => {
    const lib = libByCode[a['assertion_library_ref']];
    return {
      stepId: a['step_id'],
      libraryCode: a['assertion_library_ref'],
      furpsDim: a['furps_dimension'] as FurpsDim,
      expected: a['expected'],
      playwrightSnippet: lib?.['playwright_snippet'] ?? '',
      cypressSnippet: lib?.['cypress_snippet'] ?? '',
    };
  });
}

/* ──────────────────────────────────────────────────────────────────────── */
/* Top-level API                                                            */
/* ──────────────────────────────────────────────────────────────────────── */

export function loadTestCase(tcCode: string, env: string = 'tst'): ResolvedTestCase {
  const wb = loadWorkbook();
  const tcRows = sheetToRows<Record<string, string>>(wb, '02_TestCases')
    .filter(r => r['item_code'] === tcCode);
  if (tcRows.length === 0) {
    throw new Error(`spec-loader: TC '${tcCode}' not found in 02_TestCases`);
  }
  const tc = tcRows[0];

  return {
    itemCode: tc['item_code'],
    nameCs: tc['item_name_cs'],
    nameEn: tc['item_name_en'],
    ttRef: tc['test_target_ref'],
    type: tc['type'] as ResolvedTestCase['type'],
    priority: tc['priority'] as ResolvedTestCase['priority'],
    furpsDimensions: (tc['furps_dimensions'] || '').split(',').map(s => s.trim()).filter(Boolean) as FurpsDim[],
    requirementRef: tc['requirement_ref'] || '',
    impulseRef: tc['impulse_ref'] || '',
    diligence: tc['diligence'] || '',
    stateMachineTerminalState: tc['state_machine_terminal_state'] || '',
    stateErrorSubreason: tc['state_error_subreason'] || '',
    parameters: resolveParameters(wb, tcCode, env),
    assertions: resolveAssertions(wb, tcCode),
    steps: [], // step list lives in SPEC.md (Tier B); future v0.3 will land 02e_TC_Steps
    envCoverage: (tc['env_coverage'] || '').split('+').map(s => s.trim()).filter(Boolean),
    viewportSpec: (tc['viewport_spec'] || '').split('/').map(s => s.trim()).filter(Boolean),
    frameworkTargets: (tc['framework_targets'] || '').split(';').map(s => s.trim()).filter(Boolean),
    devSpecPath: tc['dev_spec_path'] || '',
  };
}

export function listAllTestCases(): string[] {
  const wb = loadWorkbook();
  return sheetToRows<Record<string, string>>(wb, '02_TestCases')
    .map(r => r['item_code'])
    .filter(Boolean);
}
