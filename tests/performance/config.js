




export const options = {
  scenarios: {
    login_once: {
      executor: "per-vu-iterations",
      vus: 30,
      iterations: 1,
    },
  },
};
/*
k6 sẽ khởi tạo ngay 30 VU cùng lúc, và mỗi VU sẽ chạy đúng 1 iteration (tức là login 1 lần).
Sau khi mỗi VU chạy xong 1 iteration thì dừng lại → test kết thúc.
Nghĩa là bạn sẽ có 50 request login gần như đồng thời được gửi đi và chỉ có đúng 30 request thôi
*/





export const options = {
  vus: 30,
  duration: "30s",
};

/* Nghĩa là có 30 user ảo, mỗi user sẽ lặp đi lặp lại logic trong default() trong 30 giây.
Một vòng login ~ 2s.
Có sleep(0.5) sau vòng login.
Như vậy mỗi VU ~ 2.5s tạo 1 request login.
Trong 30s:
1 VU tạo ra ≈ 30 ÷ 2.5 ≈ 12 requests.
Với 30 VU → tổng ≈ 360 requests.
*/


export const options = {
  stages: [
    { duration: '1m', target: 10 },  // tăng từ 0 lên 10 users trong 1 phút
    { duration: '2m', target: 20 },  // tăng lên 20 users trong 2 phút
    { duration: '3m', target: 30 },  // tăng lên 30 users trong 3 phút
    { duration: '5m', target: 30 },  // giữ 30 users trong 5 phút
    { duration: '1m', target: 0 },   // giảm về 0 trong 1 phút
  ],
};