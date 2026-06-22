import type {
  Idea,
  BoardCard,
  Channel,
  StageDef,
  IdeaKind,
  IdeaStatus,
  IdeaType,
  RawCounts,
} from "./types";

export type ApiResponse<T> =
  | { success: true; data: T }
  | { success: false; error: { code: string; message: string; details?: unknown } };

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
  if (body.success) return body.data as T;
  throw new ApiError(body.error.code, body.error.message, res.status, body.error.details);
}

function jsonBody(body: unknown): RequestInit {
  return {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  };
}

export interface CountsByType {
  total: number;
  byType: Record<string, number>;
}

export const api = {
  stages: () => apiFetch<StageDef[]>("/api/stages"),

  ideas: (params?: { status?: string; type?: string }) => {
    const q = new URLSearchParams();
    if (params?.status) q.set("status", params.status);
    if (params?.type) q.set("type", params.type);
    const qs = q.toString();
    return apiFetch<Idea[]>("/api/ideas" + (qs ? `?${qs}` : ""));
  },
  ideaCounts: () => apiFetch<CountsByType>("/api/ideas/counts"),
  triage: (id: string, body: { status?: IdeaStatus; kind?: IdeaKind; notes?: string }) =>
    apiFetch<Idea>(`/api/ideas/${id}`, { ...jsonBody(body), method: "PATCH" }),
  promote: (id: string) =>
    apiFetch<{ slug: string; name: string }>(`/api/ideas/${id}/promote`, { method: "POST" }),
  createIdea: (body: { title: string; type?: IdeaType; rationale?: string; source?: string }) =>
    apiFetch<Idea>("/api/ideas", jsonBody(body)),

  board: () => apiFetch<BoardCard[]>("/api/board"),
  syncBoard: () => apiFetch<BoardCard[]>("/api/board/sync", { method: "POST" }),
  setCard: (name: string, body: { stage?: string; notes?: string; title?: string }) =>
    apiFetch<{ name: string }>(`/api/board/${encodeURIComponent(name)}`, {
      ...jsonBody(body),
      method: "PATCH",
    }),
  addCard: (body: { slug: string; title?: string; date: string; stage?: string }) =>
    apiFetch<{ name: string }>("/api/board", jsonBody(body)),
  deleteCard: (name: string) =>
    apiFetch<{ name: string }>(`/api/board/${encodeURIComponent(name)}`, { method: "DELETE" }),

  rawCounts: () => apiFetch<RawCounts>("/api/discovery/raw-counts"),
  runDiscovery: (body: {
    sources?: string;
    videosPerChannel?: number;
    commentsPerVideo?: number;
    noComments?: boolean;
  }) => apiFetch<RawCounts & { log: string }>("/api/discovery/run", jsonBody(body)),

  channels: () => apiFetch<Channel[]>("/api/channels"),
};
