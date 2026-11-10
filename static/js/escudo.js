// Escudo do Mestre: troca de sub-aba (lembrada no navegador) e impressão de todas as abas de uma vez.

function trocarAbaDoEscudo(id) {
  const abas = [...document.querySelectorAll(".escudo-aba")];
  if (!abas.some((a) => a.dataset.escudo === id)) id = abas[0]?.dataset.escudo;
  document.querySelectorAll(".escudo-abas .passo-aba").forEach((b) => b.setAttribute("aria-selected", b.dataset.escudo === id));
  abas.forEach((a) => { a.hidden = a.dataset.escudo !== id; });
  try { localStorage.setItem("aba-do-escudo", id); } catch { /* armazenamento indisponível */ }
}

// Letalidade (heroica, equilibrada ou mortal): mostra as tabelas daquele modo e leva a escolha aos downloads.
function trocarLetalidade(modo) {
  const seletor = document.getElementById("escudo-letalidade");
  if (!seletor) return;
  if (![...seletor.options].some((o) => o.value === modo)) modo = seletor.dataset.padrao;
  seletor.value = modo;
  document.querySelectorAll(".escudo-bloco[data-letalidade]").forEach((b) => { b.hidden = b.dataset.letalidade !== modo; });
  document.querySelectorAll(".escudo-download").forEach((a) => { a.href = `${a.dataset.base}?letalidade=${modo}`; });
  const descricao = document.getElementById("escudo-letalidade-descricao");
  if (descricao) descricao.textContent = seletor.selectedOptions[0]?.dataset.descricao || "";
  try { localStorage.setItem("letalidade-do-escudo", modo); } catch { /* armazenamento indisponível */ }
}

document.addEventListener("DOMContentLoaded", () => {
  if (!document.getElementById("aba-escudo")) return;
  document.querySelectorAll(".escudo-abas .passo-aba").forEach((b) => {
    b.addEventListener("click", () => trocarAbaDoEscudo(b.dataset.escudo));
  });
  let inicial = null;
  try { inicial = localStorage.getItem("aba-do-escudo"); } catch { /* armazenamento indisponível */ }
  trocarAbaDoEscudo(inicial);
  const seletor = document.getElementById("escudo-letalidade");
  seletor.addEventListener("change", () => trocarLetalidade(seletor.value));
  let letalidade = null;
  try { letalidade = localStorage.getItem("letalidade-do-escudo"); } catch { /* armazenamento indisponível */ }
  trocarLetalidade(letalidade || seletor.dataset.padrao);
  // Na impressão saem todas as abas, cada uma numa folha (o CSS de impressão cuida do resto).
  document.getElementById("escudo-imprimir").addEventListener("click", () => window.print());
});
