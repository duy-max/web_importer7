import http from "k6/http";
import { sleep, check } from "k6";
import { config } from "../k6config";
import { login } from "../utils";

export const options = config.options;

export function cloneTest() {
  const token = login(config.BASE_URL, config.IDENTIFIER, config.PASSWORD);

  const res = http.post(
    `${config.BASE_URL}/api/version/clone`,
    JSON.stringify({ versionId: 123 }),
    {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    }
  );

  check(res, {
    "clone success": (r) => r.status === 200,
  });

  sleep(1);
}