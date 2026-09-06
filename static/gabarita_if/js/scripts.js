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
