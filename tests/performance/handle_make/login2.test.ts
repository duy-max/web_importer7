import http, { RefinedResponse, ResponseType } from "k6/http";
import { check, sleep } from "k6";
import { config } from "../k6config"; // giả sử bạn có file config

export const options = config.options;

interface LogEntry {
  vu: number;
  iter: number;
  status: number;
  body: string;
}

let logs: LogEntry[] = [];

export function loginTest() {
  console.log(
    `url: ${config.BASE_URL}, identifier: ${config.IDENTIFIER}, password: ${config.PASSWORD}`
  );

  const res = login(config.BASE_URL, config.IDENTIFIER, config.PASSWORD);
logs.push({
  vu: __VU,
  iter: __ITER,
  status: res.status,
  body: String(res.body),
});

// xử lý token nếu 200 thôi
let token: string | null = null;
if (res.status === 200) {
  try {
    const jwt = res.json("jwt") as string | null;
    token = typeof jwt === "string" ? jwt : null;
  } catch (err) {
    console.error("Failed to parse token:", err);
  }
}

const ok = check(res, {
  "login success": (r) => r.status === 200 && token !== null,
});

if (!ok) {
  console.error(
    JSON.stringify({
      url: `${config.BASE_URL}/api/auth/local`,
      status: res.status,
      message: "Login failed",
    })
  );
}

sleep(1);
}

export default function () {
  loginTest();
}

export function handleSummary(data: any) {
  return {
    "result.json": JSON.stringify({ metrics: data, logs }, null, 2),
  };
}

function login(
  BASE_URL: string,
  identifier: string,
  password: string
): RefinedResponse<ResponseType>{
  const res = http.post(
    `${BASE_URL}/api/auth/local`,
    JSON.stringify({ identifier, password }),
    { headers: { "Content-Type": "application/json" } }
  );

  console.log(`status: ${res.status}, body: ${res.body}`);

  // if (res.status === 200) {
  //   return res;
  // }

  // return null;
  return res; // luôn trả về res, kể cả khi status != 200

}
