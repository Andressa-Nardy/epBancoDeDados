document.addEventListener('DOMContentLoaded', () => {

    // =================================================================
    // 1. NAVEGAÇÃO SPA
    // =================================================================
    const navButtons = document.querySelectorAll('.nav-btn');
    const sections = document.querySelectorAll('.view-section');

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            navButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const targetId = btn.dataset.target;
            sections.forEach(sec => {
                sec.classList.add('hidden');
                sec.classList.remove('active');
            });
            const targetSection = document.getElementById(targetId);
            if(targetSection) {
                targetSection.classList.remove('hidden');
                targetSection.classList.add('active');
            }
        });
    });

    // =================================================================
    // 2. CADASTRO DE USUÁRIO
    // =================================================================
    const formCadastro = document.getElementById('form-cadastro');
    const mensagemCadastro = document.getElementById('mensagem-cadastro');

    if (formCadastro) {
        formCadastro.addEventListener('submit', (evento) => {
            evento.preventDefault();
            mensagemCadastro.textContent = 'Enviando...';
            mensagemCadastro.style.color = 'black';

            const dadosFormulario = new FormData(formCadastro);
            const dadosUsuario = Object.fromEntries(dadosFormulario.entries());

            fetch('http://127.0.0.1:8000/usuario/cadastrar', { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dadosUsuario)
            })
            .then(res => res.json())
            .then(res => {
                if (res.erro) {
                    mensagemCadastro.textContent = `Erro: ${res.erro}`;
                    mensagemCadastro.style.color = 'red';
                } else {
                    mensagemCadastro.textContent = res.mensagem || "Cadastrado com sucesso!";
                    mensagemCadastro.style.color = 'green';
                    formCadastro.reset();
                }
            })
            .catch(err => {
                console.error(err);
                mensagemCadastro.textContent = "Erro de conexão.";
                mensagemCadastro.style.color = 'red';
            });
        });
    }

    // =================================================================
    // 3. ANÁLISE (Dashboards)
    // =================================================================
    const btnAnalisar = document.getElementById('btnCarregarAnalise');
    const listaResultados = document.getElementById('lista-resultados-analise');
    const selectAnalise = document.getElementById('select-analise');

    if (btnAnalisar && selectAnalise) {
        btnAnalisar.addEventListener('click', () => {
            listaResultados.innerHTML = '<li>Carregando...</li>';
            const endpoint = selectAnalise.value;
            const url = `http://127.0.0.1:8000/analise/${endpoint}`;

            fetch(url)
                .then(r => r.json())
                .then(data => formatarAnalise(data))
                .catch(e => {
                    console.error(e);
                    listaResultados.innerHTML = '<li>Erro de conexão. Verifique o backend.</li>';
                });
        });
    }

    function formatarAnalise(dados) {
        listaResultados.innerHTML = '';
        if (!dados || (Array.isArray(dados) && dados.length === 0)) {
            listaResultados.innerHTML = '<li>Nenhum dado encontrado.</li>'; 
            return;
        }

        const criarItem = (obj) => {
            const li = document.createElement('li');
            for (const k in obj) {
                const p = document.createElement('p');
                p.innerHTML = `<span class="item-label">${k.replace(/_/g,' ').toUpperCase()}:</span> ${obj[k]}`;
                li.appendChild(p);
            }
            return li;
        };

        if (Array.isArray(dados)) dados.forEach(d => listaResultados.appendChild(criarItem(d)));
        else listaResultados.appendChild(criarItem(dados));
    }

    // =================================================================
    // 4. GERENCIAMENTO DINÂMICO
    // =================================================================
    
    const schemas = {
        acervo: {
            label: "Acervo",
            cols: [
                { id: 'posicao_ranking', label: 'Ranking (#)' },
                { id: 'titulo', label: 'Título' },
                { id: 'autor', label: 'Autor' },
                { id: 'genero', label: 'Gênero' }, 
                { id: 'ano_publicacao', label: 'Ano' },
                // { id: 'status', label: 'Status' },
                { id: 'total_emprestimos', label: 'Total Empréstimos' }
            ]
        },
        usuarios: {
            label: "Usuários",
            cols: [
                // --- NOVA COLUNA: Ranking ---
                { id: 'ranking_emprestimos', label: 'Ranking (#)' },
                { id: 'nome', label: 'Nome' },
                { id: 'cpf', label: 'CPF' },
                { id: 'email', label: 'Email' },
                { id: 'total_emprestimos', label: 'Total Empréstimos' },
                { id: 'taxa_pontualidade', label: 'Pontualidade (%)' }
            ]
        },
        infraestrutura: {
            label: "Infraestrutura",
            cols: [
                { id: 'ranking_reservas', label: 'Ranking Uso (#)' },
                { id: 'local', label: 'Local' },
                { id: 'tipo', label: 'Tipo' },
                { id: 'capacidade', label: 'Capacidade' },
                { id: 'total_reservas', label: 'Total Reservas' },
                { id: 'total_eventos', label: 'Total Eventos' }
            ]
        },
        emprestimos: {
            label: "Empréstimos",
            cols: [
                { id: 'cpf_usuario', label: 'CPF Usuário' },
                { id: 'data_emprestimo', label: 'Data Empréstimo' },
                { id: 'data_devolucao_prevista', label: 'Devolução Prevista' }
            ]
        }
    };

    let currentTable = 'acervo';
    let activeFilters = [];
    let visibleCols = schemas['acervo'].cols.map(c => c.id);

    // Elementos DOM
    const btnAddFiltro = document.getElementById('btn-add-filtro');
    const modalFiltro = document.getElementById('modal-filtro');
    const btnAplicarFiltro = document.getElementById('btn-aplicar-filtro');
    const btnCancelarFiltro = document.getElementById('btn-cancelar-filtro');
    const btnColunas = document.getElementById('btn-colunas');
    const modalColunas = document.getElementById('modal-colunas');
    const btnFecharColunas = document.getElementById('btn-fechar-colunas');
    
    const tbody = document.getElementById('corpo-tabela');
    const thead = document.getElementById('linha-cabecalho');
    const filtersArea = document.getElementById('area-filtros-ativos');
    const tableTitle = document.getElementById('titulo-tabela-dinamica');
    const recordCount = document.getElementById('contador-registros');

    // Inicialização
    if(document.getElementById('secao-gerenciamento')) {
        setupTableControls();
        refreshTable();
    }

    function setupTableControls() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                currentTable = btn.dataset.tabela;
                activeFilters = [];
                visibleCols = schemas[currentTable] ? schemas[currentTable].cols.map(c => c.id) : [];
                refreshTable();
            });
        });

        if(btnAddFiltro) btnAddFiltro.addEventListener('click', openFilterModal);
        if(btnCancelarFiltro) btnCancelarFiltro.addEventListener('click', () => modalFiltro.classList.add('oculto'));
        if(btnAplicarFiltro) btnAplicarFiltro.addEventListener('click', applyFilter);
        
        if(btnColunas) btnColunas.addEventListener('click', openColsModal);
        if(btnFecharColunas) btnFecharColunas.addEventListener('click', () => {
            modalColunas.classList.add('oculto');
            refreshTable();
        });
    }

    function refreshTable() {
        if(!schemas[currentTable]) return;
        if(tableTitle) tableTitle.textContent = schemas[currentTable].label;
        renderHeader();
        renderFilters();
        fetchDynamicData();
    }

    function renderHeader() {
        if(!thead) return;
        thead.innerHTML = '';
        schemas[currentTable].cols.forEach(col => {
            if(visibleCols.includes(col.id)) {
                const th = document.createElement('th');
                th.textContent = col.label;
                thead.appendChild(th);
            }
        });
    }

    function renderFilters() {
        if(!filtersArea) return;
        filtersArea.innerHTML = '';
        const opMap = {'eq':'=', 'contains':'contém', 'gt':'>', 'lt':'<', 'gte':'>=', 'lte':'<=', 'neq':'!='};
        activeFilters.forEach((f, idx) => {
            const chip = document.createElement('div');
            chip.className = 'chip-filtro';
            const colLabel = schemas[currentTable].cols.find(c => c.id === f.campo)?.label || f.campo;
            chip.innerHTML = `<span>${colLabel} <strong>${opMap[f.operador]}</strong> "${f.valor}"</span> <i class="fa-solid fa-xmark"></i>`;
            chip.querySelector('i').addEventListener('click', () => {
                activeFilters.splice(idx, 1);
                refreshTable();
            });
            filtersArea.appendChild(chip);
        });
    }

    function fetchDynamicData() {
        if(!tbody) return;
        tbody.innerHTML = '<tr><td colspan="100%">Carregando...</td></tr>';
        const payload = {
            tabela: currentTable,
            filtros: activeFilters,
            colunas: visibleCols
        };
        fetch('http://127.0.0.1:8000/analise/gerenciamento/consulta', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(r => r.json())
        .then(data => {
            if(data.erro) tbody.innerHTML = `<tr><td colspan="100%" style="color:red">Erro: ${data.erro}</td></tr>`;
            else renderRows(data);
        })
        .catch(e => {
            console.error(e);
            tbody.innerHTML = '<tr><td colspan="100%" style="color:red">Erro backend.</td></tr>';
        });
    }

    function renderRows(data) {
        tbody.innerHTML = '';
        if(recordCount) recordCount.textContent = data.length || 0;
        if (!data || data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="100%">Nenhum registro encontrado.</td></tr>';
            return;
        }
        data.forEach(row => {
            const tr = document.createElement('tr');
            schemas[currentTable].cols.forEach(col => {
                if(visibleCols.includes(col.id)) {
                    const td = document.createElement('td');
                    let val = row[col.id]; 
                    if (val === undefined) val = '-';
                    td.textContent = val;
                    tr.appendChild(td);
                }
            });
            tbody.appendChild(tr);
        });
    }

    function openFilterModal() {
        const sel = document.getElementById('select-campo');
        sel.innerHTML = '';
        schemas[currentTable].cols.forEach(col => {
            const opt = document.createElement('option');
            opt.value = col.id;
            opt.textContent = col.label;
            sel.appendChild(opt);
        });
        document.getElementById('input-valor').value = '';
        modalFiltro.classList.remove('oculto');
    }

    function applyFilter() {
        const campo = document.getElementById('select-campo').value;
        const operador = document.getElementById('select-operador').value;
        const valor = document.getElementById('input-valor').value;
        if(valor.trim() !== '') {
            activeFilters.push({ campo, operador, valor });
            modalFiltro.classList.add('oculto');
            refreshTable();
        }
    }

    function openColsModal() {
        const list = document.getElementById('lista-checkbox-colunas');
        list.innerHTML = '';
        schemas[currentTable].cols.forEach(col => {
            const lbl = document.createElement('label');
            lbl.className = 'checkbox-label';
            const chk = document.createElement('input');
            chk.type = 'checkbox';
            chk.value = col.id;
            chk.checked = visibleCols.includes(col.id);
            chk.addEventListener('change', (e) => {
                if(e.target.checked) { if(!visibleCols.includes(col.id)) visibleCols.push(col.id); } 
                else { visibleCols = visibleCols.filter(v => v !== col.id); }
            });
            lbl.appendChild(chk);
            lbl.appendChild(document.createTextNode(col.label));
            list.appendChild(lbl);
        });
        modalColunas.classList.remove('oculto');
    }
});