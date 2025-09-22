import { loginTest } from "./handle_make/login.test";
import { cloneTest } from "./handle_make/clone-version.test";
import path from "path";


// k6 options: map each scenario to its corresponding exec function
export const options = {
  scenarios: {
    login: {
      executor: "constant-vus",
      exec: "loginTest",
      vus: Number(__ENV.LOGIN_VUS || 5),
      duration: String(__ENV.LOGIN_DURATION || "10s"),
    },
    download: {
      executor: "constant-vus",
      exec: "downloadTest",
      vus: Number(__ENV.DOWNLOAD_VUS || 5),
      duration: String(__ENV.DOWNLOAD_DURATION || "10s"),
    },
  },
};

// Re-export functions so k6 can invoke them by name
export { loginTest, cloneTest };

// Aggregate all metrics and write timestamped JSON under tests/performance/reports/
export function handleSummary(data: any) {
  const toPlain = (metrics: Record<string, any>) => {
    const out: Record<string, any> = {};
    for (const [name, m] of Object.entries(metrics)) {
      out[name] = {
        type: (m as any).type,
        contains: (m as any).contains,
        thresholds: (m as any).thresholds,
        values: (m as any).values,
      };
    }
    return out;
  };

  const now = new Date();
  const pad = (n: number) => String(n).padStart(2, "0");
  const stamp = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}_${pad(
    now.getHours()
  )}-${pad(now.getMinutes())}-${pad(now.getSeconds())}`;

  const summary = {
    timestamp: now.toISOString(),
    scenarios: Object.keys((options as any).scenarios || {}),
    options,
    metrics: toPlain(data.metrics || {}),
  };

  const outPath = path.resolve(
  __dirname, // thư mục chứa file main.js sau khi build
  "reports",
  `result_${stamp}.json`
);

  return {
    [outPath]: JSON.stringify(summary, null, 2),
    stdout: `\n=== k6 summary saved to ${outPath}\n`,
  };
}