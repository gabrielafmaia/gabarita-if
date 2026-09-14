const crudModalElement = document.getElementById("crud-modal");
const crudModal = crudModalElement ? bootstrap.Modal.getOrCreateInstance(crudModalElement) : null;

document.body.addEventListener("htmx:afterSwap", function (event) {
  if (event.detail.target?.id !== "modal-body") {
    return;
  }

  const saveButton = document.getElementById("crud-save");
  const form = event.detail.target.querySelector("form#crud-form");
  saveButton?.classList.toggle("d-none", !form);

  if (!event.detail.elt?.matches("[hx-get]") || !crudModal) {
    return;
  }

  const title = event.detail.elt?.dataset?.modalTitle;
  if (title) {
    document.querySelector("#crud-modal .modal-title").textContent = title;
  }

  crudModal.show();
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

window.addEventListener("DOMContentLoaded", (event) => {
  const sidebarToggle = document.body.querySelector("#sidebarToggle");
  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", (event) => {
      event.preventDefault();
      document.body.classList.toggle("sb-sidenav-toggled");
      localStorage.setItem("sb|sidebar-toggle", document.body.classList.contains("sb-sidenav-toggled"));
    });
  }
});

/* =========================================
   CADERNO — Adicionar bloco
   ========================================= */
document.addEventListener("click", function (event) {
  const botao = event.target.closest("[data-acao='adicionar-bloco']");
  if (!botao) return;

  const container = document.getElementById("containerBlocos");
  if (!container) return;

  const blocos = container.querySelectorAll(".bloco-item");
  const indice = blocos.length;
  const primeiroBloco = container.querySelector(".bloco-item");
  if (!primeiroBloco) return;

  const novoBloco = primeiroBloco.cloneNode(true);
  novoBloco.dataset.index = indice;

  const titulo = novoBloco.querySelector(".titulo-bloco");
  if (titulo) titulo.textContent = "BLOCO " + (indice + 1);

  // Dificuldades
  ["facil", "media", "dificil"].forEach(function (sufixo) {
    const input = novoBloco.querySelector(`input[value="${sufixo}"]`);
    if (input) {
      const novoId = `dif_${sufixo}_${indice}`;
      input.id = novoId;
      input.name = `blocos[${indice}][dificuldades]`;
      input.checked = false;
      const label = novoBloco.querySelector(`label[for^="dif_${sufixo}_"]`);
      if (label) label.setAttribute("for", novoId);
    }
  });

  // Selects — resetar e atualizar name
  const disciplinaSelect = novoBloco.querySelector(".disciplina-select");
  if (disciplinaSelect) {
    disciplinaSelect.name = `blocos[${indice}][disciplina]`;
    disciplinaSelect.value = "";
  }
  const assuntoSelect = novoBloco.querySelector(".assunto-select");
  if (assuntoSelect) {
    assuntoSelect.name = `blocos[${indice}][assunto]`;
    assuntoSelect.value = "";
  }

  // Quantidade
  const inputQtd = novoBloco.querySelector(".input-qtd");
  if (inputQtd) {
    inputQtd.name = `blocos[${indice}][quantidade]`;
    inputQtd.value = 10;
  }

  container.appendChild(novoBloco);
  atualizarResumoCaderno();
});

/* =========================================
   CADERNO — Remover bloco
   ========================================= */
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
  });

  atualizarResumoCaderno();
});

/* =========================================
   CADERNO — Quantidade (+ / −)
   ========================================= */
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

/* =========================================
   CADERNO — Resumo
   ========================================= */
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

/* =========================================
   CADERNO — Atualizar resumo ao abrir o modal
   ========================================= */
document.body.addEventListener("htmx:afterSwap", function (event) {
  if (event.detail.target?.id !== "modal-body") return;
  if (document.getElementById("containerBlocos")) {
    atualizarResumoCaderno();
  }
});