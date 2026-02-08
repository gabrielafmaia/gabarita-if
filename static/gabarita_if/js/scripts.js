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

const spinner = `
<div class="d-flex justify-content-center align-items-center" style="height: 200px;">
    <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
    </div>
</div>`

document.querySelectorAll(".detalharQuestao").forEach(function(elemento) {
    elemento.addEventListener("click", function() {
        document.querySelector("#modal-questao .modal-body").innerHTML = spinner;
        // Pega a URL da questão a partir do atributo data-url
        const dataUrl = this.dataset.url;
        fetch(dataUrl)
            .then((response) => response.text())
            .then((html) => {
                document.querySelector("#modal-questao .modal-body").innerHTML = html;
            });
    });
});

// document.querySelectorAll(".form-like").forEach(function(form) {
//   form.addEventListener("submit", function(evento) {
//     evento.preventDefault(); // evita a submissão "normal" do form
//     const formData = new FormData(this);
//     fetch(this.getAttribute("action"), {
//       method: "POST",
//       body: new URLSearchParams(formData)})
//         .then((response) => response.json())
//         .then((resposta) => {
//           if (resposta.like) {
//             document.querySelector(`#like-${resposta.id_questao}`).innerHTML = `<span>${resposta.favoritos}</span><i class="bi bi-heart-fill ms-1"></i>`;
//           } else {
//             document.querySelector(`#like-${resposta.id_questao}`).innerHTML = `<span>${resposta.favoritos}</span><i class="bi bi-heart ms-1"></i>`;
//           }
//           buscarMensagens();
//       })
//       .catch((error) => {
//         alert(error);
//     });
//   });
// });

function buscarMensagens() {
  fetch(mensagensUrl)
    .then((response) => response.text())
    .then((html) => {
      document.querySelector("#div-mensagens").innerHTML = html;
    });
}

// const generosSelect = document.querySelector("#generos-select");
// if (generosSelect) {
//   generosSelect.addEventListener("change", function() {
//     const urlFiltrada = `${questaosUrl}?f=${this.value}`;
//     document.querySelector(".album").innerHTML = spinner;
//     fetch(urlFiltrada)
//       .then((response) => response.text())
//       .then((html) => {
//         document.querySelector(".album").innerHTML = html;
//       });
//   });
// }

function criarEventoPaginacao() {
  document.querySelectorAll(".page-link").forEach(function(link) {
    link.addEventListener("click", function(evento) {
      evento.preventDefault();
      const url = this.dataset.url;
      document.querySelector(".album").innerHTML = spinner;
      fetch(url)
        .then((response) => response.text())
        .then((html) => {
          document.querySelector(".album").innerHTML = html;
          criarEventoPaginacao();
        });
    });
  });
}
criarEventoPaginacao();

const meuModal = new bootstrap.Modal(".modal");

document.querySelector(".btn-criar").addEventListener("click", function(evento) {
    evento.preventDefault();
    fetch(this.href)
        .then(response => response.text())
        .then(conteudo => {
            document.querySelector(".modal-title").innerText = "Criar";
            document.querySelector(".modal-body").innerHTML = conteudo;
            document.querySelector(".form-questao").action = this.href;
            meuModal.show();
    })
})

document.querySelector(".btn-salvar").addEventListener("click", function(evento) {
    const formQuestao = document.querySelector(".form-questao");
    fetch(formQuestao.action, {"method": "POST", "body": new FormData(formQuestao)})
        .then(response => response.json())
        .then(conteudo => {
            meuModal.hide();
            buscarMensagens();
        })
})

document.querySelectorAll(".btn-detalhar").forEach(botao => {
    botao.addEventListener("click", evento => {
        evento.preventDefault();
        fetch(botao.href)
            .then(response => response.text())
            .then(conteudo => {
                document.querySelector(".modal-title").innerText = "Detalhar";
                document.querySelector(".modal-body").innerHTML = conteudo;
                document.querySelector(".btn-salvar").classList.add("d-none");
                meuModal.show();
            })
    })
})

document.querySelectorAll(".btn-editar").forEach(botao => {
    botao.addEventListener("click", evento => {
        evento.preventDefault();
        fetch(botao.href)
            .then(response => response.text())
            .then(conteudo => {
                document.querySelector(".modal-title").innerText = "Editar";
                document.querySelector(".modal-body").innerHTML = conteudo;
                document.querySelector(".form-questao").action = botao.href;
                meuModal.show();
            })
    })
})

document.querySelectorAll(".btn-remover").forEach(botao => {
    botao.addEventListener("click", evento => {
        evento.preventDefault();
        fetch(botao.href)
            .then(response => response.text())
            .then(conteudo => {
                document.querySelector(".modal-title").innerText = "Remover";
                document.querySelector(".modal-body").innerHTML = `<p>Confirma a remoção do item?</p>`;
                document.querySelector(".modal-footer").innerHTML = conteudo;
                document.querySelector(".form-remover").action = botao.href;
                meuModal.show();
            })
    })
})

document.querySelector(".btn-confirmar")?.addEventListener("click", function(evento) {
    const formRemover = document.querySelector(".form-remover");
    fetch(formRemover.action, {"method": "POST", "body": new FormData(formRemover)})
        .then(response => response.json())
        .then(conteudo => {
            meuModal.hide();
            buscarMensagens();
        })
})