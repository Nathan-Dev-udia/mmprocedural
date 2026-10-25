// Bestiário: catálogo de criaturas e monstros organizado por famílias e variantes, com filtros em tempo real e download em PDF.

(function () {
  const el = (id) => document.getElementById(id);
  let todas = [];
  let criaturaAtual = null;
  let inicializado = false;

  function escapar(texto) {
    return String(texto ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  const normalizar = (texto) =>
    String(texto ?? "")
      .normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase();

  function faixaNpValida(np, faixaId) {
    if (!faixaId || faixaId === "todos") return true;
    if (faixaId === "1-3") return np >= 1 && np <= 3;
    if (faixaId === "4-6") return np >= 4 && np <= 6;
    if (faixaId === "7-9") return np >= 7 && np <= 9;
    if (faixaId === "10+") return np >= 10;
    return true;
  }

  function filtrados() {
    const genero = el("bestiario-genero") ? el("bestiario-genero").value : "todos";
    const tipo = el("bestiario-tipo") ? el("bestiario-tipo").value : "todos";
    const npFaixa = el("bestiario-np") ? el("bestiario-np").value : "todos";
    const papel = el("bestiario-papel") ? el("bestiario-papel").value : "todos";
    const agrupar = el("bestiario-agrupar") ? el("bestiario-agrupar").checked : false;
    const termos = normalizar(el("bestiario-busca") ? el("bestiario-busca").value : "")
      .split(/\s+/)
      .filter(Boolean);

    // 1. Filtro base
    const encontradas = todas.filter((c) => {
      if (genero !== "todos" && c.genero !== genero) return false;
      if (tipo !== "todos" && c.tipo !== tipo) return false;
      if (papel !== "todos" && c.papel !== papel) return false;
      if (!faixaNpValida(c.np, npFaixa)) return false;

      if (termos.length > 0) {
        const texto = normalizar(
          [c.nome, c.genero, c.genero_nome, c.familia, c.variante, c.tipo, c.subtipo, c.papel, c.tamanho, ...(c.ambientes || []), ...(c.termos || [])].join(" ")
        );
        if (!termos.every((t) => texto.includes(t))) return false;
      }

      return true;
    });

    // 2. Se estiver agrupando por família e o usuário NÃO estiver digitando uma busca específica,
    // mostramos apenas a criatura principal (padrao) de cada família.
    if (agrupar && termos.length === 0) {
      const vistas = new Set();
      const agrupadas = [];
      for (const c of encontradas) {
        const chave = `${c.genero}:${c.familia}`;
        if (!vistas.has(chave)) {
          vistas.add(chave);
          // Prefere a criatura padrão se houver, ou a primeira encontrada
          const padraoDaFamilia = encontradas.find((x) => `${x.genero}:${x.familia}` === chave && x.padrao) || c;
          agrupadas.push(padraoDaFamilia);
        }
      }
      return agrupadas;
    }

    return encontradas;
  }

  function desenharLista() {
    if (!el("lista-criaturas") || !el("contagem-criaturas")) return;
    const lista = filtrados();
    const total = todas.length;
    const agrupar = el("bestiario-agrupar") && el("bestiario-agrupar").checked;

    el("contagem-criaturas").textContent =
      lista.length === total
        ? `${total} criaturas no catálogo`
        : agrupar
        ? `${lista.length} famílias encontradas`
        : `${lista.length} de ${total} criaturas encontradas`;

    const aberta = location.hash.startsWith("#bestiario/") ? location.hash.slice(12) : "";
    el("lista-criaturas").innerHTML = lista.length
      ? lista
          .map((c) => {
            const ehFamilia = c.total_variantes > 1;
            const titulo = agrupar && ehFamilia ? c.familia : c.nome;
            const subtituloVariante = agrupar && ehFamilia
              ? `<span class="badge-variantes">${c.total_variantes} variantes</span>`
              : c.variante && c.variante !== c.nome
              ? `<span class="badge-papel">${escapar(c.variante)}</span>`
              : "";

            return `<li>
            <button type="button" class="item-heroi item-criatura" data-id="${escapar(c.id)}"
              aria-current="${c.id === aberta}">
              <div class="info-criatura">
                <strong>${escapar(titulo)}</strong>
                <div class="tags-criatura">
                  <span class="badge-tipo">${escapar(c.tipo)}</span>
                  <span class="badge-papel">${escapar(c.papel)}</span>
                  ${subtituloVariante}
                </div>
              </div>
              <small class="badge-np">NP ${escapar(c.np ?? "—")}</small>
            </button>
          </li>`;
          })
          .join("")
      : "<li class='vazio'>Nenhuma criatura encontrada para estes filtros.</li>";
  }

  function gerarBlocoTexto(f) {
    const linhas = [
      `=== ${f.nome.toUpperCase()} (NP ${f.np}) ===`,
      `Gênero: ${f.genero_nome || f.genero} | Família: ${f.familia}${f.variante ? ` (${f.variante})` : ""} | Papel: ${f.papel} | Porte: ${f.tamanho}`,
      f.ambientes && f.ambientes.length ? `Ambientes: ${f.ambientes.join(", ")}` : "",
      "",
      "HABILIDADES:",
      Object.entries(f.habilidades)
        .map(([k, v]) => `${k} ${v >= 0 ? `+${v}` : v}`)
        .join("  |  "),
      "",
    ];

    for (const s of f.secoes) {
      linhas.push(`${s.titulo.toUpperCase()}:`);
      for (const item of s.itens) {
        linhas.push(`  • ${item}`);
      }
      linhas.push("");
    }

    if (f.descricao) linhas.push(`Descrição: ${f.descricao}`);
    if (f.tatica) linhas.push(`Tática: ${f.tatica}`);
    linhas.push(`Fonte: ${f.fonte}`);

    return linhas.filter((l) => l !== "").join("\n");
  }

  function copiarBlocoTexto() {
    if (!criaturaAtual) return;
    const texto = gerarBlocoTexto(criaturaAtual);
    navigator.clipboard.writeText(texto).then(() => {
      const botao = el("btn-copiar-criatura");
      if (!botao) return;
      const textoOriginal = botao.textContent;
      botao.textContent = "Copiado!";
      botao.classList.add("sucesso");
      setTimeout(() => {
        botao.textContent = textoOriginal;
        botao.classList.remove("sucesso");
      }, 2000);
    });
  }

  function desenharFicha(f) {
    if (!el("ficha-criatura")) return;
    criaturaAtual = f;
    const habilidades = Object.entries(f.habilidades)
      .map(
        ([nome, valor]) =>
          `<div><dt>${escapar(nome)}</dt><dd>${valor === null ? "—" : escapar(valor)}</dd></div>`
      )
      .join("");

    const secoes = f.secoes
      .map(
        (s) =>
          `<h3>${escapar(s.titulo)}</h3>` +
          (s.itens.length > 1
            ? `<ul>${s.itens.map((i) => `<li>${escapar(i)}</li>`).join("")}</ul>`
            : `<p>${escapar(s.itens[0])}</p>`)
      )
      .join("");

    const ambientesHtml =
      f.ambientes && f.ambientes.length
        ? `<p class="discreto"><strong>Ambientes:</strong> ${escapar(f.ambientes.join(", "))}</p>`
        : "";

    const descricaoHtml = f.descricao
      ? `<p class="descricao-criatura"><em>${escapar(f.descricao)}</em></p>`
      : "";

    const variantesHtml =
      f.variantes && f.variantes.length > 1
        ? `<div class="variantes-container">
            <span class="variantes-titulo">Variantes da Família ${escapar(f.familia)} (${f.variantes.length}):</span>
            <div class="variantes-chips">
              ${f.variantes
                .map(
                  (v) => `
                <button type="button" class="chip-variante ${v.atual ? "ativo" : ""}" data-id="${escapar(v.id)}">
                  <strong>${escapar(v.variante)}</strong> <small>NP ${escapar(v.np)}</small>
                </button>`
                )
                .join("")}
            </div>
          </div>`
        : "";

    el("ficha-criatura").innerHTML = `
      <header>
        <div class="cabecalho-criatura">
          <h2>${escapar(f.nome)}</h2>
          <span class="badge-np-ficha">NP ${escapar(f.np ?? "—")}</span>
        </div>
        <p class="subtitulo">${escapar(f.tipo)}${f.subtipo ? ` · ${escapar(f.subtipo)}` : ""} · ${escapar(f.papel)} · Porte ${escapar(f.tamanho)}</p>
        ${ambientesHtml}
        ${descricaoHtml}
        ${variantesHtml}
      </header>
      <dl class="habilidades-heroi">${habilidades}</dl>
      ${secoes}
      <footer>
        <div class="acoes-ficha">
          <a class="botao" href="/bestiario/${f.id.split("/").map(encodeURIComponent).join("/")}.pdf" download>Baixar ficha em PDF</a>
          <button type="button" id="btn-copiar-criatura" class="botao secundario">Copiar bloco de texto</button>
        </div>
        <p class="discreto">Fonte: ${escapar(f.fonte)}</p>
      </footer>`;

    el("ficha-criatura").hidden = false;
    const btnCopiar = el("btn-copiar-criatura");
    if (btnCopiar) btnCopiar.addEventListener("click", copiarBlocoTexto);

    // Eventos dos chips de variantes
    el("ficha-criatura").querySelectorAll(".chip-variante").forEach((chip) => {
      chip.addEventListener("click", () => {
        abrirFicha(chip.dataset.id);
      });
    });
  }

  async function abrirFicha(id) {
    try {
      const resposta = await fetch(`/api/bestiario/${id.split("/").map(encodeURIComponent).join("/")}`);
      const dados = await resposta.json();
      if (!resposta.ok) throw new Error(dados.erro || "Não consegui abrir a ficha.");
      desenharFicha(dados.ficha);
      history.replaceState(null, "", `#bestiario/${id}`);
      document.querySelectorAll(".item-criatura").forEach((b) => b.setAttribute("aria-current", b.dataset.id === id));
      if (window.matchMedia("(max-width: 800px)").matches) el("ficha-criatura").scrollIntoView({ behavior: "smooth" });
    } catch (erro) {
      console.error(erro);
    }
  }

  async function inicializarBestiario() {
    if (inicializado || !el("aba-bestiario")) return;
    inicializado = true;

    if (el("bestiario-busca")) el("bestiario-busca").addEventListener("input", desenharLista);
    if (el("bestiario-genero")) el("bestiario-genero").addEventListener("change", desenharLista);
    if (el("bestiario-tipo")) el("bestiario-tipo").addEventListener("change", desenharLista);
    if (el("bestiario-np")) el("bestiario-np").addEventListener("change", desenharLista);
    if (el("bestiario-papel")) el("bestiario-papel").addEventListener("change", desenharLista);
    if (el("bestiario-agrupar")) el("bestiario-agrupar").addEventListener("change", desenharLista);

    if (el("lista-criaturas")) {
      el("lista-criaturas").addEventListener("click", (e) => {
        const botao = e.target.closest(".item-criatura");
        if (botao) abrirFicha(botao.dataset.id);
      });
    }

    try {
      const resposta = await fetch("/api/bestiario");
      const dados = await resposta.json();
      todas = dados.criaturas || [];
      desenharLista();

      const hash = location.hash.startsWith("#bestiario/") ? location.hash.slice(12) : null;
      const inicial = hash || (todas[0] ? todas[0].id : null);
      if (inicial) abrirFicha(inicial);
    } catch (erro) {
      console.error("Erro ao carregar bestiário:", erro);
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    // Escuta clique na aba bestiário
    document.querySelectorAll('.aba[data-aba="bestiario"]').forEach((btn) => {
      btn.addEventListener("click", inicializarBestiario);
    });

    // Se a aba inicial já for o bestiário
    const params = new URLSearchParams(location.search);
    const abaUrl = params.get("aba");
    let abaSalva = null;
    try { abaSalva = localStorage.getItem("aba"); } catch (_) {}

    if (abaUrl === "bestiario" || (!abaUrl && abaSalva === "bestiario") || location.hash.startsWith("#bestiario/")) {
      inicializarBestiario();
    }
  });
})();
