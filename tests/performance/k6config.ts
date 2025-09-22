export const config = {
  BASE_URL: "https://importers.cartek.com.vn",
  IDENTIFIER: "qcteam.rdhw@vn.innova.com",
  PASSWORD: "qcteam.rdhw",
  options: {
    vus: 30,   
    duration: "30s",
    thresholds: {
      http_req_duration: ["p(95)<1000"],
      http_req_failed: ["rate<0.01"]  // <1% request lỗi
    },
  },
};