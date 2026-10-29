// Rolagem de eventos de viagem: categoria (gênero), situação, rolagem do período (dados físicos opcionais),
// texto para narrar e diário. Cada categoria guarda o próprio dia, clima e diário.

(function () {
  const el = (id) => document.getElementById(id);
  const CAMPOS = { area: "areas", periodo: "periodos", estacao: "estacoes", terreno: "terrenos", situacao: "situacoes" };
  const PADRAO = { area: "Média", periodo: "Manhã", estacao: "Primavera", terreno: "Estrada", situacao: "Na estrada" };
  const CHAVE_CATEGORIA = "viagem-categoria";
  let categoria = null;
  let opcoes = null;
  let inicializado = false;
  // O que atravessa os períodos: dia, clima do dia, se já houve combate hoje e o diário.
  const novaViagem = (situacao = { ...PADRAO }) => ({ dia: 1, clima: null, combateHoje: false, diario: [], situacao });
  let viagem = novaViagem();

  function escapar(texto) {
    return String(texto ?? "")
      .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
  }

  function salvar() {
    try { localStorage.setItem(`viagem:${categoria}`, JSON.stringify(viagem)); } catch { /* armazenamento indisponível */ }
  }

  function carregar() {
    viagem = novaViagem();
    try {
      const salvo = JSON.parse(localStorage.getItem(`viagem:${categoria}`) || "null");
      if (salvo) viagem = { ...viagem, ...salvo, situacao: { ...PADRAO, ...salvo.situacao } };
    } catch { /* armazenamento indisponível */ }
  }

  function situacaoAtual() {
    const s = {};
    for (const campo of Object.keys(CAMPOS)) s[campo] = el(`viagem-${campo}`).value;
    return s;
  }

  function descrever(campo) {
    const item = opcoes[CAMPOS[campo]].find((i) => i.id === el(`viagem-${campo}`).value);
    el(`viagem-${campo}-descricao`).textContent = item ? item.descricao : "";
  }

  function desenharDia() {
    el("viagem-dia").textContent = `Dia ${viagem.dia}`;
    el("viagem-clima-atual").textContent = viagem.clima
      ? `Clima: ${viagem.clima}${viagem.combateHoje ? " · já houve combate hoje" : ""}`
      : "Clima: ainda não rolado (sai no primeiro período do dia)";
  }

  function desenharDiario() {
    el("viagem-diario-bloco").hidden = viagem.diario.length === 0;
    el("viagem-diario").innerHTML = viagem.diario.map((d) => `<li>${escapar(d)}</li>`).join("");
  }

  // Na rolagem vão só os campos ativos; na prévia vão todos, porque um campo desligado pode voltar a valer
  // se o mestre mudar um dado anterior (ex.: o d20 que dava "nada acontece").
  function dadosInformados(incluirDesligados = false) {
    const dados = {};
    document.querySelectorAll("[data-viagem-dado]").forEach((input) => {
      if (input.value !== "" && (incluirDesligados || !input.disabled)) dados[input.dataset.viagemDado] = Number(input.value);
    });
    return dados;
  }

  // ---------------------------------------------------------------- prévia dos dados físicos

  let pedidoDaPrevia = 0;
  let esperaDaPrevia = null;

  function agendarPrevia() {
    clearTimeout(esperaDaPrevia);
    esperaDaPrevia = setTimeout(atualizarPrevia, 150);
  }

  async function atualizarPrevia() {
    if (!opcoes || !document.querySelector("details.viagem-dados").open) return;
    const pedido = ++pedidoDaPrevia;
    const resposta = await fetch("/api/viagem/previa", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ categoria, situacao: situacaoAtual(), dados: dadosInformados(true), clima_atual: viagem.clima }),
    });
    const p = await resposta.json();
    if (pedido !== pedidoDaPrevia) return;  // chegou uma resposta mais nova
    const aviso = el("viagem-previa");
    aviso.classList.toggle("erro", !resposta.ok);
    if (!resposta.ok) {
      aviso.textContent = p.erro;
      return;
    }
    aviso.textContent = p.mensagem;
    const resolvidas = Object.fromEntries(p.etapas.map((e) => [e.id, e.resultado]));
    document.querySelectorAll("[data-viagem-dado]").forEach((input) => {
      const chave = input.dataset.viagemDado;
      const dispensada = p.dispensadas.includes(chave);
      input.disabled = dispensada;
      input.closest(".campo").classList.toggle("viagem-proximo-dado", p.proxima === chave);
      input.closest(".campo").classList.toggle("viagem-dispensado", dispensada);
      document.querySelector(`[data-viagem-previa="${chave}"]`).textContent =
        chave in resolvidas ? `→ ${resolvidas[chave]}` : dispensada ? "não precisa" : p.proxima === chave ? "← próximo" : "";
    });
  }

  function desenharResultado(r) {
    const corpo = el("viagem-etapas").querySelector("tbody");
    corpo.innerHTML = r.etapas.map((e) => `
      <tr>
        <td>${escapar(e.etapa)}</td>
        <td class="viagem-dado"><span>${escapar(e.dado)}</span> <strong>${escapar(e.valor)}</strong>${e.informado ? " <em>(seu)</em>" : ""}</td>
        <td class="viagem-resultado">${escapar(e.resultado)}</td>
        <td>${escapar(e.detalhe)}</td>
      </tr>`).join("");
    el("viagem-etapas").hidden = false;

    el("viagem-avisos").innerHTML = r.avisos.map((a) => `<li>${escapar(a)}</li>`).join("");
    el("viagem-narrar").innerHTML = r.narrar.map((linha) => {
      let extra = "";
      if (linha.regra) extra += `<br><small>Regra: ${escapar(linha.regra)}</small>`;
      if (linha.ficha) {
        extra += `<br><small>Ficha base: ${escapar(linha.ficha)}</small> `;
        extra += linha.bestiario_id
          ? `<a class="link" href="/?aba=bestiario#bestiario/${escapar(linha.bestiario_id)}" target="_blank" rel="noopener">ver ficha ↗</a>`
          : `<small>(gere na aba Fichas de NPC)</small>`;
      }
      return `<div><dt>${escapar(linha.rotulo)}</dt><dd>${escapar(linha.texto)}${extra}</dd></div>`;
    }).join("");
    el("viagem-narrar-bloco").hidden = false;
  }

  function anotarNoDiario(r, situacao) {
    let resumo = "nada acontece";
    if (r.evento) {
      resumo = `${r.tipo}: ${r.evento.nome}`;
      if (r.criatura) resumo += r.tipo === "Pista / presságio" ? ` (rastro de ${r.criatura.nome})` : ` — ${r.criatura.nome}`;
      if (r.intensidade) resumo += `, ${r.intensidade.nome.toLowerCase()}`;
    }
    viagem.diario.push(`Dia ${viagem.dia} · ${situacao.periodo} · ${r.clima.nome} · ${resumo}`);
  }

  async function rolarPeriodo() {
    const situacao = situacaoAtual();
    const mensagem = el("mensagem");
    mensagem.textContent = "";
    mensagem.classList.remove("erro");
    try {
      const resposta = await fetch("/api/viagem/rolar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ categoria, situacao, dados: dadosInformados(), clima_atual: viagem.clima, combate_hoje: viagem.combateHoje }),
      });
      const r = await resposta.json();
      if (!resposta.ok) throw new Error(r.erro || "Não consegui rolar.");
      viagem.clima = r.clima.nome;
      viagem.combateHoje = viagem.combateHoje || r.combate;
      anotarNoDiario(r, situacao);
      document.querySelectorAll("[data-viagem-dado]").forEach((input) => { input.value = ""; });
      atualizarPrevia();
      desenharResultado(r);
      desenharDia();
      desenharDiario();
      salvar();
    } catch (erro) {
      mensagem.textContent = erro.message;
      mensagem.classList.add("erro");
    }
  }

  function novoDia() {
    viagem.dia += 1;
    viagem.clima = null;
    viagem.combateHoje = false;
    el("viagem-periodo").value = opcoes.periodos[0].id;
    mudouCampo("periodo");
    desenharDia();
  }

  function proximoPeriodo() {
    const ids = opcoes.periodos.map((p) => p.id);
    const atual = ids.indexOf(el("viagem-periodo").value);
    if (atual === ids.length - 1) return novoDia();
    el("viagem-periodo").value = ids[atual + 1];
    mudouCampo("periodo");
  }

  function mudouCampo(campo) {
    descrever(campo);
    viagem.situacao = situacaoAtual();
    salvar();
    agendarPrevia();
  }

  async function abrirCategoria(id, categorias) {
    categoria = id;
    try { localStorage.setItem(CHAVE_CATEGORIA, id); } catch { /* armazenamento indisponível */ }
    const genero = window.OPCOES && window.OPCOES.genero;
    const escolhida = categorias.find((c) => c.id === id);
    let descricao = escolhida.descricao;
    if (genero && !categorias.some((c) => c.id === genero.id)) {
      descricao = `Ainda não há rolagens de ${genero.nome}. ${descricao}`;
    }
    el("viagem-categoria-descricao").textContent = descricao;

    const resposta = await fetch(`/api/viagem/${encodeURIComponent(id)}`);
    opcoes = await resposta.json();
    carregar();
    for (const [campo, lista] of Object.entries(CAMPOS)) {
      const select = el(`viagem-${campo}`);
      select.innerHTML = opcoes[lista].map((i) => `<option value="${escapar(i.id)}">${escapar(i.id)}</option>`).join("");
      const salvo = viagem.situacao[campo];
      if (opcoes[lista].some((i) => i.id === salvo)) select.value = salvo;
      descrever(campo);
    }
    // O resultado na tela é da categoria anterior.
    el("viagem-etapas").hidden = true;
    el("viagem-narrar-bloco").hidden = true;
    desenharDia();
    desenharDiario();
    atualizarPrevia();
  }

  async function inicializar() {
    if (inicializado || !el("aba-viagem")) return;
    inicializado = true;
    let categorias;
    try {
      categorias = (await (await fetch("/api/viagem")).json()).categorias;
    } catch (erro) {
      console.error("Erro ao carregar a rolagem de eventos:", erro);
      return;
    }
    // Abre no gênero da página; se ele ainda não tem rolagens, na última categoria usada; senão, na primeira.
    let salva = null;
    try { salva = localStorage.getItem(CHAVE_CATEGORIA); } catch { /* armazenamento indisponível */ }
    const genero = window.OPCOES && window.OPCOES.genero && window.OPCOES.genero.id;
    const inicial = [genero, salva].find((id) => categorias.some((c) => c.id === id)) || categorias[0].id;
    const seletor = el("viagem-categoria");
    seletor.innerHTML = categorias.map((c) => `<option value="${escapar(c.id)}">${escapar(c.nome)}</option>`).join("");
    seletor.value = inicial;
    seletor.addEventListener("change", () => abrirCategoria(seletor.value, categorias));
    for (const campo of Object.keys(CAMPOS)) el(`viagem-${campo}`).addEventListener("change", () => mudouCampo(campo));
    document.querySelectorAll("[data-viagem-dado]").forEach((input) => input.addEventListener("input", agendarPrevia));
    document.querySelector("details.viagem-dados").addEventListener("toggle", atualizarPrevia);
    el("viagem-rolar").addEventListener("click", rolarPeriodo);
    el("viagem-proximo").addEventListener("click", proximoPeriodo);
    el("viagem-novo-dia").addEventListener("click", () => { novoDia(); salvar(); });
    el("viagem-limpar-diario").addEventListener("click", () => {
      viagem = novaViagem(situacaoAtual());
      salvar();
      desenharDia();
      desenharDiario();
      atualizarPrevia();
    });
    await abrirCategoria(inicial, categorias);
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('.aba[data-aba="viagem"]').forEach((b) => b.addEventListener("click", inicializar));
    let abaSalva = null;
    try { abaSalva = localStorage.getItem("aba"); } catch { /* armazenamento indisponível */ }
    const abaUrl = new URLSearchParams(location.search).get("aba");
    if (abaUrl === "viagem" || (!abaUrl && abaSalva === "viagem")) inicializar();
  });
})();
