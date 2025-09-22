import { sleep, check } from "k6";
import { config } from "../k6config";
import { login, cloneDraft, deleteDraft } from "../utils";

const BASE_URL = config.BASE_URL;
const MAKE_NAME = (__ENV.MAKE_NAME as string) || "Honda";
const FUNCTION_NAME = (__ENV.FUNCTION_NAME as string) || "Common";
const DRAFT_ID = __ENV.DRAFT_ID as string | undefined;

export const options = config.options;

export function deleteTest () {
  const token = login(BASE_URL, config.IDENTIFIER, config.PASSWORD);
  const authOk = check(token, { "auth: got token": (t) => t !== null });
  if (!authOk) {
    console.error("Login failed, no token returned");
    return;
  }

  let draftId: number | null = null;
  if (DRAFT_ID) {
    draftId = Number(DRAFT_ID);
  } else {
    draftId = cloneDraft(BASE_URL, token as string, MAKE_NAME, FUNCTION_NAME);
  }

  if (!draftId || Number.isNaN(draftId)) {
    return;
  }

  deleteDraft(BASE_URL, token as string, draftId);
  sleep(1);
}

export function handleSummary(data: any) {
  return {
    "result.json": JSON.stringify(data, null, 2),
  };
}