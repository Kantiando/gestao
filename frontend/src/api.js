export const competencia = "2025-06";
export const dataInicio = "2025-06-01";
export const dataFim = "2025-06-30";

export function apiBaseCandidates() {
  if (!window.location.hostname.includes("onrender.com")) return ["http://localhost:8000"];

  const host = window.location.hostname;
  const candidates = ["https://gestao-api.onrender.com"];

  if (host.includes("gestao-web")) {
    candidates.unshift(`https://${host.replace("gestao-web", "gestao-api")}`);
  }

  const saved = window.localStorage.getItem("GESTAO_API_URL");
  if (saved) candidates.unshift(saved.replace(/\/$/, ""));

  return [...new Set(candidates)];
}

export function apiBaseUrl() {
  return apiBaseCandidates()[0];
}

export async function api(path, options = {}) {
  const errors = [];

  for (const base of apiBaseCandidates()) {
    try {
      const response = await fetch(`${base}${path}`, {
        headers: { "Content-Type": "application/json" },
        ...options,
      });

      if (response.ok) return response.json();
      errors.push(`${base}${path} -> ${response.status}`);
    } catch (error) {
      errors.push(`${base}${path} -> ${error.message}`);
    }
  }

  throw new Error(errors.join(" | "));
}

export function money(value) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(Number(value || 0));
}
