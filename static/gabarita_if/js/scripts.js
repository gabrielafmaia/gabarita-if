// Constante do Spinner compartilhada
const spinner = `
<div class="d-flex justify-content-center align-items-center" style="height: 200px;">
    <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
    </div>
</div>`;

const meuModal = new bootstrap.Modal(".modal");

// Variável global para armazenar a linha (<tr>) que será removida após a confirmação
let linhaParaRemover = null;

// Função para restaurar o rodapé padrão do modal (limpa resquícios do botão Remover)
function restaurarBotoesModalPadrao() {
    const modalFooter = document.querySelector(".modal-footer");
    if (modalFooter) {
        // Reconstrói o rodapé com os botões originais do Bootstrap
        modalFooter.innerHTML = `
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
            <button type="button" class="btn btn-primary btn-salvar">Salvar</button>
        `;
    }
}

// Função que atualiza o painel .card inteiro via AJAX
function atualizarTabela() {
    const urlSemCache = window.location.origin + window.location.pathname + '?t=' + new Date().getTime();

    fetch(urlSemCache, { 
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' } 
    })
    .then(response => {
        if (!response.ok) throw new Error("Erro na requisição");
        return response.text();
    })
    .then(html => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, "text/html");
        
        const cardNovo = doc.querySelector(".card");
        const cardAtual = document.querySelector(".card");

        if (cardNovo && cardAtual) {
            cardAtual.innerHTML = cardNovo.innerHTML;
            console.log("Painel sincronizado via AJAX com sucesso!");
        }
    })
    .catch(erro => console.error("Erro ao sincronizar dados:", erro));
}

// Ouvinte de eventos global (Event Delegation) para elementos dinâmicos
document.addEventListener("click", function(evento) {
    const btnDetalhar = evento.target.closest(".btn-detalhar");
    const btnEditar = evento.target.closest(".btn-editar");
    const btnRemover = evento.target.closest(".btn-remover");
    const btnConfirmar = evento.target.closest(".btn-confirmar");
    const btnSalvar = evento.target.closest(".btn-salvar"); // Captura o clique no botão salvar mesmo recriado

    // Ação: Detalhar
    if (btnDetalhar) {
        evento.preventDefault();
        fetch(btnDetalhar.href)
            .then(response => response.text())
            .then(conteudo => {
                restaurarBotoesModalPadrao();
                document.querySelector(".modal-title").innerText = "Detalhar";
                document.querySelector(".modal-body").innerHTML = conteudo;
                document.querySelector(".btn-salvar")?.classList.add("d-none"); 
                meuModal.show();
            });
    }

    // Ação: Editar
    if (btnEditar) {
        evento.preventDefault();
        fetch(btnEditar.href)
            .then(response => response.text())
            .then(conteudo => {
                restaurarBotoesModalPadrao(); // Garante o botão "Salvar" azul
                document.querySelector(".modal-title").innerText = "Editar";
                document.querySelector(".modal-body").innerHTML = conteudo;
                
                const formQuestao = document.querySelector(".form-questao");
                if (formQuestao) formQuestao.action = btnEditar.href;
                
                meuModal.show();
            });
    }

    // Ação: Remover
    if (btnRemover) {
        evento.preventDefault();
        linhaParaRemover = btnRemover.closest("tr");

        fetch(btnRemover.href)
            .then(response => response.text())
            .then(conteudo => {
                document.querySelector(".modal-title").innerText = "Remover";
                document.querySelector(".modal-body").innerHTML = `<p>Confirma a remoção do item?</p>`;
                
                // Injeta o rodapé enviado pelo Django que contém o botão "Confirmar" vermelho
                const modalFooter = document.querySelector(".modal-footer");
                if (modalFooter) modalFooter.innerHTML = conteudo;
                
                const formRemover = document.querySelector(".form-remover");
                if (formRemover) formRemover.action = btnRemover.href;
                
                meuModal.show();
            })
            .catch(erro => console.error("Erro ao carregar modal de remoção:", erro));
    }

    // Ação: Confirmar Remoção
    if (btnConfirmar) {
        evento.preventDefault();
        const formRemover = document.querySelector(".form-remover");
        
        if (formRemover) {
            fetch(formRemover.action, {
                method: "POST", 
                body: new FormData(formRemover),
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.ok ? response.text() : Promise.reject("Erro ao remover"))
            .then(() => {
                meuModal.hide();
                if (linhaParaRemover) {
                    linhaParaRemover.remove();
                    linhaParaRemover = null;
                }
                atualizarTabela();
                if (typeof buscarMensagens === "function") buscarMensagens();
            })
            .catch(erro => {
                console.error("Erro ao remover:", erro);
                meuModal.hide();
                atualizarTabela();
            });
        }
    }

    // Ação: Salvar (Criar ou Editar) - Capturado via delegação global
    if (btnSalvar) {
        const formQuestao = document.querySelector(".form-questao");
        if (formQuestao) {
            evento.preventDefault();
            fetch(formQuestao.action, {
                method: "POST", 
                body: new FormData(formQuestao),
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.ok ? response.text() : Promise.reject("Erro no servidor"))
            .then(() => {
                meuModal.hide();
                atualizarTabela(); 
                if (typeof buscarMensagens === "function") buscarMensagens();
            })
            .catch(erro => console.error("Erro ao salvar:", erro));
        }
    }
});

// Botão que abre a tela de Criação
document.querySelector(".btn-criar")?.addEventListener("click", function(evento) {
    evento.preventDefault();
    fetch(this.href)
        .then(response => response.text())
        .then(conteudo => {
            restaurarBotoesModalPadrao(); // Garante que o botão volte a ser "Salvar" e limpa o lixo do remover
            document.querySelector(".modal-title").innerText = "Criar";
            document.querySelector(".modal-body").innerHTML = conteudo;
            document.querySelector(".form-questao").action = this.href;
            meuModal.show();
        });
});

// Suporte para o seletor antigo .detalharQuestao
document.querySelectorAll(".detalharQuestao").forEach(function(elemento) {
    elemento.addEventListener("click", function() {
        document.querySelector("#modal-questao .modal-body").innerHTML = spinner;
        const dataUrl = this.dataset.url;
        fetch(dataUrl)
            .then((response) => response.text())
            .then((html) => {
                document.querySelector("#modal-questao .modal-body").innerHTML = html;
            });
    });
});

// Busca mensagens flash do Django de forma assíncrona
function buscarMensagens() {
    if (typeof mensagensUrl !== 'undefined') {
        fetch(mensagensUrl)
            .then((response) => response.text())
            .then((html) => {
                const divMsg = document.querySelector("#div-mensagens");
                if (divMsg) divMsg.innerHTML = html;
            });
    }
}