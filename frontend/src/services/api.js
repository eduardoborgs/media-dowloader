import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "";

const api = axios.create({
  baseURL: API_URL,
  timeout: 20000,
});

export async function fetchMediaInfo(url) {
  try {
    const { data } = await api.post("/api/info", { url });
    return data;
  } catch (error) {
    const detail = error.response?.data?.detail;
    throw new Error(detail || "Erro ao buscar informações da mídia.");
  }
}

export function buildDownloadUrl(url, formatId, mediaType) {
  const params = new URLSearchParams({
    url,
    format_id: formatId,
    media_type: mediaType,
  });
  return `${API_URL}/api/download?${params.toString()}`;
}