export type ApiOk<T> = { success: true; data: T };
export type ApiFail = {
  success: false;
  error: { code: string; message: string; details?: unknown };
};
export type ApiResponse<T> = ApiOk<T> | ApiFail;

export class ApiError extends Error {
  readonly code: string;
  readonly httpStatus: number;
  readonly details?: unknown;

  constructor(code: string, message: string, httpStatus: number, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.httpStatus = httpStatus;
    this.details = details;
  }
}

function isApiResponse(v: unknown): v is ApiResponse<unknown> {
  return (
    typeof v === "object" &&
    v !== null &&
    "success" in v &&
    typeof (v as { success: unknown }).success === "boolean"
  );
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(path, init);
  } catch (e: unknown) {
    throw new ApiError("NETWORK", e instanceof Error ? e.message : String(e), 0);
  }

  let body: unknown;
  try {
    body = await res.json();
  } catch (e: unknown) {
    throw new ApiError(
      "PARSE",
      `failed to parse JSON: ${e instanceof Error ? e.message : String(e)}`,
      res.status,
    );
  }

  if (!isApiResponse(body)) {
    throw new ApiError("PARSE", "response did not match envelope shape", res.status);
  }

  if (body.success) {
    return body.data as T;
  }
  throw new ApiError(body.error.code, body.error.message, res.status, body.error.details);
}
