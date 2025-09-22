// handle_make/login.test.ts
import http from "k6/http";
import { check, sleep } from "k6";
import { randomSeed } from "k6";

// k6config.ts
var config = {
  BASE_URL: "https://importers.cartek.com.vn",
  IDENTIFIER: "qcteam.rdhw@vn.innova.com",
  PASSWORD: "qcteam.rdhw",
  options: {
    vus: 30,
    duration: "30s",
    thresholds: {
      http_req_duration: ["p(95)<1000"],
      http_req_failed: ["rate<0.01"]
      // <1% request lỗi
    }
  }
};

// handle_make/login.test.ts
var options = {
  vus: 30,
  duration: "30s"
};
randomSeed(12345);
function login_test_default() {
  loginTest();
}
function nowIso() {
  return (/* @__PURE__ */ new Date()).toISOString();
}
function loginTest() {
  const res = login(config.BASE_URL, config.IDENTIFIER, config.PASSWORD);
  let token = null;
  if (res.status === 200) {
    try {
      const jwt = res.json("jwt");
      token = typeof jwt === "string" ? jwt : null;
    } catch {
    }
  }
  if (res.status !== 200 || !token) {
    console.log(`[${nowIso()}] VU:${__VU} ITER:${__ITER} STATUS:${res.status}`);
    console.log(res.body.slice(0, 1e3));
    console.log("--------------------------------------------------");
  }
  check(res, {
    "status is 200": (r) => r.status === 200,
    "got token when 200": (r) => r.status !== 200 || token !== null
  });
  sleep(randomIntBetween(3, 5));
}
function login(baseUrl, identifier, password) {
  return http.post(`${baseUrl}/api/auth/local`, JSON.stringify({ identifier, password }), {
    headers: { "Content-Type": "application/json" }
  });
}
function randomIntBetween(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}
export {
  login_test_default as default,
  options
};
