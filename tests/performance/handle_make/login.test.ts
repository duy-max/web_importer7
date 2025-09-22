import http, { RefinedResponse, ResponseType } from "k6/http";
import { check, sleep } from "k6";
import { randomSeed } from "k6";
import { config } from "../k6config";

export const options = {
  vus: 30,
  duration: "30s",
};

randomSeed(12345);

export default function () {
  loginTest();
}

function nowIso(): string {
  return new Date().toISOString();
}

function loginTest() {
  const res = login(config.BASE_URL, config.IDENTIFIER, config.PASSWORD);

  let token: string | null = null;
  if (res.status === 200) {
    try {
      const jwt = res.json("jwt") as string | null;
      token = typeof jwt === "string" ? jwt : null;
    } catch {}
  }

  // Log mọi response fail ra console
  if (res.status !== 200 || !token) {
    console.log(`[${nowIso()}] VU:${__VU} ITER:${__ITER} STATUS:${res.status}`);
    console.log(res.body.slice(0, 1000)); // in tối đa 1000 ký tự
    console.log("--------------------------------------------------");
  }

  check(res, {
    "status is 200": (r) => r.status === 200,
    "got token when 200": (r) => r.status !== 200 || token !== null,
  });

  sleep(randomIntBetween(3, 5));
}

function login(baseUrl: string, identifier: string, password: string): RefinedResponse<ResponseType> {
  return http.post(`${baseUrl}/api/auth/local`, JSON.stringify({ identifier, password }), {
    headers: { "Content-Type": "application/json" },
  });
}

function randomIntBetween(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}
