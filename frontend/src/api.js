export const competencia = "2025-06";
export const dataInicio = "2025-06-01";
export const dataFim = "2025-06-30";

export function apiBaseUrl() {
  if (!window.location.hostname.includes("onrender.com")) {
    return "http://localhost:8000";
  }
  return "https://gestao-m3mu.onrender.com";
}

export async function api(path, options = {}) {
  const response = await fetch(apiBaseUrl() + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    throw new Error(String(response.status) + " em " + apiBaseUrl() + path);
  }

  return response.json();
}

export function money(value) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(Number(value || 0));
}
