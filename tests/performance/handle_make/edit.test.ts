import { sleep, check } from "k6";
import { config } from "../k6config";
import { login, cloneDraft, updateReleaseNote } from "../utils";

const BASE_URL = config.BASE_URL;
const MAKE_NAME = (__ENV.MAKE_NAME as string) || "Honda";
const FUNCTION_NAME = (__ENV.FUNCTION_NAME as string) || "Common";

export const options = config.options;

export function editTest () {
  // 1) Authenticate
  const token = login(BASE_URL, config.IDENTIFIER, config.PASSWORD);
  const authOk = check(token, { "auth: got token": (t) => t !== null });
  if (!authOk) {
    console.error(
      JSON.stringify(
        {
          step: "auth",
          url: `${BASE_URL}/api/auth/local`,
          status: "failed",
          message: "Login failed, no token returned",
        },
        null,
        2
      )
    );
    return;
  }

  // 2) Ensure a draft exists (clone)
  const draftId = cloneDraft(BASE_URL, token as string, MAKE_NAME, FUNCTION_NAME);
  if (!draftId) return;

  // 3) Prepare payloads (match UI test style)
  const ts = new Date().toISOString().slice(0, 19).replace("T", " "); // "YYYY-MM-DD HH:mm:ss"
  const rdNotes = `update rd note at ${ts}`;
  const releaseNotes = `update release note at ${ts}`;
  const libLog = `update lib log at ${ts}`;

  // 4) Update notes via API
  const res = updateReleaseNote(
    BASE_URL,
    token as string,
    draftId,
    rdNotes,
    releaseNotes,
    libLog
  );

  // 5) Validate response (mirror assertions in UI test)
  const ok = check(res, {
    "edit: status 200": (r) => r.status === 200,
    "edit: json ok": (r) => {
      try {
        r.json();
        return true;
      } catch {
        return false;
      }
    },
    "edit: fields echoed": (r) => {
      try {
        const body = r.json() as any;
        return (
          body?.data?.release_note === releaseNotes &&
          body?.data?.rad_note === rdNotes &&
          body?.data?.lib_log === libLog
        );
      } catch {
        return false;
      }
    },
    "edit: success message": (r) => {
      try {
        const body = r.json() as any;
        return String(body?.message || "").includes("Successfully update release_note");
      } catch {
        return false;
      }
    },
  });

  if (!ok) {
    console.error(
      JSON.stringify(
        {
          step: "edit",
          url: `${BASE_URL}/api/version/update_release_note`,
          status: res.status,
          body: (() => {
            try {
              return res.json();
            } catch {
              return res.body;
            }
          })(),
          message: "Update release note API validation failed",
        },
        null,
        2
      )
    );
  }

  sleep(1);
}

// export function handleSummary(data: any) {
//   return {
//     "result.json": JSON.stringify(data, null, 2),
//   };
// }