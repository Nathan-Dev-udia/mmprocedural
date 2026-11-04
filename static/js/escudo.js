// Escudo do Mestre: troca de sub-aba (lembrada no navegador) e impressão de todas as abas de uma vez.

function trocarAbaDoEscudo(id) {
  const abas = [...document.querySelectorAll(".escudo-aba")];
  if (!abas.some((a) => a.dataset.escudo === id)) id = abas[0]?.dataset.escudo;
  document.querySelectorAll(".escudo-abas .passo-aba").forEach((b) => b.setAttribute("aria-selected", b.dataset.escudo === id));
  abas.forEach((a) => { a.hidden = a.dataset.escudo !== id; });
  try { localStorage.setItem("aba-do-escudo", id); } catch { /* armazenamento indisponível */ }
}

document.addEventListener("DOMContentLoaded", () => {
  if (!document.getElementById("aba-escudo")) return;
  document.querySelectorAll(".escudo-abas .passo-aba").forEach((b) => {
    b.addEventListener("click", () => trocarAbaDoEscudo(b.dataset.escudo));
  });
  let inicial = null;
  try { inicial = localStorage.getItem("aba-do-escudo"); } catch { /* armazenamento indisponível */ }
  trocarAbaDoEscudo(inicial);
  // Na impressão saem todas as abas, cada uma numa folha (o CSS de impressão cuida do resto).
  document.getElementById("escudo-imprimir").addEventListener("click", () => window.print());
});
