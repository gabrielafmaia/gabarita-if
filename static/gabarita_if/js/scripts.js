// Constante do Spinner compartilhada
const spinner = `
<div class="d-flex justify-content-center align-items-center" style="height: 200px;">
    <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Carregando...</span>
    </div>
</div>`;

// Inicializa a instância única da Modal usando o ID correto
const modalElement = document.getElementById("modalPadrao");
const meuModal = modalElement ? new bootstrap.Modal(modalElement) : null;

// Variável global para armazenar a linha (<tr>) selecionada para remoção
let linhaParaRemover = null;

// ============ FUNÇÃO PARA ENCONTRAR FORMULÁRIO ============
function encontrarFormularioNoModal() {
    const modalBody = document.querySelector("#modalPadrao .modal-body");
    if (!modalBody) return null;
    
    let form = modalBody.querySelector("form");
    
    // Fallback: Se o HTML retornado vier sem a tag <form>, envolve o conteúdo em um
    if (!form && modalBody.innerHTML.trim() !== "") {
        const tempContent = modalBody.innerHTML;
        modalBody.innerHTML = `<form id="form-dinamico">${tempContent}</form>`;
        form = modalBody.querySelector("#form-dinamico");
    }

    return form;
}

// Função para restaurar os botões do rodapé padrão do modal
function restaurarBotoesModalPadrao() {
    const modalFooter = document.querySelector("#modalPadrao .modal-footer");
    if (modalFooter) {
        modalFooter.innerHTML = `
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
            <button type="button" class="btn btn-primary btn-salvar">Salvar</button>
        `;
    }
}

// Função para atualizar a tabela via AJAX após inserção/edição/deleção
function atualizarTabela() {
    const urlSemCache = window.location.origin + window.location.pathname + '?t=' + new Date().getTime();

    fetch(urlSemCache, { 
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' } 
    })
    .then(response => {
        if (!response.ok) throw new Error("Erro na requisição ao atualizar tabela");
        return response.text();
    })
    .then(html => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, "text/html");
        
        const cardNovo = doc.querySelector(".card");
        const cardAtual = document.querySelector(".card");

        if (cardNovo && cardAtual) {
            cardAtual.innerHTML = cardNovo.innerHTML;
        }
    })
    .catch(erro => console.error("Erro ao sincronizar dados:", erro));
}

// Função para buscar mensagens flash do Django
function buscarMensagens() {
    if (typeof mensagensUrl !== 'undefined' && mensagensUrl) {
        fetch(mensagensUrl)
            .then(response => response.text())
            .then(html => {
                const divMsg = document.querySelector("#div-mensagens");
                if (divMsg) divMsg.innerHTML = html;
            })
            .catch(erro => console.error("Erro ao carregar mensagens:", erro));
    }
}

// ============= LISTENER PRINCIPAL DE CLIQUES =============
document.addEventListener("click", function(evento) {
    const btnCriar = evento.target.closest(".btn-criar");
    const btnDetalhar = evento.target.closest(".btn-detalhar");
    const btnEditar = evento.target.closest(".btn-editar");
    const btnRemover = evento.target.closest(".btn-remover");
    const btnConfirmar = evento.target.closest(".btn-confirmar");
    const btnSalvar = evento.target.closest(".btn-salvar");

    // ============ Ação: CRIAR ============
    if (btnCriar) {
        evento.preventDefault();
        evento.stopPropagation(); // Evita re-disparos em cadeia
        
        const urlCriar = btnCriar.getAttribute("href") || btnCriar.dataset.url;
        const modalBody = document.querySelector("#modalPadrao .modal-body");
        const modalTitle = document.querySelector("#modalPadrao .modal-title");

        if (modalTitle) modalTitle.innerText = "Criar";
        if (modalBody) modalBody.innerHTML = spinner;
        
        restaurarBotoesModalPadrao();
        if (meuModal) meuModal.show();
        
        fetch(urlCriar, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => {
            if (!response.ok) throw new Error(`Erro HTTP ${response.status}`);
            return response.text();
        })
        .then(conteudo => {
            if (modalBody) modalBody.innerHTML = conteudo;
            
            const form = encontrarFormularioNoModal();
            if (form) {
                form.action = urlCriar;
                form.method = "POST";
            }
        })
        .catch(erro => {
            console.error("❌ Erro no modal de criação:", erro);
            if (modalBody) {
                modalBody.innerHTML = `<div class="alert alert-danger">Erro ao carregar o formulário.</div>`;
            }
        });
    }

    // ============ Ação: DETALHAR ============
    if (btnDetalhar) {
        evento.preventDefault();
        const urlDetalhar = btnDetalhar.getAttribute("href");
        const modalBody = document.querySelector("#modalPadrao .modal-body");
        const modalTitle = document.querySelector("#modalPadrao .modal-title");

        if (modalTitle) modalTitle.innerText = "Detalhes do Usuário";
        if (modalBody) modalBody.innerHTML = spinner;
        if (meuModal) meuModal.show();

        fetch(urlDetalhar, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => {
            if (!response.ok) throw new Error(`Erro HTTP ${response.status}`);
            return response.text();
        })
        .then(conteudo => {
            if (modalBody) modalBody.innerHTML = conteudo;
            const modalFooter = document.querySelector("#modalPadrao .modal-footer");
            if (modalFooter) {
                modalFooter.innerHTML = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>`;
            }
        })
        .catch(erro => console.error("❌ Erro ao detalhar:", erro));
    }

    // ============ Ação: EDITAR ============
    if (btnEditar) {
        evento.preventDefault();
        const urlEditar = btnEditar.getAttribute("href");
        const modalBody = document.querySelector("#modalPadrao .modal-body");
        const modalTitle = document.querySelector("#modalPadrao .modal-title");

        if (modalTitle) modalTitle.innerText = "Editar Usuário";
        if (modalBody) modalBody.innerHTML = spinner;
        
        restaurarBotoesModalPadrao();
        if (meuModal) meuModal.show();

        fetch(urlEditar, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => {
            if (!response.ok) throw new Error(`Erro HTTP ${response.status}`);
            return response.text();
        })
        .then(conteudo => {
            if (modalBody) modalBody.innerHTML = conteudo;
            
            const form = encontrarFormularioNoModal();
            if (form) {
                form.action = urlEditar;
                form.method = "POST";
            }
        })
        .catch(erro => console.error("❌ Erro ao editar:", erro));
    }

    // ============ Ação: REMOVER ============
    if (btnRemover) {
        evento.preventDefault();
        const urlRemover = btnRemover.getAttribute("href");
        linhaParaRemover = btnRemover.closest("tr");
        const modalBody = document.querySelector("#modalPadrao .modal-body");
        const modalTitle = document.querySelector("#modalPadrao .modal-title");

        if (modalTitle) modalTitle.innerText = "Remover Usuário";

        fetch(urlRemover, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => {
            if (!response.ok) throw new Error(`Erro HTTP ${response.status}`);
            return response.text();
        })
        .then(conteudo => {
            if (modalBody) {
                modalBody.innerHTML = `<p class="mb-0 text-danger">⚠️ Confirma a remoção deste usuário?</p>`;
            }
            
            const modalFooter = document.querySelector("#modalPadrao .modal-footer");
            if (modalFooter) modalFooter.innerHTML = conteudo;
            
            const formRemover = document.querySelector("#modalPadrao form");
            if (formRemover) formRemover.action = urlRemover;
            
            if (meuModal) meuModal.show();
        })
        .catch(erro => console.error("❌ Erro ao remover:", erro));
    }

    // ============ Ação: CONFIRMAR REMOÇÃO ============
    if (btnConfirmar) {
        evento.preventDefault();
        const formRemover = document.querySelector("#modalPadrao form");
        
        if (formRemover) {
            fetch(formRemover.action, {
                method: "POST", 
                body: new FormData(formRemover),
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => {
                if (response.ok) {
                    if (meuModal) meuModal.hide();
                    if (linhaParaRemover) {
                        linhaParaRemover.remove();
                        linhaParaRemover = null;
                    }
                    atualizarTabela();
                    buscarMensagens();
                }
            })
            .catch(erro => console.error("❌ Erro ao confirmar remoção:", erro));
        }
    }

    // ============ Ação: SALVAR ============
    if (btnSalvar) {
        evento.preventDefault();
        
        const formAtivo = encontrarFormularioNoModal();
        
        if (formAtivo) {
            const urlAcao = formAtivo.action || window.location.href;
            
            fetch(urlAcao, {
                method: "POST", 
                body: new FormData(formAtivo),
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => {
                if (response.ok) {
                    if (meuModal) meuModal.hide();
                    atualizarTabela();
                    buscarMensagens();
                } else if (response.status === 400) {
                    // Erros de validação do Django (Formulário inválido)
                    return response.text().then(htmlComErros => {
                        const modalBody = document.querySelector("#modalPadrao .modal-body");
                        if (modalBody) modalBody.innerHTML = htmlComErros;
                    });
                }
            })
            .catch(erro => console.error("❌ Erro ao salvar dados:", erro));
        }
    }
});

// Inicialização
document.addEventListener("DOMContentLoaded", function() {
    buscarMensagens();
});