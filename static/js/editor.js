async function ativarEdicao(id, campo) {
    const p = document.querySelector(`#${campo}-${id}`);
    if (!p) return;

    const textoOriginal = p.textContent;
    const areaTexto = document.createElement('textarea');
    
    areaTexto.className = "edit-area w-full bg-gray-800 text-gray-200 border border-emerald-500 rounded p-2 focus:outline-none ring-2 ring-emerald-900";
    areaTexto.value = textoOriginal;
    areaTexto.rows = 5;

    p.replaceWith(areaTexto);
    areaTexto.focus();

    // Função para salvar
    const salvar = async () => {
        const novoTexto = areaTexto.value;
        let formData = new FormData();
        formData.append(campo, novoTexto);

        const response = await fetch(`/atualizar_parcial/${id}`, { method: 'POST', body: formData });
        if (response.ok) {
            const novoDiv = document.createElement('div');
            novoDiv.id = `${campo}-${id}`;
            novoDiv.className = "text-sm text-gray-300 solution-content edit-area";
            novoDiv.innerHTML = marked.parse(novoTexto);
            areaTexto.replaceWith(novoDiv);
        }
    };
    areaTexto.onkeydown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            salvar();
        }
        if (e.key === "Escape") {
            location.reload(); // Cancela
        }
    };

    areaTexto.onblur = salvar;
}