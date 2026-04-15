const API_BASE_URL = (
  process.env.API_BASE_URL || "http://localhost:8000"
).replace(/\/+$/, "");

interface ApiResponse {
  [key: string]: unknown;
}

interface AssetResponse {
  id: string;
  job_id: string;
  asset_type: string;
  file_path: string;
  file_url?: string;
  duration?: number;
  metadata?: Record<string, unknown>;
}

interface JobResponse {
  id: string;
  user_id: string;
  workflow_type: string;
  status: "queued" | "processing" | "completed" | "failed";
  input_data: Record<string, unknown>;
  output_data?: Record<string, unknown>;
  error_message?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

interface UploadResponse {
  url?: string;
  file_path?: string;
}

async function request<T = ApiResponse>(
  method: string,
  path: string,
  options: { body?: unknown; isFormData?: boolean } = {}
): Promise<T | null> {
  const url = `${API_BASE_URL}${path}`;
  const headers: Record<string, string> = {};

  if (!options.isFormData) {
    headers["Content-Type"] = "application/json";
  }

  try {
    const fetchOptions: RequestInit = { method, headers };

    if (options.body && !options.isFormData) {
      fetchOptions.body = JSON.stringify(options.body);
    } else if (options.body) {
      fetchOptions.body = options.body as BodyInit;
    }

    const resp = await fetch(url, fetchOptions);

    if (!resp.ok) {
      const text = await resp.text().catch(() => "");
      console.error(`[API] ${method} ${path} → ${resp.status}: ${text.slice(0, 300)}`);
      return null;
    }

    return (await resp.json()) as T;
  } catch (err) {
    console.error(`[API] ${method} ${path} failed:`, err);
    return null;
  }
}

export async function createUser(
  telegramId: number,
  username: string,
  firstName: string
): Promise<ApiResponse | null> {
  return request("POST", "/api/users", {
    body: { telegram_id: telegramId, username, first_name: firstName },
  });
}

export async function createJob(
  userId: string,
  workflowType: "generate_video" | "clip_shorts",
  inputData: Record<string, unknown>
): Promise<JobResponse | null> {
  return request<JobResponse>("POST", "/api/jobs", {
    body: { user_id: userId, workflow_type: workflowType, input_data: inputData },
  });
}

export async function getJobStatus(jobId: string): Promise<JobResponse | null> {
  return request<JobResponse>("GET", `/api/jobs/${jobId}`);
}

export async function getJobAssets(jobId: string): Promise<AssetResponse[]> {
  const result = await request<{ items: AssetResponse[] }>(
    "GET",
    `/api/jobs/${jobId}/assets`
  );
  if (result && Array.isArray(result.items)) return result.items;
  if (Array.isArray(result)) return result as unknown as AssetResponse[];
  return [];
}

export async function uploadFile(
  fileBytes: ArrayBuffer,
  filename: string
): Promise<UploadResponse | null> {
  const formData = new FormData();
  formData.append("file", new Blob([fileBytes]), filename);

  return request<UploadResponse>("POST", "/api/upload", {
    body: formData,
    isFormData: true,
  });
}
