export const fluxoVazio = {
  entradas: 0,
  saidas: 0,
  saldo_periodo: 0,
  movimentos: [],
  por_dia: [],
  por_categoria: [],
};

export async function optionalRequest(requestFn, path, fallback) {
  try {
    return await requestFn(path);
  } catch (_) {
    return fallback;
  }
}
