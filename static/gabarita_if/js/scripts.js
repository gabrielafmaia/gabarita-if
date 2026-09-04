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

// Variável global para controle de índice de blocos adicionados
let contadorBlocosCaderno = 1;

// ============ FUNÇÃO PARA ENCONTRAR FORMULÁRIO ============
function encontrarFormularioNoModal() {
    const modalBody = document.querySelector("#modalPadrao .modal-body");
    if (!modalBody) {
        console.warn("⚠️ Modal-body não encontrado");
        return null;
    }
    
    let form = modalBody.querySelector("form");
    
    // Fallback: Se o HTML retornado vier sem a tag <form>, envolve o conteúdo em uma
    if (!form && modalBody.innerHTML.trim() !== "") {
        const tempContent = modalBody.innerHTML;
        modalBody.innerHTML = `<form id="form-dinamico" method="post">${tempContent}</form>`;
        form = modalBody.querySelector("#form-dinamico");
        
        // Adiciona CSRF token se não existir
        if (form && !form.querySelector('input[name="csrfmiddlewaretoken"]')) {
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
            form.prepend(csrfInput);
        }
    }

    if (form) {
        console.log("✅ Formulário encontrado!");
    } else {
        console.warn("⚠️ Nenhum formulário encontrado no modal");
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
            console.log("✅ Painel sincronizado via AJAX!");
        } else {
            window.location.reload();
        }
    })
    .catch(erro => {
        console.error("❌ Erro ao sincronizar dados:", erro);
        window.location.reload();
    });
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
            .catch(erro => console.error("❌ Erro ao carregar mensagens:", erro));
    }
}

// Função para mostrar mensagens de sucesso/erro
function mostrarMensagem(mensagem, tipo = 'success') {
    const divMsg = document.querySelector("#div-mensagens");
    if (divMsg) {
        const alertClass = tipo === 'success' ? 'alert-success' : 'alert-danger';
        divMsg.innerHTML = `
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                ${mensagem}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        // Auto-fade após 5 segundos
        setTimeout(() => {
            const alert = divMsg.querySelector('.alert');
            if (alert) {
                alert.classList.remove('show');
                setTimeout(() => alert.remove(), 300);
            }
        }, 5000);
    } else {
        alert(mensagem);
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
    
    // Controles de quantidade (+ / -)
    const btnQtdMinus = evento.target.closest(".btn-qtd-minus");
    const btnQtdPlus = evento.target.closest(".btn-qtd-plus");

    // ============ Ação: BOTÃO MENOS (-) ============
    if (btnQtdMinus) {
        evento.preventDefault();
        const input = btnQtdMinus.closest('.input-group').querySelector('.input-qtd');
        if (input) {
            let val = parseInt(input.value) || 1;
            if (val > 1) {
                input.value = val - 1;
                atualizarResumoCaderno();
            }
        }
        return;
    }

    // ============ Ação: BOTÃO MAIS (+) ============
    if (btnQtdPlus) {
        evento.preventDefault();
        const input = btnQtdPlus.closest('.input-group').querySelector('.input-qtd');
        if (input) {
            let val = parseInt(input.value) || 0;
            input.value = val + 1;
            atualizarResumoCaderno();
        }
        return;
    }

    // ============ Ação: CRIAR ============
    if (btnCriar) {
        evento.preventDefault();
        evento.stopPropagation();
        
        const urlCriar = btnCriar.getAttribute("href") || btnCriar.dataset.url;
        const modalBody = document.querySelector("#modalPadrao .modal-body");
        const modalTitle = document.querySelector("#modalPadrao .modal-title");

        if (modalTitle) modalTitle.innerText = "Criar";
        if (modalBody) modalBody.innerHTML = spinner;
        
        restaurarBotoesModalPadrao();
        if (meuModal) meuModal.show();
        
        console.log("🔄 Carregando formulário de criação:", urlCriar);
        
        fetch(urlCriar, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => {
            if (!response.ok) throw new Error(`Erro HTTP ${response.status}`);
            return response.text();
        })
        .then(conteudo => {
            if (modalBody) {
                modalBody.innerHTML = conteudo;
                console.log("✅ Conteúdo inserido no modal");
            }
            
            // Procura e configura o formulário
            setTimeout(() => {
                const form = encontrarFormularioNoModal();
                if (form) {
                    form.action = urlCriar;
                    form.method = "POST";
                    // Adiciona classe para ser capturado pelo submit listener
                    form.classList.add('js-ajax-form');
                    console.log("✅ Formulário configurado com action:", form.action);
                } else {
                    console.warn("⚠️ Formulário não encontrado após carregar");
                }
            }, 100);
            
            contadorBlocosCaderno = document.querySelectorAll('#modalPadrao .bloco-item').length || 1;
            atualizarResumoCaderno();
        })
        .catch(erro => {
            console.error("❌ Erro no modal de criação:", erro);
            if (modalBody) {
                modalBody.innerHTML = `
                    <div class="alert alert-danger">
                        <strong>Erro ao carregar o formulário!</strong><br>
                        ${erro.message}
                    </div>
                `;
            }
        });
    }

    // ============ Ação: DETALHAR ============
    if (btnDetalhar) {
        evento.preventDefault();
        const urlDetalhar = btnDetalhar.getAttribute("href");
        const modalBody = document.querySelector("#modalPadrao .modal-body");
        const modalTitle = document.querySelector("#modalPadrao .modal-title");

        if (modalTitle) modalTitle.innerText = "Detalhes do Caderno";
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
        .catch(erro => {
            console.error("❌ Erro ao detalhar:", erro);
            if (modalBody) {
                modalBody.innerHTML = `<div class="alert alert-danger">Erro ao carregar detalhes.</div>`;
            }
        });
    }

    // ============ Ação: EDITAR ============
    if (btnEditar) {
        evento.preventDefault();
        const urlEditar = btnEditar.getAttribute("href");
        const modalBody = document.querySelector("#modalPadrao .modal-body");
        const modalTitle = document.querySelector("#modalPadrao .modal-title");

        if (modalTitle) modalTitle.innerText = "Editar Caderno";
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
            
            setTimeout(() => {
                const form = encontrarFormularioNoModal();
                if (form) {
                    form.action = urlEditar;
                    form.method = "POST";
                    form.classList.add('js-ajax-form');
                    console.log("✅ Formulário de edição configurado");
                }
            }, 100);
        })
        .catch(erro => {
            console.error("❌ Erro ao editar:", erro);
            if (modalBody) {
                modalBody.innerHTML = `<div class="alert alert-danger">Erro ao carregar formulário de edição.</div>`;
            }
        });
    }

    // ============ Ação: REMOVER ============
    if (btnRemover) {
        evento.preventDefault();
        const urlRemover = btnRemover.getAttribute("href");
        linhaParaRemover = btnRemover.closest("tr");
        const modalBody = document.querySelector("#modalPadrao .modal-body");
        const modalTitle = document.querySelector("#modalPadrao .modal-title");

        if (modalTitle) modalTitle.innerText = "Remover Caderno";

        fetch(urlRemover, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => {
            if (!response.ok) throw new Error(`Erro HTTP ${response.status}`);
            return response.text();
        })
        .then(conteudo => {
            if (modalBody) {
                modalBody.innerHTML = `<p class="mb-0 text-danger">⚠️ Confirma a remoção deste caderno?</p>`;
            }
            
            const modalFooter = document.querySelector("#modalPadrao .modal-footer");
            if (modalFooter) modalFooter.innerHTML = conteudo;
            
            const formRemover = document.querySelector("#modalPadrao form");
            if (formRemover) {
                formRemover.action = urlRemover;
                formRemover.method = "POST";
            }
            
            if (meuModal) meuModal.show();
        })
        .catch(erro => {
            console.error("❌ Erro ao remover:", erro);
        });
    }

    // ============ Ação: CONFIRMAR REMOÇÃO ============
    if (btnConfirmar) {
        evento.preventDefault();
        const formRemover = document.querySelector("#modalPadrao form");
        
        if (formRemover) {
            fetch(formRemover.action, {
                method: "POST", 
                body: new FormData(formRemover),
                headers: { 
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                }
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
                    mostrarMensagem("Caderno removido com sucesso!", "success");
                } else {
                    throw new Error(`Erro HTTP ${response.status}`);
                }
            })
            .catch(erro => {
                console.error("❌ Erro ao confirmar remoção:", erro);
                mostrarMensagem("Erro ao remover caderno!", "danger");
                if (meuModal) meuModal.hide();
                atualizarTabela();
            });
        }
    }

    // ============ Ação: SALVAR (BOTÃO NO RODAPÉ PADRÃO DO MODAL) ============
    if (btnSalvar) {
        evento.preventDefault();
        evento.stopPropagation();
        
        console.log("🔄 Botão SALVAR clicado!");

        const formAtivo = encontrarFormularioNoModal();
        
        if (!formAtivo) {
            console.error("❌ Formulário não encontrado!");
            mostrarMensagem("Erro: Formulário não encontrado!", "danger");
            return;
        }

        // Garante que o action está definido
        if (!formAtivo.action || formAtivo.action === window.location.href) {
            const btnCriar = document.querySelector(".btn-criar");
            if (btnCriar) {
                formAtivo.action = btnCriar.getAttribute("href") || btnCriar.dataset.url;
                console.log("📝 Action definido a partir do btn-criar:", formAtivo.action);
            }
        }

        formAtivo.method = "POST";
        formAtivo.classList.add('js-ajax-form');
        
        console.log("📝 URL de ação:", formAtivo.action);
        console.log("📝 Método:", formAtivo.method);

        // Força a validação do formulário
        if (formAtivo.checkValidity()) {
            // Dispara o evento submit que será capturado pelo listener abaixo
            formAtivo.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
        } else {
            formAtivo.reportValidity();
            console.warn("⚠️ Formulário com campos inválidos");
        }
    }
});

// ============= DELEGAÇÃO GLOBAL DE SUBMIT PARA FORMULÁRIOS AJAX =============
document.addEventListener('submit', function (e) {
    const form = e.target.closest('form');
    
    // Verifica se o formulário deve ser processado via AJAX
    if (!form || (!form.classList.contains('js-ajax-form') && !form.closest('#modalPadrao'))) return;

    e.preventDefault();
    e.stopPropagation();

    console.log("📤 Submetendo formulário via AJAX...");
    console.log("📝 URL:", form.action);
    console.log("📝 Método:", form.method);

    const formData = new FormData(form);
    const actionUrl = form.getAttribute('action') || window.location.href;

    // Mostra loading no botão salvar se existir
    const btnSalvar = form.closest('#modalPadrao')?.querySelector('.btn-salvar');
    const btnOriginal = btnSalvar ? btnSalvar.innerHTML : '';
    if (btnSalvar) {
        btnSalvar.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Salvando...';
        btnSalvar.disabled = true;
    }

    fetch(actionUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
        }
    })
    .then(async response => {
        console.log("📡 Resposta recebida:", response.status);
        
        const contentType = response.headers.get("content-type");
        const responseText = await response.text();
        console.log("📦 Conteúdo da resposta (primeiros 500 caracteres):", responseText.substring(0, 500));
        
        // Tenta parsear como JSON
        try {
            const data = JSON.parse(responseText);
            console.log("📦 Dados JSON:", data);
            
            if (response.ok && (data.success || data.status === 'ok')) {
                if (meuModal) meuModal.hide();
                mostrarMensagem(data.message || "Caderno salvo com sucesso!", "success");
                
                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                } else {
                    atualizarTabela();
                    buscarMensagens();
                }
                return;
            } else if (data.redirect_url) {
                window.location.href = data.redirect_url;
                return;
            } else if (data.errors) {
                // Mostra erros de validação específicos
                let erroMsg = '';
                if (typeof data.errors === 'object') {
                    erroMsg = Object.entries(data.errors)
                        .map(([campo, erros]) => `<li><strong>${campo}:</strong> ${erros.join(', ')}</li>`)
                        .join('');
                } else {
                    erroMsg = data.errors;
                }
                
                const modalBody = document.querySelector("#modalPadrao .modal-body");
                if (modalBody) {
                    modalBody.innerHTML = `
                        <div class="alert alert-danger">
                            <strong>Erros de validação:</strong>
                            <ul>${erroMsg}</ul>
                        </div>
                        ${responseText.includes('<form') ? responseText : ''}
                    `;
                }
                mostrarMensagem("Corrija os erros do formulário.", "danger");
                return;
            }
        } catch (e) {
            // Não é JSON, trata como HTML
            console.log("📄 Resposta é HTML, não JSON");
        }
        
        // Se chegou aqui, é HTML
        const modalBody = document.querySelector("#modalPadrao .modal-body");
        
        if (response.status === 400 || response.status === 422 || response.status === 500) {
            // Erro - mostra o HTML retornado
            if (modalBody) {
                modalBody.innerHTML = responseText;
                // Reconfigura o formulário
                setTimeout(() => {
                    const novoForm = encontrarFormularioNoModal();
                    if (novoForm) {
                        novoForm.action = actionUrl;
                        novoForm.method = "POST";
                        novoForm.classList.add('js-ajax-form');
                    }
                }, 50);
            }
            
            // Tenta extrair mensagem de erro do HTML
            const erroMatch = responseText.match(/<div class="alert alert-danger[^>]*>([\s\S]*?)<\/div>/i);
            if (erroMatch) {
                mostrarMensagem(erroMatch[1].trim(), "danger");
            } else {
                mostrarMensagem("Erro ao salvar o caderno. Verifique os dados.", "danger");
            }
        } else if (response.ok) {
            // Sucesso, mas resposta não é JSON
            if (meuModal) meuModal.hide();
            mostrarMensagem("Caderno salvo com sucesso!", "success");
            atualizarTabela();
            buscarMensagens();
        } else {
            throw new Error(`Erro HTTP ${response.status}`);
        }
    })
    .catch(error => {
        console.error('❌ Erro na submissão AJAX:', error);
        mostrarMensagem(`Erro ao salvar: ${error.message}`, "danger");
        atualizarTabela();
    })
    .finally(() => {
        // Restaura o botão
        if (btnSalvar) {
            btnSalvar.innerHTML = btnOriginal;
            btnSalvar.disabled = false;
        }
    });
});

// ============= FUNÇÕES DO BLOCO DO CADERNO =============
window.atualizarResumoCaderno = function() {
    let total = 0;
    document.querySelectorAll('#modalPadrao .input-qtd').forEach(input => {
        total += parseInt(input.value) || 0;
    });
    
    const resumoTotal = document.getElementById('resumoTotal');
    if (resumoTotal) resumoTotal.innerText = total;

    const resumoBlocos = document.getElementById('resumoBlocos');
    const qtdBlocos = document.querySelectorAll('#modalPadrao .bloco-item').length;
    if (resumoBlocos) resumoBlocos.innerText = `${qtdBlocos} Bloco(s)`;
};

window.adicionarBlocoCaderno = function() {
    const container = document.getElementById('containerBlocos');
    if (!container) {
        console.warn("⚠️ Container de blocos não encontrado");
        return;
    }
    
    const index = contadorBlocosCaderno++;
    const novoBloco = document.createElement('div');
    novoBloco.className = 'bloco-item border rounded-3 p-3 bg-light mb-3';
    novoBloco.setAttribute('data-index', index);

    const primeiroSelectDisc = document.querySelector('.select-disciplina');
    const primeiroSelectTop = document.querySelector('.select-topico');

    const opcoesDisciplinas = primeiroSelectDisc ? primeiroSelectDisc.innerHTML : '<option value="">Selecione a disciplina</option>';
    const opcoesTopicos = primeiroSelectTop ? primeiroSelectTop.innerHTML : '<option value="">Tópicos: Todos</option>';

    novoBloco.innerHTML = `
      <div class="d-flex justify-content-between align-items-center mb-2">
        <span class="badge bg-dark text-white titulo-bloco">BLOCO ${container.children.length + 1}</span>
        <button type="button" class="btn btn-link text-danger p-0 text-decoration-none small" onclick="removerBlocoCaderno(this)">Excluir bloco</button>
      </div>

      <div class="mb-2">
        <label class="form-label fw-semibold small text-muted mb-1">Dificuldade</label>
        <div class="d-flex gap-2">
          <input type="checkbox" class="btn-check" id="dif_facil_${index}" name="blocos[${index}][dificuldades]" value="facil" checked>
          <label class="btn btn-sm btn-outline-success flex-fill rounded-pill" for="dif_facil_${index}">Fácil</label>

          <input type="checkbox" class="btn-check" id="dif_media_${index}" name="blocos[${index}][dificuldades]" value="media" checked>
          <label class="btn btn-sm btn-outline-warning flex-fill rounded-pill" for="dif_media_${index}">Moderada</label>

          <input type="checkbox" class="btn-check" id="dif_dificil_${index}" name="blocos[${index}][dificuldades]" value="dificil" checked>
          <label class="btn btn-sm btn-outline-danger flex-fill rounded-pill" for="dif_dificil_${index}">Difícil</label>
        </div>
      </div>

      <div class="row g-2 mb-2">
        <div class="col-md-6">
          <select class="form-select form-select-sm rounded-3 select-disciplina" name="blocos[${index}][disciplina]" required>
            ${opcoesDisciplinas}
          </select>
        </div>
        <div class="col-md-6">
          <select class="form-select form-select-sm rounded-3 select-topico" name="blocos[${index}][topico]">
            ${opcoesTopicos}
          </select>
        </div>
      </div>

      <div class="d-flex align-items-center gap-2 mt-2">
        <span class="small fw-semibold text-muted">N.º de questões:</span>
        <div class="input-group input-group-sm" style="width: 110px;">
          <button class="btn btn-outline-secondary btn-qtd-minus" type="button">-</button>
          <input type="text" class="form-control text-center bg-white input-qtd" name="blocos[${index}][quantidade]" value="10" readonly>
          <button class="btn btn-outline-secondary btn-qtd-plus" type="button">+</button>
        </div>
      </div>
    `;

    container.appendChild(novoBloco);
    atualizarResumoCaderno();
    console.log("✅ Bloco adicionado:", index);
};

window.removerBlocoCaderno = function(btn) {
    const bloco = btn.closest('.bloco-item');
    if (bloco) {
        bloco.remove();
        document.querySelectorAll('#modalPadrao .bloco-item').forEach((b, idx) => {
            const titulo = b.querySelector('.titulo-bloco');
            if (titulo) titulo.innerText = `BLOCO ${idx + 1}`;
        });
        atualizarResumoCaderno();
        console.log("✅ Bloco removido");
    }
};

// ============= INICIALIZAÇÃO =============
document.addEventListener("DOMContentLoaded", function() {
    console.log("✅ Script do Caderno carregado!");
    buscarMensagens();
    
    // Inicializa o resumo se houver blocos
    setTimeout(atualizarResumoCaderno, 300);
});