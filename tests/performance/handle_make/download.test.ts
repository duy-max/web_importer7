import { sleep, check } from "k6";
import { config } from "../k6config";
import { login, exportExcel } from "../utils";

const BASE_URL = config.BASE_URL;
const MAKE_NAME = (__ENV.MAKE_NAME as string) || "Chrysler";
const FUNCTION_NAME = (__ENV.FUNCTION_NAME as string) || "Mode06";

export const options = config.options;

export function downloadTest () {
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

  // 2) Trigger export-excel API
  const res = exportExcel(BASE_URL, token as string, MAKE_NAME, FUNCTION_NAME);

  // 3) Basic validations
  const ok = check(res, {
    "export: status 200/202": (r) => r.status === 200 || r.status === 202,
    "export: JSON parsable": (r) => {
      try {
        r.json();
        return true;
      } catch {
        return false;
      }
    },
  });

  if (!ok) {
    console.error(
      JSON.stringify(
        {
          step: "export",
          url: `${BASE_URL}/api/function/export-excel-data`,
          status: res.status,
          body: (() => {
            try {
              return res.json();
            } catch {
              return res.body;
            }
          })(),
          message: "Export Excel API validation failed",
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