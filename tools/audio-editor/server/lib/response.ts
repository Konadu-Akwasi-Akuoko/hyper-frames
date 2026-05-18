import type { Context } from "hono";
import type { ContentfulStatusCode } from "hono/utils/http-status";

export type ApiOk<T> = { success: true; data: T };
export type ApiFail = {
  success: false;
  error: { code: string; message: string; details?: unknown };
};
export type ApiResponse<T> = ApiOk<T> | ApiFail;

export class ApiError extends Error {
  readonly code: string;
  readonly httpStatus: ContentfulStatusCode;
  readonly details?: unknown;

  constructor(
    code: string,
    message: string,
    httpStatus: ContentfulStatusCode,
    details?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.httpStatus = httpStatus;
    this.details = details;
  }
}

export function ok<T>(c: Context, data: T, status: ContentfulStatusCode = 200) {
  return c.json({ success: true, data }, status);
}

export function fail(
  c: Context,
  code: string,
  message: string,
  status: ContentfulStatusCode,
  details?: unknown,
) {
  return c.json({ success: false, error: { code, message, details } }, status);
}
