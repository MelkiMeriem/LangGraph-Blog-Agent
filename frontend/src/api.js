const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function fetchLanguages() {
  const res = await fetch(`${API_BASE_URL}/languages`);
  if (!res.ok) {
    throw new Error("Failed to load supported languages");
  }
  const data = await res.json();
  return data.supported_languages;
}

export async function transcribeUpload(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE_URL}/transcribe-upload`, {
    method: "POST",
    body: formData,
  });
  const data = await res.json();
  if (!res.ok) {
    const detail = Array.isArray(data.detail)
      ? data.detail.map((d) => d.msg).join("; ")
      : data.detail;
    throw new Error(detail || `Upload failed with status ${res.status}`);
  }
  return data.transcript;
}

export async function generateBlog(payload) {
  const res = await fetch(`${API_BASE_URL}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) {
    const detail = Array.isArray(data.detail)
      ? data.detail.map((d) => d.msg).join("; ")
      : data.detail;
    throw new Error(detail || `Request failed with status ${res.status}`);
  }
  return data;
}
