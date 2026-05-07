/**
 * TC-CP-003 + TC-CP-004 — wizard end-to-end (skeleton; tst.* only).
 *
 * Per CLIENT-PILOT-SUPIN-V0.1.md §4.1 and FLW-003 / FLW-004:
 *   - TC-CP-003: full submit happy path (24 typed steps).
 *   - TC-CP-004: 9 failure variants (F1..F9).
 *
 * SKELETON STATUS: this file ships in CP-SUPIN-02 as a placeholder so the
 * folder structure is complete. The interior of the wizard is not yet
 * recon'd in detail — depth lands when user-supplied tst.* recon templates
 * arrive. Until then each test below uses test.skip() with a reason.
 *
 * R-CAST-2 — when implemented, every step MUST carry one of:
 *   trigger_point | data_collection_point | control_point | assertion
 */
import { test } from "@playwright/test";

test.describe("TC-CP-003 — Wizard happy end-to-end (tst.*)", () => {
  test.skip(({ baseURL }) => !baseURL?.includes("tst.bouracka.cz"),
    "TC-CP-003 runs against tst.* only (public is production-protected per C-1/C-2).");

  test("Phones → docs → SPZ → location → SMS-OTP both → submit → e-mail dispatch", async () => {
    test.skip(true, "Skeleton — depth pending user-supplied tst.* recon (per OQ-CP-15) and reCAPTCHA posture decision (per OQ-CP-14).");
  });
});

test.describe("TC-CP-004 — Wizard failure envelope (F1..F9)", () => {
  test.skip(({ baseURL }) => !baseURL?.includes("tst.bouracka.cz"),
    "TC-CP-004 runs against tst.* only.");

  for (const variant of [
    "F1 — Invalid SPZ format",
    "F2 — OCR fail (unreadable document)",
    "F3 — Driver-B SMS-OTP mismatch",
    "F4 — Out-of-ČR location",
    "F5 — Damage > 200 000 Kč (eligibility)",
    "F6 — reCAPTCHA challenge fails",
    "F7 — Server timeout on submit",
    "F8 — Mobile-only: viewport meta missing",
    "F9 — Mobile-only: hamburger overlay covers submit",
  ]) {
    test(variant, async () => {
      test.skip(true, "Skeleton — depth pending tst.* recon.");
    });
  }
});
