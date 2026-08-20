(() => {
    "use strict";

    // ============================================================================
    // CLIQUE NO GRÁFICO HEAD-TO-HEAD → TABELA À DIREITA
    // ----------------------------------------------------------------------------
    // OUVE o clique numa barra do gráfico H2H e atualiza a tabela de comparação.
    // O payload inclui um timestamp para garantir que Shiny SEMPRE invalide a
    // reatividade, mesmo quando se clica novamente na mesma equipe.
    // ============================================================================
    const BOUND_ATTRIBUTE = "data-h2h-click-bound";
    const EQUIPE_CUSTOMDATA_INDEX = 0;
    const RETRY_FRAME_LIMIT = 120;

    function getHiddenInput(graph) {
        const card = graph.closest(".h2h-card");
        if (!card) {
            return null;
        }
        return card.querySelector(".h2h-oculto input");
    }

    function bindPlotlyGraph(graph, frames = 0) {
        if (graph.getAttribute(BOUND_ATTRIBUTE) === "true") {
            return;
        }

        // Plotly pode ainda não ter sido inicializado no elemento recém-inserido
        // (ex.: troca de aba). Tenta novamente a cada frame até ficar pronto.
        if (typeof graph.on !== "function") {
            if (frames < RETRY_FRAME_LIMIT) {
                requestAnimationFrame(() => bindPlotlyGraph(graph, frames + 1));
            }
            return;
        }

        graph.setAttribute(BOUND_ATTRIBUTE, "true");

        graph.on("plotly_click", (eventData) => {
            const points = eventData?.points || [];
            if (!points.length) {
                return;
            }

            const customdata = points[0].customdata || [];
            const equipe = customdata[EQUIPE_CUSTOMDATA_INDEX];
            if (!equipe) {
                return;
            }

            const hiddenInput = getHiddenInput(graph);
            if (!hiddenInput) {
                return;
            }

            Shiny.setInputValue(
                hiddenInput.id,
                JSON.stringify({ equipe: equipe, t: Date.now() }),
                { priority: "event" }
            );
        });
    }

    function bindH2HGraphs() {
        document
            .querySelectorAll(
                ".h2h-card .js-plotly-plot, .h2h-card .plotly-graph-div"
            )
            .forEach(bindPlotlyGraph);
    }

    const observer = new MutationObserver(bindH2HGraphs);

    function initialize() {
        bindH2HGraphs();
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ["class"],
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initialize, { once: true });
    } else {
        initialize();
    }
})();
