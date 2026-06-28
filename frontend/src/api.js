export const competencia = "2026-06";
export const dataInicio = "2026-03-31";
export const dataFim = "2026-06-26";

export function apiBaseUrl() {
  if (!window.location.hostname.includes("onrender.com")) {
    return "http://localhost:8000";
  }
  return "https://gestao-m3mu.onrender.com";
}

export async function api(path, options = {}) {
  const config = { ...options };

  if (config.body) {
    config.headers = { "Content-Type": "application/json", ...(config.headers || {}) };
  }

  const response = await fetch(apiBaseUrl() + path, config);

  if (!response.ok) {
    throw new Error(String(response.status) + " em " + apiBaseUrl() + path);
  }

  return response.json();
}

export function money(value) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(Number(value || 0));
}
