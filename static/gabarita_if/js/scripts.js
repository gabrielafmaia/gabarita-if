const crudModalElement = document.getElementById("crud-modal");
const crudModal = crudModalElement ? bootstrap.Modal.getOrCreateInstance(crudModalElement) : null;

document.body.addEventListener("htmx:afterSwap", function (event) {
  const targetId = event.detail.target?.id;

  if (targetId === "modal-body") {
    const saveButton = document.getElementById("crud-save");
    const form = event.detail.target.querySelector("form#crud-form");
    saveButton?.classList.toggle("d-none", !form);

    if (event.detail.elt?.matches("[hx-get]") && crudModal) {
      const title = event.detail.elt.dataset?.modalTitle;
      if (title) {
        document.querySelector("#crud-modal .modal-title").textContent = title;
      }

      crudModal.show();
    }

    inicializarAssuntosDosBlocos(event.detail.target);
    atualizarResumoCaderno();
  }

  if (targetId === "containerBlocos" || targetId === "blocosQuestoes") {
    inicializarAssuntosDosBlocos(event.detail.target);
    atualizarResumoCaderno();
  }
});

document.body.addEventListener("crudSaved", function () {
  document.querySelectorAll(".modal.show").forEach((element) => {
    bootstrap.Modal.getOrCreateInstance(element).hide();
  });
});

crudModalElement?.addEventListener("hidden.bs.modal", function () {
  document.body.classList.remove("modal-open");
  document.body.style.removeProperty("padding-right");
  document.querySelectorAll(".modal-backdrop").forEach((backdrop) => backdrop.remove());
});

window.addEventListener("DOMContentLoaded", () => {
  const sidebarToggle = document.body.querySelector("#sidebarToggle");
  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", (event) => {
      event.preventDefault();
      document.body.classList.toggle("sb-sidenav-toggled");
      localStorage.setItem("sb|sidebar-toggle", document.body.classList.contains("sb-sidenav-toggled"));
    });
  }

  inicializarAssuntosDosBlocos(document);
});

function obterContainerBlocos() {
  return document.getElementById("containerBlocos") || document.getElementById("blocosQuestoes");
}

function atualizarAssuntosDoBloco(bloco) {
  const disciplina = bloco?.querySelector(".disciplina-select");
  const assunto = bloco?.querySelector(".assunto-select");
  if (!disciplina || !assunto) return;

  const disciplinaId = disciplina.value;
  const assuntoSelecionado = assunto.value;
  if (!assunto._opcoesAssunto) {
    assunto._opcoesAssunto = Array.from(assunto.options).map((opcao) => ({
      value: opcao.value,
      text: opcao.text,
      disciplinaId: opcao.dataset.disciplinaId,
    }));
  }
  const opcoesAssunto = assunto._opcoesAssunto;

  assunto.replaceChildren();

  const opcaoVazia = document.createElement("option");
  opcaoVazia.value = "";
  opcaoVazia.textContent = disciplinaId ? "Todos" : "Selecione uma disciplina primeiro";
  assunto.append(opcaoVazia);

  opcoesAssunto
    .filter((opcao) => opcao.value && opcao.disciplinaId === disciplinaId)
    .forEach((opcao) => {
      const elemento = document.createElement("option");
      elemento.value = opcao.value;
      elemento.textContent = opcao.text;
      elemento.dataset.disciplinaId = opcao.disciplinaId;
      assunto.append(elemento);
    });

  assunto.disabled = !disciplinaId;
  assunto.value =
    disciplinaId &&
    opcoesAssunto.some((opcao) => opcao.value === assuntoSelecionado && opcao.disciplinaId === disciplinaId)
      ? assuntoSelecionado
      : "";
}

function inicializarAssuntosDosBlocos(container) {
  container?.querySelectorAll(".bloco-item").forEach(atualizarAssuntosDoBloco);
}

document.addEventListener("change", function (event) {
  if (!event.target.matches(".disciplina-select")) return;
  atualizarAssuntosDoBloco(event.target.closest(".bloco-item"));
});

document.addEventListener("submit", function (event) {
  if (!event.target.matches("#crud-form")) return;
  inicializarAssuntosDosBlocos(event.target);
  event.target.querySelectorAll(".assunto-select").forEach((assunto) => {
    assunto.disabled = false;
  });
});

document.body.addEventListener("htmx:configRequest", function (event) {
  const botao = event.detail.elt;
  if (!botao?.matches("#btnAdicionarBloco, #adicionarBloco")) return;

  const container = obterContainerBlocos();
  if (!container) return;

  event.detail.parameters.index = container.querySelectorAll(".bloco-item").length;
});

document.addEventListener("click", function (event) {
  const botao = event.target.closest("[data-acao='remover-bloco']");
  if (!botao) return;

  const bloco = botao.closest(".bloco-item");
  if (!bloco) return;

  const container = document.getElementById("containerBlocos");
  if (!container) return;

  const blocos = container.querySelectorAll(".bloco-item");
  if (blocos.length <= 1) return;

  bloco.remove();

  container.querySelectorAll(".bloco-item").forEach(function (b, i) {
    b.dataset.index = i;

    const titulo = b.querySelector(".titulo-bloco");
    if (titulo) titulo.textContent = "BLOCO " + (i + 1);

    const disciplinaSelect = b.querySelector(".disciplina-select");
    if (disciplinaSelect) {
      disciplinaSelect.name = `blocos[${i}][disciplina]`;
      disciplinaSelect.id = `disciplina_${i}`;
      const lbl = b.querySelector(`label[for]`);
      if (lbl && lbl.getAttribute("for") && lbl.getAttribute("for").toLowerCase().includes("disciplina")) {
        lbl.setAttribute("for", `disciplina_${i}`);
      }
    }

    const assuntoSelect = b.querySelector(".assunto-select");
    if (assuntoSelect) {
      assuntoSelect.name = `blocos[${i}][assunto]`;
      assuntoSelect.id = `assunto_${i}`;
      const lblA = b.querySelectorAll(`label[for]`);
      lblA.forEach(function (l) {
        if (l.getAttribute("for") && l.getAttribute("for").toLowerCase().includes("assunto")) {
          l.setAttribute("for", `assunto_${i}`);
        }
      });
    }

    // Quantidade
    const inputQtd = b.querySelector(".input-qtd");
    if (inputQtd) {
      inputQtd.name = `blocos[${i}][quantidade]`;
    }
  });

  atualizarResumoCaderno();
});

document.addEventListener("click", function (event) {
  const mais = event.target.closest(".btn-qtd-plus");
  const menos = event.target.closest(".btn-qtd-minus");
  if (!mais && !menos) return;

  const input = event.target.closest(".input-group")?.querySelector(".input-qtd");
  if (!input) return;

  let valor = Number(input.value) || 1;
  if (mais) valor++;
  if (menos) valor--;
  if (valor < 1) valor = 1;
  if (valor > 100) valor = 100;

  input.value = valor;
  atualizarResumoCaderno();
});

function atualizarResumoCaderno() {
  const container = document.getElementById("containerBlocos");
  if (!container) return;

  const blocos = container.querySelectorAll(".bloco-item");
  const total = Array.from(blocos).reduce(function (soma, bloco) {
    const input = bloco.querySelector(".input-qtd");
    return soma + (Number(input?.value) || 0);
  }, 0);

  const totalEl = document.getElementById("resumoTotal");
  const blocosEl = document.getElementById("resumoBlocos");

  if (totalEl) totalEl.textContent = total;
  if (blocosEl) blocosEl.textContent = blocos.length + " Bloco(s)";
}
