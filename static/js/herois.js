// Heróis conhecidos: lista, busca e ficha das fichas prontas da Marvel e da DC (sem gerador).

const opcoes = window.OPCOES;
const el = (id) => document.getElementById(id);
let todos = [];

const DESCRICAO_DA_EDITORA = {
  marvel: "Conversões dos perfis do Marvel Files (M&M 2ª edição) para a 3ª edição, com notas de conversão.",
  dc: "Fichas publicadas nos livros DC Adventures: Heroes and Villains (M&M 3ª edição), no texto original em inglês.",
};

function escapar(texto) {
  return String(texto ?? "")
    .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
}

// Sem acentos e em minúsculas, para "arcanjo" achar "Arcanjo" e "fenix" achar "Fênix".
const normalizar = (texto) => String(texto ?? "").normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase();

const editora = () => document.querySelector('input[name="editora"]:checked').value;

function lembrar(chave, valor) {
  try { localStorage.setItem(chave, valor); } catch { /* armazenamento indisponível */ }
}

function lembrado(chave) {
  try { return localStorage.getItem(chave); } catch { return null; }
}

function mostrarMensagem(texto) {
  el("mensagem").textContent = texto;
  el("mensagem").classList.toggle("erro", Boolean(texto));
}

function filtrados() {
  const termos = normalizar(el("busca-heroi").value).split(/\s+/).filter(Boolean);
  return todos.filter((h) => h.editora === editora()).filter((h) => {
    const texto = normalizar([h.nome, h.nome_pt, ...h.termos].join(" "));
    return termos.every((t) => texto.includes(t));
  });
}

function desenharLista() {
  const lista = filtrados();
  const nomeDaEditora = opcoes.editoras.find((e) => e.id === editora()).nome;
  el("contagem-herois").textContent = el("busca-heroi").value.trim()
    ? `${lista.length} de ${todos.filter((h) => h.editora === editora()).length} personagens da ${nomeDaEditora}`
    : `${lista.length} personagens da ${nomeDaEditora}`;
  el("editora-descricao").textContent = DESCRICAO_DA_EDITORA[editora()] || "";
  const aberta = location.hash.slice(1);
  el("lista-herois").innerHTML = lista.length
    ? lista.map((h) => `<li><button type="button" class="item-heroi" data-id="${escapar(h.id)}"
        aria-current="${h.id === aberta}">
        <strong>${escapar(h.nome_pt || h.nome)}</strong>${h.nome_pt && h.nome !== h.nome_pt ? ` <span class="discreto">(${escapar(h.nome)})</span>` : ""}
        <small>NP ${escapar(h.np ?? "—")}${h.volume ? ` · ${escapar(h.volume)}, p. ${escapar(h.pagina)}` : ""}</small></button></li>`).join("")
    : "<li class='vazio'>Nenhum personagem encontrado.</li>";
}

function desenharFicha(f) {
  const habilidades = Object.entries(f.habilidades)
    .map(([nome, valor]) => `<div><dt>${escapar(nome)}</dt><dd>${escapar(valor)}</dd></div>`).join("");
  const secoes = f.secoes.map((s) => `<h3>${escapar(s.titulo)}</h3>` + (s.itens.length > 1
    ? `<ul>${s.itens.map((i) => `<li>${escapar(i)}</li>`).join("")}</ul>`
    : `<p>${escapar(s.itens[0])}</p>`)).join("");
  el("ficha-heroi").innerHTML = `
    <header>
      <h2>${escapar(f.nome_pt || f.nome)}</h2>
      ${f.nome_pt && f.nome !== f.nome_pt ? `<p class="subtitulo">${escapar(f.nome)}</p>` : ""}
      <p class="discreto">NP ${escapar(f.np ?? "—")}${f.pp ? ` · ${escapar(f.pp)} ${escapar(f.pp_rotulo)}` : ""}
        · ${escapar(f.status)}</p>
    </header>
    <dl class="habilidades-heroi">${habilidades}</dl>
    ${secoes}
    <footer>
      <div class="acoes-ficha">
        <a class="botao" href="/herois/${f.id.split("/").map(encodeURIComponent).join("/")}.pdf" download
          title="Preenche a ficha editável oficial de M&amp;M">PDF padrão</a>
        <button type="button" class="botao destaque" id="imprimir-ficha"
          title="Abre a impressão com a ficha como na tela; escolha &quot;Salvar como PDF&quot;">PDF personalizado</button>
      </div>
      <p class="discreto">Fonte: ${escapar(f.fonte)}</p>
    </footer>`;
  el("imprimir-ficha").addEventListener("click", () => imprimirFicha(f.nome_pt || f.nome));
  el("ficha-heroi").hidden = false;
}

// O navegador sugere o título da página como nome do PDF salvo; durante a impressão ele vira o nome do personagem.
function imprimirFicha(nome) {
  const titulo = document.title;
  document.title = nome;
  window.addEventListener("afterprint", () => { document.title = titulo; }, { once: true });
  window.print();
}

async function abrirFicha(id) {
  try {
    const resposta = await fetch(`/api/herois/${id.split("/").map(encodeURIComponent).join("/")}`);
    const dados = await resposta.json();
    if (!resposta.ok) throw new Error(dados.erro || "Não consegui abrir a ficha.");
    desenharFicha(dados.ficha);
    history.replaceState(null, "", `#${id}`);
    document.querySelectorAll(".item-heroi").forEach((b) => b.setAttribute("aria-current", b.dataset.id === id));
    if (window.matchMedia("(max-width: 800px)").matches) el("ficha-heroi").scrollIntoView({ behavior: "smooth" });
    mostrarMensagem("");
  } catch (erro) {
    mostrarMensagem(erro.message);
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  el("genero").innerHTML = opcoes.generos
    .map((g) => `<option value="${escapar(g.id)}">${escapar(g.nome)}</option>`).join("");
  el("genero").value = opcoes.genero.id;
  el("genero").addEventListener("change", () => {
    window.location.search = `?genero=${encodeURIComponent(el("genero").value)}`;
  });

  // Uma ficha aberta pelo link (#marvel/archangel) escolhe a editora dela; senão, vale a última usada.
  const doLink = location.hash.slice(1).split("/")[0];
  const inicial = opcoes.editoras.some((e) => e.id === doLink) ? doLink : lembrado("editora-herois");
  const radio = document.querySelector(`input[name="editora"][value="${CSS.escape(inicial || "")}"]`);
  if (radio) radio.checked = true;

  document.querySelectorAll('input[name="editora"]').forEach((r) => r.addEventListener("change", () => {
    lembrar("editora-herois", editora());
    desenharLista();
  }));
  el("busca-heroi").addEventListener("input", desenharLista);
  el("lista-herois").addEventListener("click", (evento) => {
    const botao = evento.target.closest(".item-heroi");
    if (botao) abrirFicha(botao.dataset.id);
  });

  try {
    const resposta = await fetch("/api/herois");
    todos = (await resposta.json()).herois;
    desenharLista();
    if (location.hash.length > 1) abrirFicha(decodeURIComponent(location.hash.slice(1)));
  } catch {
    el("contagem-herois").textContent = "Não consegui carregar a lista de personagens.";
  }
});
