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
   CADERNO — Adicionar bloco via HTMX
   -----------------------------------------
   Antes de disparar a requisição HTMX, setamos `hx-vals` com o
   índice correto (calculado como número atual de blocos). A view
   renderizará o partial com `numero` e nomes/ids corretos.
   ========================================= */
document.addEventListener("click", function (event) {
  const botao = event.target.closest("#btnAdicionarBloco, #adicionarBloco");
  if (!botao) return;

  const container = document.getElementById("containerBlocos") || document.getElementById("blocosQuestoes");
  if (!container) return;

  // Índice calculado exatamente como no código anterior: número atual de blocos
  const indice = container.querySelectorAll(".bloco-item").length;

  // Define `hx-vals` dinamicamente para que o HTMX envie `index` na requisição
  try {
    botao.setAttribute("hx-vals", JSON.stringify({ index: indice }));
  } catch (e) {
    // se algo falhar, não impedir outras interações
    console.error("Erro ao setar hx-vals para adicionar bloco:", e);
  }
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

  // Re-numera todos os blocos restantes para garantir índices contínuos
  container.querySelectorAll(".bloco-item").forEach(function (b, i) {
    // data-index
    b.dataset.index = i;

    // Título visual BLOCO N
    const titulo = b.querySelector(".titulo-bloco");
    if (titulo) titulo.textContent = "BLOCO " + (i + 1);

    // Selects: disciplina e assunto
    const disciplinaSelect = b.querySelector(".disciplina-select");
    if (disciplinaSelect) {
      disciplinaSelect.name = `blocos[${i}][disciplina]`;
      // ajustar id se existir para manter compatibilidade
      disciplinaSelect.id = `disciplina_${i}`;
      // atualizar label que referencia esse select (se houver)
      const lbl = b.querySelector(`label[for]`);
      if (lbl && lbl.getAttribute("for") && lbl.getAttribute("for").toLowerCase().includes("disciplina")) {
        lbl.setAttribute("for", `disciplina_${i}`);
      }
    }

    const assuntoSelect = b.querySelector(".assunto-select");
    if (assuntoSelect) {
      assuntoSelect.name = `blocos[${i}][assunto]`;
      assuntoSelect.id = `assunto_${i}`;
      // atualizar label associado ao assunto, se existir
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
      // manter value
    }
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
  // Manter comportamento original (atualizar resumo ao abrir modal)
  if (event.detail.target?.id === "modal-body") {
    if (document.getElementById("containerBlocos")) {
      atualizarResumoCaderno();
    }
  }

  // Quando o HTMX inserir blocos diretamente em `#containerBlocos` ou `#blocosQuestoes`
  // atualizamos o resumo para refletir os blocos adicionados dinamicamente.
  if (event.detail.target?.id === "containerBlocos" || event.detail.target?.id === "blocosQuestoes") {
    atualizarResumoCaderno();
  }
});