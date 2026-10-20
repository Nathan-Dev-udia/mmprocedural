// Interface do gerador: abas, formulários, chamadas à API e cartões das fichas.

const opcoes = window.OPCOES;
const estado = {
  npc: { parametros: null, npcs: [], avisos: [] },
  pj: { parametros: null, personagem: null },
};

const el = (id) => document.getElementById(id);

const ROTULO_STATUS = {
  invalida: "status-invalida",
  conceitual: "status-conceitual",
  parcial: "status-parcial",
  calculada: "status-calculada",
  validada: "status-validada",
};

const ROTULO_DADOS = {
  validado: "dados do livro",
  ilustrativo: "ilustrativo",
  pendente: "pendente",
  conceitual: "conceitual",
};

function escapar(texto) {
  return String(texto ?? "")
    .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function lista(itens) {
  if (!itens || itens.length === 0) return "<p class='vazio'>—</p>";
  return "<ul>" + itens.map((i) => `<li>${escapar(i)}</li>`).join("") + "</ul>";
}

function opcoesDeSelect(itens, rotulo = (i) => i.nome, valor = (i) => i.id) {
  return itens.map((i) => `<option value="${escapar(valor(i))}">${escapar(rotulo(i))}</option>`).join("");
}

// ---------------------------------------------------------------- abas

function trocarAba(nome) {
  document.querySelectorAll(".aba").forEach((b) => b.setAttribute("aria-selected", b.dataset.aba === nome));
  document.querySelectorAll(".painel-aba").forEach((p) => { p.hidden = p.id !== `aba-${nome}`; });
  try { localStorage.setItem("aba", nome); } catch { /* armazenamento indisponível */ }
}

// ---------------------------------------------------------------- API e arquivos

async function chamar(url, corpo) {
  const resposta = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...corpo, genero: opcoes.genero.id }),
  });
  const dados = await resposta.json();
  if (!resposta.ok) throw new Error(dados.erro || "Erro desconhecido.");
  return dados;
}

function mostrarMensagem(texto, ehErro = false) {
  const m = el("mensagem");
  m.textContent = texto;
  m.classList.toggle("erro", ehErro);
  if (texto) setTimeout(() => { if (m.textContent === texto) m.textContent = ""; }, 5000);
}

function salvarArquivo(blob, nome) {
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = nome;
  link.click();
  setTimeout(() => URL.revokeObjectURL(link.href), 1000);
}

function nomeDeArquivo(texto) {
  return texto.normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase()
    .replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "") || "ficha";
}

// Tela de "carregando" por cima da página enquanto o servidor monta o arquivo.
function mostrarCarregando(texto) {
  el("carregando-texto").textContent = texto;
  el("carregando").hidden = false;
}

function esconderCarregando() {
  el("carregando").hidden = true;
}

async function baixarDoServidor(url, corpo, nomePadrao, textoCarregando = "Preparando o arquivo…") {
  mostrarCarregando(textoCarregando);
  try {
    const resposta = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(corpo),
    });
    if (!resposta.ok) {
      const erro = await resposta.json().catch(() => ({}));
      throw new Error(erro.erro || "Não consegui gerar o arquivo.");
    }
    salvarArquivo(await resposta.blob(), nomePadrao);
  } catch (erro) {
    mostrarMensagem(erro.message, true);
  } finally {
    esconderCarregando();
  }
}

async function copiar(texto) {
  try {
    await navigator.clipboard.writeText(texto);
    mostrarMensagem("Copiado para a área de transferência.");
  } catch {
    mostrarMensagem("Não consegui copiar. Seu navegador bloqueou a área de transferência.", true);
  }
}

function acaoDeArquivo(acao, ficha) {
  const base = nomeDeArquivo(ficha.nome);
  if (acao === "docx") baixarDoServidor("/api/ficha.docx", { npc: ficha }, `${base}.docx`, "Preparando a ficha em DOCX…");
  if (acao === "pdf") baixarDoServidor("/api/ficha.pdf", { npc: ficha }, `${base}.pdf`, "Preparando a ficha em PDF…");
  if (acao === "txt") salvarArquivo(new Blob([ficha.texto], { type: "text/plain;charset=utf-8" }), `${base}.txt`);
  if (acao === "copiar") copiar(ficha.texto);
}

// ---------------------------------------------------------------- cartão (serve para NPC e PJ)

function cartao(ficha, { regerar = false, aberto = false } = {}) {
  const v = ficha.validacao;
  const e = ficha.exibicao;
  const ehJogador = ficha.tipo === "jogador";
  const chips = ficha.modulos.map((m) => ehJogador
    ? `<span class="chip validado">${escapar(m.nome)} <em>foco</em></span>`
    : `<span class="chip ${m.status_dados}" title="${escapar(m.fonte)}">${escapar(m.nome)}` +
      ` <em>${m.papel} · ${ROTULO_DADOS[m.status_dados]}</em></span>`).join("");
  const limites = v.limites.map((l) =>
    `<tr class="${l.ok ? "" : "falha"}"><td>${escapar(l.nome)}</td><td>${l.valor}</td><td>${l.maximo}</td></tr>`).join("");
  const notas = [
    ...v.problemas.map((p) => `<li class="problema">${escapar(p)}</li>`),
    ...v.pendencias.map((p) => `<li class="pendencia">${escapar(p)}</li>`),
    ...v.avisos.map((a) => `<li class="aviso">${escapar(a)}</li>`),
  ].join("");
  const subtitulo = ehJogador
    ? `${ficha.raca ? `${escapar(ficha.raca.nome)} · ` : ""}${escapar(ficha.arquetipo.nome)} · personagem de jogador · NP ${ficha.np_pretendido}` +
      (ficha.jogador ? ` · jogador: ${escapar(ficha.jogador)}` : "")
    : `${escapar(ficha.arquetipo.nome)} · ficha-base ${escapar(ficha.faixa.nome)} · NP pretendido ` +
      `${ficha.np_pretendido} <span class="discreto">(estimado: ${v.np_efetivo})</span>`;

  return `
  <article class="cartao ${ehJogador ? "cartao-jogador" : ""}" data-uid="${ficha.uid}">
    <header>
      <h2>${escapar(ficha.nome)}</h2>
      <p class="subtitulo">${subtitulo}</p>
      <span class="status ${ROTULO_STATUS[v.status]}">${escapar(v.status_rotulo)}</span>
      ${ficha.repetida ? "<span class='status status-parcial'>Combinação repetida</span>" : ""}
    </header>

    <div class="modulos">${chips}</div>

    <section class="narrativa">
      <h3>Descrição <small>narrativa</small></h3>
      <p>${escapar(ficha.descricao)}</p>
      ${ehJogador ? "" : `<h3>Tática <small>narrativa</small></h3><p>${escapar(ficha.tatica)}</p>`}
    </section>

    <section class="mecanica">
      <h3>Ficha <small>mecânica</small></h3>
      ${ehJogador ? `<p><strong>Habilidades:</strong> ${escapar(e.habilidades)}</p>` : ""}
      <p><strong>Ataques:</strong> Inic ${escapar(e.iniciativa)}; ${e.ataques.map(escapar).join("; ")}</p>
      <p><strong>Defesas:</strong> ${escapar(e.defesas)}</p>
      <p><strong>Equipamento:</strong> ${escapar(e.equipamento.join(", ") || "nenhum")}</p>
      ${e.dinheiro ? `<p><strong>Dinheiro:</strong> ${escapar(e.dinheiro)}</p>` : ""}
      ${!e.dinheiro && ficha.pontos_de_equipamento ? `<p class="discreto">${escapar(e.pontos_equipamento)}</p>` : ""}
      ${e.de_fora ? `<p class="aviso-texto"><strong>Ficou de fora:</strong> ${escapar(e.de_fora)}</p>` : ""}
      <p><strong>Custo:</strong> ${escapar(e.totais)}</p>
      ${ficha.capanga ? "<p class='discreto'>Capanga: não faz críticos contra quem não é capanga; qualquer falha num salvamento aplica o pior resultado.</p>" : ""}
    </section>

    ${e.complicacoes.length ? `<section class="complicacoes"><h3>Complicações</h3>${lista(e.complicacoes)}</section>` : ""}

    <details ${aberto ? "open" : ""}>
      <summary>Ficha completa e validação</summary>
      ${ehJogador ? "" : `<p><strong>Habilidades:</strong> ${escapar(e.habilidades)}</p>`}
      <div class="colunas">
        <div><h4>Perícias</h4>${lista(e.pericias)}</div>
        <div><h4>Vantagens</h4>${lista(e.vantagens)}</div>
      </div>
      ${e.poderes.length ? `<h4>${escapar(ficha.rotulo_poderes || "Poderes")}</h4>${lista(e.poderes)}` : ""}
      <p class="discreto">${escapar(e.pontos_equipamento)}</p>
      <h4>Limites do NP ${v.np_verificado}</h4>
      <table class="limites">
        <thead><tr><th>Item</th><th>Valor</th><th>Máximo</th></tr></thead>
        <tbody>${limites}</tbody>
      </table>
      ${notas ? `<h4>Observações</h4><ul class="notas">${notas}</ul>` : ""}
      <h4>Origem</h4>
      <p class="discreto">${escapar(ficha.faixa.fonte)}. ${escapar(ficha.faixa.observacao)}</p>
    </details>

    <footer>
      ${opcoes.pdf_disponivel ? "<button type='button' class='botao pequeno destaque' data-acao='pdf'>Baixar PDF (ficha editável)</button>" : ""}
      <button type="button" class="botao pequeno ${opcoes.pdf_disponivel ? "" : "destaque"}" data-acao="docx">Baixar DOCX</button>
      <button type="button" class="botao pequeno" data-acao="txt">Baixar TXT</button>
      <button type="button" class="botao pequeno" data-acao="copiar">Copiar texto</button>
      ${regerar ? "<button type='button' class='botao pequeno' data-acao='regerar'>Regerar este</button>" : ""}
    </footer>
  </article>`;
}

// ---------------------------------------------------------------- aba NPC

function prepararAbaNpc() {
  if (!opcoes.arquetipos.length) {
    el("formulario-npc").insertAdjacentHTML("afterend", "<p class='dica'>Este gênero ainda não tem NPCs cadastrados.</p>");
    el("formulario-npc").querySelectorAll("label:not(:first-child), .acoes-formulario").forEach((e) => { e.hidden = true; });
    return;
  }
  el("arquetipo").innerHTML = opcoesDeSelect(opcoes.arquetipos);
  el("estilo").innerHTML = opcoesDeSelect(opcoes.estilos);
  el("quantidade").max = opcoes.quantidade_maxima;
  el("quantidade").value = opcoes.quantidade_padrao;
  el("quantidade-ajuda").textContent = `De 1 a ${opcoes.quantidade_maxima}.`;

  const arquetipoNpc = () => opcoes.arquetipos.find((a) => a.id === el("arquetipo").value);
  // Tipo = módulo principal (ex.: Dragão azul). A lista depende do NP; mantém a escolha se ela ainda existir.
  const atualizarTipos = () => {
    const anterior = el("tipo").value;
    const np = Number(el("np").value);
    const tipos = arquetipoNpc().tipos.filter((t) => t.nps.includes(np));
    el("tipo").innerHTML = `<option value="">Sortear (qualquer tipo)</option>` + opcoesDeSelect(tipos);
    if (tipos.some((t) => t.id === anterior)) el("tipo").value = anterior;
    atualizarDescricaoDoTipo();
  };
  const atualizarDescricaoDoTipo = () => {
    const tipo = arquetipoNpc().tipos.find((t) => t.id === el("tipo").value);
    el("tipo-descricao").textContent = tipo ? tipo.descricao : "Cada NPC do grupo sai com um tipo diferente.";
  };
  const atualizarNps = () => {
    const arquetipo = arquetipoNpc();
    el("np").innerHTML = arquetipo.nps.map((np) => `<option value="${np}">NP ${np}</option>`).join("");
    el("arquetipo-descricao").textContent = arquetipo.descricao;
    atualizarTipos();
  };
  const atualizarEstilo = () => {
    el("estilo-descricao").textContent = opcoes.estilos.find((e) => e.id === el("estilo").value).descricao;
  };
  el("arquetipo").addEventListener("change", atualizarNps);
  el("np").addEventListener("change", atualizarTipos);
  el("tipo").addEventListener("change", atualizarDescricaoDoTipo);
  el("estilo").addEventListener("change", atualizarEstilo);
  atualizarNps();
  atualizarEstilo();

  el("formulario-npc").addEventListener("submit", (evento) => {
    evento.preventDefault();
    gerarNpcs({
      arquetipo: el("arquetipo").value,
      tipo: el("tipo").value,
      np: Number(el("np").value),
      estilo: el("estilo").value,
      quantidade: Number(el("quantidade").value),
    });
  });
  el("gerar-de-novo").addEventListener("click", () => gerarNpcs(estado.npc.parametros));
  el("copiar-todos").addEventListener("click", () =>
    copiar(estado.npc.npcs.map((n) => n.texto).join("\n\n---\n\n")));
  el("baixar-todos").addEventListener("click", () =>
    baixarDoServidor("/api/fichas.zip", { npcs: estado.npc.npcs }, "fichas_npcs.zip", "Juntando todas as fichas…"));
  el("baixar-json").addEventListener("click", () => {
    const p = estado.npc.parametros;
    salvarArquivo(new Blob([JSON.stringify({ parametros: p, npcs: estado.npc.npcs }, null, 2)],
      { type: "application/json" }), `npcs_${p.arquetipo}_np${p.np}.json`);
  });

  el("cartoes").addEventListener("click", (evento) => {
    const botao = evento.target.closest("button[data-acao]");
    if (!botao) return;
    const npc = estado.npc.npcs.find((n) => n.uid === botao.closest(".cartao").dataset.uid);
    if (botao.dataset.acao === "regerar") regerarUm(npc.uid);
    else acaoDeArquivo(botao.dataset.acao, npc);
  });
}

async function gerarNpcs(parametros) {
  try {
    const dados = await chamar("/api/gerar", parametros);
    estado.npc = { parametros, npcs: dados.npcs, avisos: dados.avisos };
    desenharNpcs();
  } catch (erro) {
    mostrarMensagem(erro.message, true);
  }
}

async function regerarUm(uid) {
  const outros = estado.npc.npcs.filter((n) => n.uid !== uid);
  const atual = estado.npc.npcs.find((n) => n.uid === uid);
  try {
    const dados = await chamar("/api/regerar", {
      ...estado.npc.parametros,
      combinacoes: [...outros, atual].map((n) => n.combinacao),
      nomes: outros.map((n) => n.nome),
    });
    estado.npc.npcs = estado.npc.npcs.map((n) => (n.uid === uid ? dados.npc : n));
    desenharNpcs();
  } catch (erro) {
    mostrarMensagem(erro.message, true);
  }
}

function desenharNpcs() {
  const { parametros: p, npcs, avisos } = estado.npc;
  el("resultado-npc").hidden = false;
  const arquetipo = opcoes.arquetipos.find((a) => a.id === p.arquetipo);
  const estilo = opcoes.estilos.find((e) => e.id === p.estilo);
  const tipo = arquetipo.tipos.find((t) => t.id === p.tipo);
  el("resumo").textContent = `${npcs.length} × ${arquetipo.nome}${tipo ? ` (${tipo.nome})` : ""} · NP ${p.np} · ${estilo.nome}`;
  el("avisos").innerHTML = avisos.map((a) => `<li>${escapar(a)}</li>`).join("");
  el("cartoes").innerHTML = npcs.map((n) => cartao(n, { regerar: true })).join("");
}

// ---------------------------------------------------------------- aba Jogador

const pj = () => opcoes.jogador;
const arquetipoBase = () => pj().arquetipos.find((a) => a.id === el("pj-arquetipo").value);
// O foco pode substituir campos da classe (ex.: o bruxo caçador de monstros troca as magias de pacto pelos Sinais).
const arquetipoPj = () => ({ ...arquetipoBase(), ...(focoPj().substitui || {}) });

function linhaDeComplicacao(nome = "", detalhe = "") {
  const sugeridas = new Set(arquetipoPj().sugestoes.complicacoes.map((c) => c.nome));
  const opcoesHtml = pj().complicacoes.map((c) =>
    `<option value="${escapar(c.nome)}" ${c.nome === nome ? "selected" : ""}>` +
    `${escapar(c.nome)}${sugeridas.has(c.nome) ? " (sugerida)" : ""}</option>`).join("");
  const linha = document.createElement("div");
  linha.className = "linha-complicacao";
  linha.innerHTML = `
    <select class="pj-complicacao" aria-label="Complicação">${opcoesHtml}</select>
    <input class="pj-complicacao-detalhe" type="text" placeholder="Detalhe (opcional)" value="${escapar(detalhe)}">
    <button type="button" class="botao pequeno" data-remover>Remover</button>`;
  linha.querySelector(".pj-complicacao").addEventListener("change", (ev) => {
    const exemplo = pj().complicacoes.find((c) => c.nome === ev.target.value);
    const campo = linha.querySelector(".pj-complicacao-detalhe");
    if (!campo.value) campo.placeholder = exemplo ? exemplo.exemplo : "Detalhe (opcional)";
  });
  linha.querySelector("[data-remover]").addEventListener("click", () => linha.remove());
  return linha;
}

function preencherComplicacoes(lista) {
  const motivacao = lista.find((c) => c.categoria === "motivacao");
  if (motivacao) {
    el("pj-motivacao").value = motivacao.nome;
    el("pj-motivacao-detalhe").value = motivacao.detalhe || "";
  }
  const caixa = el("pj-complicacoes");
  caixa.innerHTML = "";
  lista.filter((c) => c.categoria !== "motivacao")
    .forEach((c) => caixa.appendChild(linhaDeComplicacao(c.nome, c.detalhe)));
}

function sugestoesDoArquetipo() {
  const s = arquetipoPj().sugestoes;
  preencherComplicacoes([
    { categoria: "motivacao", nome: s.motivacoes[0], detalhe: "" },
    ...s.complicacoes.slice(0, 2).map((c) => ({ categoria: "complicacao", ...c })),
  ]);
}

// --- escolha de vantagens e de armas/itens (modo "Escolher")

const focoPj = () => arquetipoBase().focos.find((f) => f.id === el("pj-foco").value) || arquetipoBase().focos[0];
const riquezaPj = () => pj().riqueza.find((r) => r.id === el("pj-riqueza").value) || pj().riqueza[0];
// Gêneros como o cyberpunk pagam o equipamento com a vantagem Equipamento (5 pontos por graduação).
const emPontos = () => pj().equipamento_modo === "pontos";
const temImplantes = () => pj().implantes.length > 0;
const temRacas = () => pj().racas.length > 0;
const racaPj = () => pj().racas.find((r) => r.id === el("pj-raca").value) || pj().racas[0];
const npPj = () => Number(el("pj-np").value);
const custoDaRaca = () => (temRacas() ? racaPj().custo_por_np[npPj()] || 0 : 0);
// Magias que acompanham o NP mudam de graduação e de custo com ele.
const implanteNoNp = (i) => i.por_np[npPj()] || { custo: i.custo, estatistica: i.estatistica };
const graduacoesDeEquipamento = (pontos) => Math.ceil(pontos / 5);
const modo = (nome) => document.querySelector(`input[name="${nome}"]:checked`).value;
const baseDaVantagem = (nome) => nome.split(" (")[0];
const dolares = (v) => {
  const numero = v.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).replace(",00", "");
  // $1.234,50 (faroeste), 2.550eb (cyberpunk), 15 po (fantasia): moeda com letras vai depois.
  if (pj().moeda === "eb") return `${numero}eb`;
  return /^[a-z]/i.test(pj().moeda) ? `${numero} ${pj().moeda}` : `${pj().moeda}${numero}`;
};
const precoDoImplante = (i) => (pj().implantes_em_dinheiro ? i.preco || 0 : 0);

function caixa(nome, valor, marcado, rotulo, detalhe = "", dica = "") {
  return `<label class="opcao" title="${escapar(dica)}">
    <input type="checkbox" name="${nome}" value="${escapar(valor)}" ${marcado ? "checked" : ""}>
    <span>${escapar(rotulo)}</span>${detalhe ? `<small>${escapar(detalhe)}</small>` : ""}</label>`;
}

function grupo(titulo, conteudo, aberto = true) {
  return conteudo ? `<details class="grupo-escolha" ${aberto ? "open" : ""}><summary>${escapar(titulo)}</summary>
    <div class="opcoes">${conteudo}</div></details>` : "";
}

function desenharVantagens() {
  const a = arquetipoPj();
  const f = focoPj();
  const efeito = Object.fromEntries(pj().vantagens.map((v) => [v.nome, v.efeito]));
  const doArquetipo = [...a.vantagens_essenciais, ...f.vantagens];
  const usadas = new Set([...doArquetipo, ...a.vantagens_opcionais].map(baseDaVantagem));
  const item = (nome, marcado) => caixa("pj-vantagem", nome, marcado, nome, "", efeito[baseDaVantagem(nome)] || "");
  const porTipo = {};
  pj().vantagens.filter((v) => !usadas.has(v.nome))
    .forEach((v) => (porTipo[v.tipo] ||= []).push(item(v.nome, false)));
  el("pj-vantagens-grupos").innerHTML =
    grupo(`Essenciais: ${a.nome} · ${f.nome}`, doArquetipo.map((n) => item(n, true)).join("")) +
    grupo(`Opcionais: ${a.nome}`, a.vantagens_opcionais.filter((n) => !doArquetipo.includes(n))
      .map((n) => item(n, false)).join("")) +
    Object.entries(porTipo).map(([tipo, itens]) => grupo(`Outras de ${tipo.toLowerCase()}`, itens.join(""), false)).join("");
  atualizarContadorDeVantagens();
}

function atualizarContadorDeVantagens() {
  const marcadas = document.querySelectorAll('input[name="pj-vantagem"]:checked').length;
  const r = riquezaPj();
  const extra = pontosExtrasDaCompra();
  const orcamento = Number(el("pj-np").value) * 15 + r.ajuste_de_pontos;
  const pontosDeRiqueza = r.beneficio + extra;
  const riqueza = pontosDeRiqueza ? ` + ${pontosDeRiqueza} PP de Benefício (Riqueza)` +
    (extra ? ` (${extra} para pagar os itens)` : "") : "";
  const partes = [`${marcadas} PP em vantagens${riqueza}`];
  let gasto = marcadas + pontosDeRiqueza;
  if (custoDaRaca()) {
    partes.push(`${custoDaRaca()} PP em traços de ${racaPj().nome.toLowerCase()}`);
    gasto += custoDaRaca();
  }
  if (emPontos() && modo("pj-equipamento-modo") === "manual") {
    const equipamento = graduacoesDeEquipamento(totalDosItens());
    partes.push(`${equipamento} PP em Equipamento`);
    gasto += equipamento;
  }
  if (temImplantes() && modo("pj-implantes-modo") === "manual") {
    const implantes = totalDosImplantes();
    partes.push(`${implantes} PP em ${pj().rotulo_poderes.toLowerCase()}`);
    gasto += implantes;
  }
  const contador = el("pj-vantagens-contador");
  contador.textContent = `${partes.join(" + ")}, de um orçamento de ${orcamento} PP` +
    (gasto > orcamento ? ` — passa ${gasto - orcamento} PP do orçamento!` : ` (sobram ${orcamento - gasto} PP para habilidades, defesas e perícias)`) +
    ". O gerador pode subir as graduações das vantagens marcadas (como Ataque à Distância), mas não acrescenta outras.";
  contador.classList.toggle("aviso", gasto > orcamento);
  if (temImplantes()) atualizarContadorDeImplantes(orcamento, gasto);
}

// --- implantes / poderes do gênero

// Mesma regra do servidor: num arranjo, a magia mais cara paga o custo cheio e cada outra custa 1 PP.
function totalDosImplantes() {
  const porId = Object.fromEntries(pj().implantes.map((i) => [i.id, i]));
  const arranjos = {};
  let total = 0;
  document.querySelectorAll('input[name="pj-implante"]:checked').forEach((c) => {
    const i = porId[c.value];
    const custo = implanteNoNp(i).custo;
    if (!i.arranjo) total += custo;
    else (arranjos[i.arranjo] ||= []).push(custo);
  });
  Object.values(arranjos).forEach((custos) => { total += Math.max(...custos) + custos.length - 1; });
  // Falhas do foco (ex.: magias rúnicas) barateiam o arranjo inteiro.
  (focoPj().falhas || []).forEach((falha) => { if (arranjos[falha.arranjo]) total += falha.custo; });
  return total;
}

function atualizarContadorDeImplantes(orcamento, gasto) {
  const contador = el("pj-implantes-contador");
  contador.textContent = `Total: ${totalDosImplantes()} PP em ${pj().rotulo_poderes.toLowerCase()}. ` +
    `Somando tudo que foi escolhido: ${gasto} de ${orcamento} PP. ` +
    "O que passar dos limites do NP fica de fora e aparece anotado na ficha.";
  contador.classList.toggle("aviso", gasto > orcamento);
}

// manterMarcados: redesenha (ex.: ao trocar o NP, que muda custos e graduações) sem perder a escolha.
function desenharImplantes(manterMarcados = false) {
  if (!temImplantes()) return;
  const a = arquetipoPj();
  const f = focoPj();
  const porId = Object.fromEntries(pj().implantes.map((i) => [i.id, i]));
  // Mesma regra do servidor (o foco pode trocar as magias da classe pelas dele).
  const [essenciais, opcionais] = f.implantes_da_escolha;
  const marcadosAntes = new Set([...document.querySelectorAll('input[name="pj-implante"]:checked')].map((c) => c.value));
  const linha = (id, marcado) => {
    const i = porId[id];
    const noNp = implanteNoNp(i);
    const preco = precoDoImplante(i) ? ` · ${dolares(i.preco)}${i.preco_estimado ? " (estimado)" : ""}` : "";
    const arranjo = i.arranjo ? ` · ${i.arranjo}: 1 PP se não for a mais cara` : "";
    return caixa("pj-implante", id, manterMarcados ? marcadosAntes.has(id) : marcado,
      `${i.nome} (${noNp.custo} PP${preco})`, [i.descricao, noNp.estatistica + arranjo].join(" "), noNp.estatistica);
  };
  const porCategoria = {};
  pj().implantes.filter((i) => !essenciais.includes(i.id) && !opcionais.includes(i.id))
    .forEach((i) => (porCategoria[i.categoria || "outros"] ||= []).push(linha(i.id, false)));
  el("pj-implantes-grupos").innerHTML =
    grupo(`Essenciais: ${a.nome} · ${f.nome}`, essenciais.map((id) => linha(id, true)).join("")) +
    grupo(`Opcionais: ${a.nome}`, opcionais.map((id) => linha(id, false)).join("")) +
    Object.entries(porCategoria).map(([cat, itens]) => grupo(`Outros: ${cat}`, itens.join(""), false)).join("");
  atualizarContadorDeVantagens();
}

function desenharEquipamento() {
  const a = arquetipoPj();
  const f = focoPj();
  const porId = Object.fromEntries(pj().catalogo.map((i) => [i.id, i]));
  const principal = f.armas[0] || a.armas.principais[0];
  const sugeridos = [...new Set([...f.armas, ...a.armas.principais, ...a.armas.secundarias, ...pj().itens_basicos,
                                 ...a.itens.essenciais, ...f.itens, ...a.itens.opcionais])];
  const marcar = new Set([principal, porId[principal]?.municao, ...pj().itens_basicos,
                          ...a.itens.essenciais, ...f.itens].filter(Boolean));
  const linha = (id) => {
    const i = porId[id];
    const cada = i.quantidade ? " cada" : "";
    const preco = emPontos() ? `${i.custo} ponto${i.custo === 1 ? "" : "s"}${cada}`
      : i.preco == null ? "a combinar" : dolares(i.preco) + cada + (i.preco_estimado ? " (estimado)" : "");
    const detalhe = [i.resumo, i.notas, preco].filter(Boolean).join(" · ");
    const opcao = caixa("pj-item", id, marcar.has(id), i.nome, detalhe, i.descricao || "");
    if (!i.quantidade) return opcao;
    return `<div class="opcao-com-quantidade">${opcao}
      <label class="quantidade"><span>Qtd.</span><input type="number" data-quantidade="${escapar(id)}"
        min="1" max="${pj().quantidade_maxima}" value="1" aria-label="Quantidade de ${escapar(i.nome)}"></label></div>`;
  };
  const porCategoria = {};
  pj().catalogo.filter((i) => !sugeridos.includes(i.id))
    .forEach((i) => (porCategoria[i.categoria] ||= []).push(linha(i.id)));
  el("pj-equipamento-grupos").innerHTML =
    grupo(`Sugeridos para ${a.nome} (${f.nome})`, sugeridos.filter((id) => porId[id]).map(linha).join("")) +
    Object.entries(porCategoria).map(([cat, itens]) => grupo(cat, itens.join(""), false)).join("");
  atualizarContadorDeEquipamento();
}

const custoEmPontos = (r) => r.beneficio - r.ajuste_de_pontos;

// Quantidade escolhida de um item (comida, munição, bebida); os outros itens valem sempre 1.
function quantidadeDe(id) {
  const campo = document.querySelector(`input[data-quantidade="${CSS.escape(id)}"]`);
  const valor = Math.floor(Number(campo?.value));
  return valor >= 1 ? Math.min(valor, pj().quantidade_maxima) : 1;
}

function totalDosItens() {
  const porId = Object.fromEntries(pj().catalogo.map((i) => [i.id, i]));
  return [...document.querySelectorAll('input[name="pj-item"]:checked')]
    .reduce((soma, c) => soma + ((emPontos() ? porId[c.value].custo : porId[c.value].preco) || 0) * quantidadeDe(c.value), 0)
    + (emPontos() ? 0 : dinheiroDosImplantes());
}

// Cyberware escolhido também sai do dinheiro (cyberpunk), quando o modo de implantes é "Escolher".
function dinheiroDosImplantes() {
  if (!temImplantes() || !pj().implantes_em_dinheiro || modo("pj-implantes-modo") !== "manual") return 0;
  const porId = Object.fromEntries(pj().implantes.map((i) => [i.id, i]));
  return [...document.querySelectorAll('input[name="pj-implante"]:checked')]
    .reduce((soma, c) => soma + precoDoImplante(porId[c.value]), 0);
}

// Mesma regra do servidor: a condição mais barata, sem descer da atual, cujo dinheiro cobre o total.
function riquezaQuePaga(total) {
  const atual = riquezaPj();
  const opcoesQueCobrem = pj().riqueza.filter((r) => r.dinheiro >= total && custoEmPontos(r) >= custoEmPontos(atual));
  opcoesQueCobrem.sort((a, b) => custoEmPontos(a) - custoEmPontos(b) || a.dinheiro - b.dinheiro);
  return opcoesQueCobrem[0] || null;
}

// PP extras que a compra vai consumir (só quando passou do dinheiro e o jogador escolheu pagar com pontos).
function pontosExtrasDaCompra() {
  if (modo("pj-equipamento-modo") !== "manual" || modo("pj-excesso") !== "pontos") return 0;
  const total = totalDosItens();
  if (total <= riquezaPj().dinheiro) return 0;
  const nova = riquezaQuePaga(total);
  return nova ? custoEmPontos(nova) - custoEmPontos(riquezaPj()) : 0;
}

function atualizarContadorDeEquipamento() {
  if (emPontos()) {
    const pontos = totalDosItens();
    const graduacoes = graduacoesDeEquipamento(pontos);
    el("pj-equipamento-contador").textContent =
      `Total: ${pontos} pontos de equipamento = Equipamento ${graduacoes} (${graduacoes} PP, ` +
      `${graduacoes * 5} pontos; sobram ${graduacoes * 5 - pontos}). Armas que não couberem no NP ficam de fora.`;
    el("pj-excesso").hidden = true;
    atualizarContadorDeVantagens();
    return;
  }
  const total = totalDosItens();
  const dinheiro = riquezaPj().dinheiro;
  const passou = total > dinheiro;
  const contador = el("pj-equipamento-contador");
  contador.textContent = `Total: ${dolares(total)} de ${dolares(dinheiro)}` +
    (passou ? ` — passa ${dolares(total - dinheiro)} do dinheiro.` : ` · faltam gastar ${dolares(dinheiro - total)}.`) +
    (dinheiroDosImplantes() ? ` (inclui ${dolares(dinheiroDosImplantes())} de cyberware)` : "") +
    " Armas que não couberem no NP ficam de fora e o dinheiro volta.";
  contador.classList.toggle("aviso", passou);

  el("pj-excesso").hidden = !passou;
  if (passou) {
    const nova = riquezaQuePaga(total);
    const opcaoPontos = document.querySelector('input[name="pj-excesso"][value="pontos"]');
    opcaoPontos.disabled = !nova;
    if (!nova) document.querySelector('input[name="pj-excesso"][value="divida"]').checked = true;
    el("pj-excesso-pontos").textContent = nova
      ? `Pagar com pontos: subir para ${nova.nome} (${dolares(nova.dinheiro)}), ` +
        `custa ${custoEmPontos(nova) - custoEmPontos(riquezaPj())} PP a mais`
      : "Pagar com pontos: nenhuma condição financeira cobre esse valor";
    el("pj-excesso-divida").textContent =
      `Ficar devendo ${dolares(total - dinheiro)} (a ficha sai com a dívida anotada; combine com o mestre)`;
  }
  atualizarContadorDeVantagens();
}

function atualizarListasDeEscolha() {
  el("pj-vantagens-lista").hidden = modo("pj-vantagens-modo") !== "manual";
  el("pj-equipamento-lista").hidden = modo("pj-equipamento-modo") !== "manual";
  if (temImplantes()) el("pj-implantes-lista").hidden = modo("pj-implantes-modo") !== "manual";
  desenharVantagens();
  desenharEquipamento();
  desenharImplantes();
}

function prepararAbaJogador() {
  el("pj-arquetipo").innerHTML = opcoesDeSelect(pj().arquetipos);
  el("pj-np").innerHTML = pj().nps.map((np) => `<option value="${np}">NP ${np} (${np * 15} PP)</option>`).join("");
  el("pj-np").value = pj().np_padrao;
  el("pj-riqueza").innerHTML = opcoesDeSelect(pj().riqueza);
  el("pj-riqueza").value = pj().riqueza.some((r) => r.id === "classe_media") ? "classe_media" : pj().riqueza[0].id;
  el("pj-riqueza-campo").hidden = emPontos();
  el("pj-bloco-implantes").hidden = !temImplantes();
  el("pj-passo-implantes-aba").hidden = !temImplantes();
  el("pj-implantes-titulo").textContent = pj().rotulo_poderes;
  el("pj-implantes-aba").textContent = pj().rotulo_poderes;
  el("pj-bloco-equipamento").querySelector("legend").textContent =
    emPontos() ? "Armas e itens (pagos com a vantagem Equipamento)" : "Armas e itens";
  el("pj-motivacao").innerHTML = pj().motivacoes
    .map((m) => `<option value="${escapar(m.nome)}" title="${escapar(m.exemplo)}">${escapar(m.nome)}</option>`).join("");
  // Na fantasia, arquétipo e foco viram classe e subclasse.
  document.querySelectorAll("[data-rotulo-arquetipo]").forEach((e) => { e.textContent = pj().rotulo_arquetipo; });
  document.querySelectorAll("[data-rotulo-foco]").forEach((e) => { e.textContent = pj().rotulo_foco; });
  el("pj-passo-raca-aba").hidden = !temRacas();
  if (temRacas()) el("pj-raca").innerHTML = opcoesDeSelect(pj().racas);

  const atualizarRaca = () => {
    if (!temRacas()) return;
    const r = racaPj();
    el("pj-raca-descricao").textContent = r.descricao;
    el("pj-raca-tracos").innerHTML = r.tracos.map((t) => `<li>${escapar(t)}</li>`).join("");
    el("pj-raca-custo").textContent = `Custo no NP ${npPj()}: ${custoDaRaca()} PP.`;
    atualizarContadorDeVantagens();
  };
  el("pj-raca").addEventListener("change", atualizarRaca);

  const atualizarFoco = () => {
    el("pj-foco-descricao").textContent = focoPj().descricao;
    desenharVantagens();
    desenharEquipamento();
    desenharImplantes();
  };
  const atualizarArquetipo = () => {
    const a = arquetipoPj();
    el("pj-conceito").textContent = a.conceito;
    el("pj-foco").innerHTML = opcoesDeSelect(a.focos);
    atualizarFoco();
    sugestoesDoArquetipo();
  };
  const atualizarRiqueza = () => {
    el("pj-riqueza-descricao").textContent = riquezaPj().descricao;
    atualizarContadorDeEquipamento();
    atualizarContadorDeVantagens();
  };
  el("pj-arquetipo").addEventListener("change", atualizarArquetipo);
  el("pj-foco").addEventListener("change", atualizarFoco);
  el("pj-riqueza").addEventListener("change", atualizarRiqueza);
  // O NP muda o custo da raça e a graduação das magias que o acompanham.
  el("pj-np").addEventListener("change", () => {
    atualizarRaca();
    desenharImplantes(true);
    atualizarContadorDeEquipamento();
  });
  document.querySelectorAll('input[name="pj-vantagens-modo"], input[name="pj-equipamento-modo"], input[name="pj-implantes-modo"]')
    .forEach((r) => r.addEventListener("change", () => {
      el("pj-vantagens-lista").hidden = modo("pj-vantagens-modo") !== "manual";
      el("pj-equipamento-lista").hidden = modo("pj-equipamento-modo") !== "manual";
      el("pj-implantes-lista").hidden = modo("pj-implantes-modo") !== "manual";
      atualizarContadorDeEquipamento();
    }));
  el("pj-implantes-grupos").addEventListener("change", atualizarContadorDeEquipamento);
  el("pj-vantagens-grupos").addEventListener("change", atualizarContadorDeVantagens);
  el("pj-equipamento-grupos").addEventListener("change", atualizarContadorDeEquipamento);
  // Mexer na quantidade já marca o item.
  el("pj-equipamento-grupos").addEventListener("input", (evento) => {
    const id = evento.target.dataset.quantidade;
    if (id === undefined) return;
    const item = document.querySelector(`input[name="pj-item"][value="${CSS.escape(id)}"]`);
    if (item) item.checked = true;
    atualizarContadorDeEquipamento();
  });
  document.querySelectorAll('input[name="pj-excesso"]').forEach((r) => r.addEventListener("change", atualizarContadorDeVantagens));
  atualizarArquetipo();
  atualizarRiqueza();
  atualizarRaca();
  atualizarListasDeEscolha();

  el("pj-adicionar-complicacao").addEventListener("click", () =>
    el("pj-complicacoes").appendChild(linhaDeComplicacao(pj().complicacoes[0].nome)));
  el("pj-sortear").addEventListener("click", async () => {
    try {
      const dados = await chamar("/api/jogador/complicacoes", { arquetipo: el("pj-arquetipo").value });
      preencherComplicacoes(dados.complicacoes);
    } catch (erro) {
      mostrarMensagem(erro.message, true);
    }
  });

  el("formulario-pj").addEventListener("submit", (evento) => {
    evento.preventDefault();
    // Enter num campo antes do último passo só avança; a ficha sai no passo "Ficha".
    if (passoAtual !== "ficha") {
      avancarPasso(1);
      return;
    }
    const complicacoes = [{ categoria: "motivacao", nome: el("pj-motivacao").value,
                            detalhe: el("pj-motivacao-detalhe").value }];
    document.querySelectorAll("#pj-complicacoes .linha-complicacao").forEach((linha) => complicacoes.push({
      categoria: "complicacao",
      nome: linha.querySelector(".pj-complicacao").value,
      detalhe: linha.querySelector(".pj-complicacao-detalhe").value,
    }));
    const marcados = (nome) => [...document.querySelectorAll(`input[name="${nome}"]:checked`)].map((c) => c.value);
    gerarPersonagem({
      nome: el("pj-nome").value,
      jogador: el("pj-jogador").value,
      arquetipo: el("pj-arquetipo").value,
      raca: temRacas() ? el("pj-raca").value : "",
      np: Number(el("pj-np").value),
      foco: el("pj-foco").value,
      riqueza: el("pj-riqueza").value,
      complicacoes,
      vantagens: modo("pj-vantagens-modo") === "manual"
        ? { modo: "manual", nomes: marcados("pj-vantagem") } : { modo: "auto" },
      equipamento: modo("pj-equipamento-modo") === "manual"
        ? { modo: "manual", ids: marcados("pj-item"), excesso: modo("pj-excesso"),
            quantidades: Object.fromEntries(marcados("pj-item").filter((id) => quantidadeDe(id) > 1)
              .map((id) => [id, quantidadeDe(id)])) }
        : { modo: "auto" },
      implantes: modo("pj-implantes-modo") === "manual"
        ? { modo: "manual", ids: marcados("pj-implante") } : { modo: "auto" },
    });
  });
  el("pj-outra-versao").addEventListener("click", () => gerarPersonagem(estado.pj.parametros));

  el("cartao-pj").addEventListener("click", (evento) => {
    const botao = evento.target.closest("button[data-acao]");
    if (botao) acaoDeArquivo(botao.dataset.acao, estado.pj.personagem);
  });
}

async function gerarPersonagem(parametros) {
  try {
    const dados = await chamar("/api/jogador/gerar", parametros);
    estado.pj = { parametros, personagem: dados.personagem };
    el("resultado-pj").hidden = false;
    el("cartao-pj").innerHTML = cartao(dados.personagem, { aberto: true });
    el("resultado-pj").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (erro) {
    mostrarMensagem(erro.message, true);
  }
}

// ---------------------------------------------------------------- passo a passo da ficha de jogador

const PASSOS = ["genero", "identidade", "raca", "arquetipo", "vantagens", "implantes", "equipamento", "complicacoes", "ficha"];
const passosAtivos = () => PASSOS.filter((p) => (p !== "implantes" || temImplantes()) && (p !== "raca" || temRacas()));
let passoAtual = "genero";

function irParaPasso(nome) {
  const ativos = passosAtivos();
  if (!ativos.includes(nome)) nome = ativos[0];
  const indice = ativos.indexOf(nome);
  passoAtual = nome;
  document.querySelectorAll("#formulario-pj .passo").forEach((s) => { s.hidden = s.dataset.passo !== nome; });
  document.querySelectorAll(".passo-aba").forEach((b) => {
    b.setAttribute("aria-selected", b.dataset.passo === nome);
    b.classList.toggle("feito", ativos.indexOf(b.dataset.passo) > -1 && ativos.indexOf(b.dataset.passo) < indice);
  });
  el("pj-voltar").disabled = indice === 0;
  el("pj-proximo").hidden = indice === ativos.length - 1;
  if (nome === "ficha") desenharResumo();
  const topo = el("formulario-pj").getBoundingClientRect().top;
  if (topo < 0) el("formulario-pj").scrollIntoView({ behavior: "smooth", block: "start" });
}

function avancarPasso(direcao) {
  const ativos = passosAtivos();
  const destino = ativos[ativos.indexOf(passoAtual) + direcao];
  if (destino) irParaPasso(destino);
}

function desenharResumo() {
  const np = Number(el("pj-np").value);
  const marcados = (nome) => document.querySelectorAll(`input[name="${nome}"]:checked`).length;
  const escolha = (modoNome, nome, plural) => (modo(modoNome) === "manual"
    ? `${marcados(nome)} ${plural} à mão`
    : `${plural.endsWith("as") ? "sorteadas" : "sorteados"} de acordo com: ${arquetipoPj().nome}`);
  let equipamento = escolha("pj-equipamento-modo", "pj-item", "escolhidos");
  if (modo("pj-equipamento-modo") === "manual" && !el("pj-excesso").hidden) {
    equipamento += modo("pj-excesso") === "pontos" ? "; a diferença é paga com pontos" : "; a diferença fica como dívida";
  }
  const complicacoes = [el("pj-motivacao").value,
    ...[...document.querySelectorAll("#pj-complicacoes .pj-complicacao")].map((s) => s.value)];
  const linhas = [
    ["genero", "Gênero", opcoes.genero.nome],
    ["identidade", "Nome", el("pj-nome").value.trim() || "sorteado pelo gerador"],
    ["identidade", "Jogador", el("pj-jogador").value.trim() || "—"],
    temRacas() && ["raca", "Raça", `${racaPj().nome} (${custoDaRaca()} PP)`],
    ["arquetipo", pj().rotulo_arquetipo, `${arquetipoPj().nome} · ${pj().rotulo_foco.toLowerCase()} ${focoPj().nome}`],
    ["arquetipo", "Nível de poder", `NP ${np} (${np * 15} PP)`],
    !emPontos() && ["arquetipo", "Condição financeira", riquezaPj().nome],
    ["vantagens", "Vantagens", escolha("pj-vantagens-modo", "pj-vantagem", "escolhidas")],
    temImplantes() && ["implantes", pj().rotulo_poderes, escolha("pj-implantes-modo", "pj-implante", "escolhidos")],
    ["equipamento", "Armas e itens", equipamento],
    ["complicacoes", "Complicações", complicacoes.join(", ")],
  ].filter(Boolean);
  const passouDoOrcamento = el("pj-vantagens-contador").classList.contains("aviso") &&
    (modo("pj-vantagens-modo") === "manual" || modo("pj-equipamento-modo") === "manual" ||
     (temImplantes() && modo("pj-implantes-modo") === "manual"));
  el("pj-resumo").innerHTML = linhas.map(([passo, rotulo, valor]) =>
    `<div><dt>${escapar(rotulo)}</dt><dd>${escapar(valor)}` +
    ` <button type="button" class="link" data-ir="${passo}">alterar</button></dd></div>`).join("") +
    (passouDoOrcamento ? `<p class="aviso-texto">${escapar(el("pj-vantagens-contador").textContent)}</p>` : "");
}

function prepararPassos() {
  document.querySelectorAll(".passo-aba").forEach((b) => b.addEventListener("click", () => irParaPasso(b.dataset.passo)));
  el("pj-voltar").addEventListener("click", () => avancarPasso(-1));
  el("pj-proximo").addEventListener("click", () => avancarPasso(1));
  el("pj-resumo").addEventListener("click", (evento) => {
    const botao = evento.target.closest("button[data-ir]");
    if (botao) irParaPasso(botao.dataset.ir);
  });
  // Depois de trocar o gênero (a página recarrega), continua no passo seguinte.
  let inicial = "genero";
  try {
    inicial = sessionStorage.getItem("passo") || inicial;
    sessionStorage.removeItem("passo");
  } catch { /* armazenamento indisponível */ }
  irParaPasso(inicial);
}

// ---------------------------------------------------------------- início

// O gênero aparece no primeiro passo da ficha de jogador e no formulário de NPC.
function prepararGenero() {
  el("genero-descricao").textContent = opcoes.genero.descricao;
  ["genero", "npc-genero"].forEach((id) => {
    el(id).innerHTML = opcoesDeSelect(opcoes.generos);
    el(id).value = opcoes.genero.id;
    el(id).addEventListener("change", () => {
      if (id === "genero") {
        try { sessionStorage.setItem("passo", "identidade"); } catch { /* armazenamento indisponível */ }
      }
      window.location.search = `?genero=${encodeURIComponent(el(id).value)}`;
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  prepararGenero();
  prepararAbaJogador();
  prepararPassos();
  prepararAbaNpc();
  document.querySelectorAll(".aba").forEach((b) => b.addEventListener("click", () => trocarAba(b.dataset.aba)));
  let inicial = "jogador";
  try { inicial = localStorage.getItem("aba") || inicial; } catch { /* armazenamento indisponível */ }
  trocarAba(inicial);
});
