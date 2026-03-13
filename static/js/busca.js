const inputBusca = document.querySelector('input[name="busca"]');
const listaErros = document.querySelector('main');

inputBusca.addEventListener('input', async (e) => {
    const termo = e.target.value;

    // Efeito de transição: lista fica clara antes de atualizar
    listaErros.style.opacity = "0.3";
    listaErros.style.transition = "opacity 0.2s ease";

    try {
        const response = await fetch(termo === "" ? '/' : `/?busca=${termo}`);
        const html = await response.text();
        const doc = new DOMParser().parseFromString(html, 'text/html');
        
        listaErros.innerHTML = doc.querySelector('main').innerHTML;
        
        // Reinicializa o Markdown
        document.querySelectorAll('.solution-content').forEach(el => {
            el.innerHTML = marked.parse(el.textContent);
        });

        // Volta a opacidade ao normal
        listaErros.style.opacity = "1";

    } catch (err) {
        console.error("Erro na busca:", err);
        listaErros.style.opacity = "1";
    }
});