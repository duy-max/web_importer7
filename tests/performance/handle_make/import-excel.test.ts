import http from "k6/http";
import { sleep, check } from "k6";
import { config } from "../k6config";
import { login } from "../utils";
// jslib helper for multipart form-data
import { FormData } from "https://jslib.k6.io/formdata/0.0.2/index.js";

// Note: `open()` is provided by k6 at runtime (reads files at init time).
// Default ZIP path relative to this script: ../../../test_data/YourZipHere.zip
const DEFAULT_IMPORT_FILE =
  __ENV.IMPORT_FILE ||
  (config.IMPORT_FILE as string) ||
  "../../../test_data/Volkswagen_Mode06_ConditionsMeet.zip";

const MAKE_NAME = (__ENV.MAKE_NAME as string) || (config.MAKE_NAME as string) || "Volkswagen";
const FUNCTION_NAME =
  (__ENV.FUNCTION_NAME as string) || (config.FUNCTION_NAME as string) || "Mode06";

const BASE_IMPORT =
  (config.BASE_API_IMPORT as string) || (config.BASE_URL as string) || "http://localhost:3000";

export const options = config.options;

// Prepare multipart body once (init context)
const fileBin = open(DEFAULT_IMPORT_FILE, "b"); // binary mode
const fd = new FormData();
fd.append("file", http.file(fileBin, DEFAULT_IMPORT_FILE.split("/").pop() || "import.zip"));
fd.append("make_name", MAKE_NAME);
fd.append("function_name", FUNCTION_NAME);
// If backend requires other fields, append them here (e.g., fd.append("notes", "some text"))

export function importExcel () {
  // 1) Authenticate to get JWT
  const token = login(config.BASE_URL, config.IDENTIFIER, config.PASSWORD);
  const authOk = check(token, { "auth: got token": (t) => t !== null });

  if (!authOk) {
    console.error(
      JSON.stringify({
        url: `${config.BASE_URL}/api/auth/local`,
        status: "failed",
        message: "Login failed, no token returned",
      })
    );
    return;
  }

  // 2) Import Excel via API
  const url = `${BASE_IMPORT}/api/importdata`;
  const headers = {
    Authorization: `Bearer ${token}`,
    "Content-Type": fd.contentType(),
  };

  const res = http.post(url, fd.body(), { headers });

  // 3) Basic validations similar to UI+API test expectations
  const ok = check(res, {
    "import: status 200/202": (r) => r.status === 200 || r.status === 202,
    "import: JSON parsable": (r) => {
      try {
        r.json();
        return true;
      } catch {
        return false;
      }
    },
    "import: succeeded==true (if present)": (r) => {
      try {
        const data = r.json() as any;
        // Some backends respond 202 Accepted; skip strict check if field not present
        return data?.succeeded === undefined || data?.succeeded === true;
      } catch {
        return false;
      }
    },
    "import: errors==null (if present)": (r) => {
      try {
        const data = r.json() as any;
        return data?.errors === undefined || data?.errors === null;
      } catch {
        return false;
      }
    },
  });

  if (!ok) {
    console.error(
      JSON.stringify(
        {
          url,
          status: res.status,
          body: (() => {
            try {
              return res.json();
            } catch {
              return res.body;
            }
          })(),
          message: "Import Excel API validation failed",
        },
        null,
        2
      )
    );
  }

  // Short pacing between iterations
  sleep(1);
}

// Export a JSON summary like login.test.ts
// export function handleSummary(data: any) {
//   return {
//     "result.json": JSON.stringify(data, null, 2),
//   };
// }