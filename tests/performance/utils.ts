import http, {RefinedResponse, ResponseType} from "k6/http";
import { check } from "k6";

// export function login(BASE_URL: string, identifier: string, password: string): RefinedResponse<ResponseType> | null {
//   const res = http.post(
//     `${BASE_URL}/api/auth/local`,
//     JSON.stringify({ identifier, password }),
//     { headers: { "Content-Type": "application/json" } }
//   );

//   console.log(`status: ${res.status}, body: ${res.body}`);

//   if (res.status === 200) {
//     return res;
//   }

//   return null;
// }


export function cloneDraft(BASE_URL: string, token: string, makeName: string, functionName: string): number | null {
  const url = `${BASE_URL}/api/version/clone-data`;
  const payload = JSON.stringify({
    make_name: makeName,
    function_name: functionName,
  });
  const headers = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };

  const res = http.post(url, payload, { headers });

  const ok = check(res, {
    "clone: status 200": (r) => r.status === 200,
    "clone: has newVersion.id": (r) => {
      try {
        const data = r.json() as any;
        return Boolean(data?.newVersion?.id);
      } catch {
        return false;
      }
    },
  });

  if (!ok) {
    console.error(
      JSON.stringify(
        {
          step: "clone",
          url,
          status: res.status,
          body: (() => {
            try {
              return res.json();
            } catch {
              return res.body;
            }
          })(),
          message: "Clone failed; cannot proceed to delete",
        },
        null,
        2
      )
    );
    return null;
  }

  const data = res.json() as any;
  return data.newVersion.id as number;
}

export function deleteDraft(BASE_URL: string, token: string, draftId: number) {
  const url = `${BASE_URL}/api/versions/${draftId}`;
  const headers = { Authorization: `Bearer ${token}` };

  const res = http.del(url, null, { headers });

  const ok = check(res, {
    "delete: status 200": (r) => r.status === 200,
  });

  if (!ok) {
    console.error(
      JSON.stringify(
        {
          step: "delete",
          url,
          status: res.status,
          body: (() => {
            try {
              return res.json();
            } catch {
              return res.body;
            }
          })(),
          message: "Delete failed",
        },
        null,
        2
      )
    );
  }

  return res;
}


export function updateReleaseNote(
  BASE_URL: string,
  token: string,
  draftId: number,
  rdNote: string,
  releaseNote: string,
  libLog: string
) {
  const url = `${BASE_URL}/api/version/update_release_note`;
  const headers = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
  // Note: backend in UI test returns "rad_note" field; request uses the same key.
  const payload = JSON.stringify({
    id: draftId, // include id to target the draft
    rad_note: rdNote,
    release_note: releaseNote,
    lib_log: libLog,
  });

  const res = http.put(url, payload, { headers });

  check(res, {
    "update: status 200": (r) => r.status === 200,
  });

  return res;
}

export function exportExcel(
  BASE_URL: string,
  token: string,
  makeName: string,
  functionName: string
) {
  const url = `${BASE_URL}/api/function/export-excel-data`;
  const headers = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
  const payload = JSON.stringify({
    make_name: makeName,
    function_name: functionName,
  });

  const res = http.post(url, payload, { headers });

  check(res, {
    "export: status 200/202": (r) => r.status === 200 || r.status === 202,
  });

  return res;
}


export function login(BASE_URL: string, identifier: string, password: string): RefinedResponse<ResponseType> | null {
  try {
    const res = http.post(
      `${BASE_URL}/api/auth/local`,
      JSON.stringify({ identifier, password }),
      { 
        headers: { "Content-Type": "application/json" },
        timeout: "10s", // timeout 10s
      }
    );

    console.log(`Login attempt - Status: ${res.status}`);
    
    // Trả về response cho mọi status để test có thể log
    return res;
    
  } catch (error) {
    console.error("Login request failed:", error);
    return null;
  }
}
