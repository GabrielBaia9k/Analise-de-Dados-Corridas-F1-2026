(() => {
    "use strict";

    // ============================================================================
    // PASSO 1 - Configuração
    // ----------------------------------------------------------------------------
    // Índices do customdata usados na decoração do hover:
    //   customdata[0] -> pontos
    //   customdata[1] -> equipe
    //   customdata[2] -> logo do time
    //   customdata[3] -> bandeira do país da corrida
    // ============================================================================
    const SVG_NS = "http://www.w3.org/2000/svg";
    const XLINK_NS = "http://www.w3.org/1999/xlink";
    const BOUND_ATTRIBUTE = "data-hover-logos-bound";
    const LOGO_CLASS = "team-hover-logo";
    const FLAG_CLASS = "flag-hover-flag";
    const LABEL_X_ATTRIBUTE = "data-hover-logo-original-x";
    const LOGO_CUSTOMDATA_INDEX = 2;
    const FLAG_CUSTOMDATA_INDEX = 3;
    const LOGO_WIDTH = 24;
    const LOGO_HEIGHT = 24;
    const FLAG_WIDTH = 24;
    const FLAG_HEIGHT = 16;
    // Compensa o deslocamento aplicado pelo CSS em text.legendtitletext
    // (transform: translateX(38px)), que reserva espaço para a bandeira.
    const FLAG_TITLE_OFFSET_X = 38;
    const LOGO_META = new Set([
        "pilotos-hover",
        "construtores-hover",
    ]);

    // ============================================================================
    // PASSO 2 - Filtro dos pontos
    // ----------------------------------------------------------------------------
    // Seleciona apenas os pontos dos traces que carregam os dados de decoração
    // (logos de times e bandeiras), identificados pelo meta de cada trace.
    // ============================================================================
    function getLogoPoints(eventData) {
        return (eventData?.points || []).filter((point) => {
            return LOGO_META.has(point?.data?.meta);
        });
    }

    // ============================================================================
    // PASSO 3 - Limpeza do hover
    // ----------------------------------------------------------------------------
    // Remove os elementos decorativos (logos de times E bandeiras) e restaura a
    // posição original dos textos da legenda quando o hover termina (unhover).
    // ============================================================================
    function cleanupHover(graph) {
        graph
            .querySelectorAll(`.${LOGO_CLASS}, .${FLAG_CLASS}`)
            .forEach((image) => image.remove());

        graph
            .querySelectorAll(
                ".hoverlayer .legend .traces text.legendtext"
            )
            .forEach((label) => {
                const originalX = label.getAttribute(LABEL_X_ATTRIBUTE);

                if (originalX !== null) {
                    label.setAttribute("x", originalX);
                    label.removeAttribute(LABEL_X_ATTRIBUTE);
                }
            });
    }

    // ============================================================================
    // PASSO 4 - Resolução da URL da imagem
    // ----------------------------------------------------------------------------
    // Converte o caminho relativo (ex.: "Country Flags/au.svg") em uma URL
    // absoluta com base na página atual, para o SVG conseguir carregar a imagem.
    // ============================================================================
    function resolveLogoUrl(logoPath) {
        if (!logoPath) {
            return "";
        }

        try {
            return new URL(logoPath, document.baseURI).href;
        } catch (_error) {
            return logoPath;
        }
    }

    // ============================================================================
    // PASSO 5 - Criação dos elementos de imagem
    // ----------------------------------------------------------------------------
    // Cria um <image> SVG posicionado à esquerda de um texto de referência.
    // A largura define a coluna vertical (borda esquerda em labelX - width - 6),
    // então bandeira e logos com a mesma largura ficam alinhados.
    // ============================================================================
    function createImageElement(label, imagePath, width, height, className, xOffset = 0) {
        const image = document.createElementNS(SVG_NS, "image");
        const labelX = Number(label.getAttribute("x") || 0);
        const labelY = Number(label.getAttribute("y") || 0);

        image.classList.add(className);
        image.setAttribute("width", String(width));
        image.setAttribute("height", String(height));
        image.setAttribute("x", String(labelX + xOffset - width - 6));
        image.setAttribute("y", String(labelY - height + 9));
        image.setAttribute("preserveAspectRatio", "xMidYMid meet");
        image.setAttribute("href", resolveLogoUrl(imagePath));
        image.setAttributeNS(
            XLINK_NS,
            "xlink:href",
            resolveLogoUrl(imagePath)
        );

        return image;
    }

    // Cria o logo do time (24x24), reutilizando a função genérica acima.
    function createLogoElement(label, logoPath) {
        return createImageElement(
            label,
            logoPath,
            LOGO_WIDTH,
            LOGO_HEIGHT,
            LOGO_CLASS
        );
    }

    // Cria a bandeira do país (24x16), reutilizando a função genérica acima.
    // O xOffset posiciona a bandeira no espaço reservado pelo título do GP.
    function createFlagElement(label, flagPath) {
        return createImageElement(
            label,
            flagPath,
            FLAG_WIDTH,
            FLAG_HEIGHT,
            FLAG_CLASS,
            FLAG_TITLE_OFFSET_X
        );
    }

    // ============================================================================
    // PASSO 6 - Decoração do hover
    // ----------------------------------------------------------------------------
    // 1. Extrai o logo de cada time (customdata[2]) e a bandeira da corrida
    //    (customdata[3]) dos pontos do evento.
    // 2. Insere a bandeira à esquerda do título do GP no hover unificado.
    // 3. Insere o logo de cada time à esquerda da respectiva linha da legenda.
    // ============================================================================
    function decorateHover(graph, points) {
        cleanupHover(graph);

        const logosByPilot = new Map();
        let flagPath = "";

        points.forEach((point) => {
            const entity = point.data?.name;
            const customdata = point.customdata || [];

            if (entity && customdata[LOGO_CUSTOMDATA_INDEX]) {
                logosByPilot.set(entity, customdata[LOGO_CUSTOMDATA_INDEX]);
            }

            // Todos os pilotos/equipes do mesmo GP compartilham a mesma bandeira,
            // portanto basta capturar o primeiro caminho não vazio encontrado.
            if (!flagPath && customdata[FLAG_CUSTOMDATA_INDEX]) {
                flagPath = customdata[FLAG_CUSTOMDATA_INDEX];
            }
        });

        // Título do GP no box unificado. A bandeira é tratada como característica
        // do título: só é inserida quando o título existe.
        const titleText = graph.querySelector(
            ".hoverlayer .legend text.legendtitletext"
        );

        if (titleText && flagPath && titleText.parentNode) {
            titleText.parentNode.insertBefore(
                createFlagElement(titleText, flagPath),
                titleText
            );
        }

        if (!logosByPilot.size) {
            return;
        }

        // Insere o logo de cada time à esquerda do texto da sua linha na legenda.
        const rows = graph.querySelectorAll(
            ".hoverlayer .legend .traces"
        );

        rows.forEach((row) => {
            const label = row.querySelector("text.legendtext");

            if (!label) {
                return;
            }

            const entity = [...logosByPilot.keys()].find((name) => {
                return label.textContent.includes(name);
            });
            const logoPath = entity ? logosByPilot.get(entity) : "";

            if (!logoPath) {
                return;
            }

            if (!label.hasAttribute(LABEL_X_ATTRIBUTE)) {
                label.setAttribute(
                    LABEL_X_ATTRIBUTE,
                    label.getAttribute("x") || "0"
                );
            }

            row.insertBefore(createLogoElement(label, logoPath), row.firstChild);
        });
    }

    // ============================================================================
    // PASSO 7 - Vínculo dos eventos do Plotly
    // ----------------------------------------------------------------------------
    // Liga os handlers de hover/unhover em cada gráfico Plotly, garantindo que a
    // decoração seja aplicada a cada novo hover e removida ao sair dele.
    // ============================================================================
    function bindPlotlyGraph(graph) {
        if (graph.getAttribute(BOUND_ATTRIBUTE) === "true") {
            return;
        }

        if (typeof graph.on !== "function") {
            return;
        }

        graph.setAttribute(BOUND_ATTRIBUTE, "true");

        graph.on("plotly_hover", (eventData) => {
            const points = getLogoPoints(eventData);

            if (!points.length) {
                cleanupHover(graph);
                return;
            }

            window.requestAnimationFrame(() => {
                decorateHover(graph, points);
            });
        });

        graph.on("plotly_unhover", () => {
            cleanupHover(graph);
        });
    }

    // ============================================================================
    // PASSO 8 - Inicialização
    // ----------------------------------------------------------------------------
    // Vincula os handlers aos gráficos já presentes e observa a DOM para vincular
    // automaticamente qualquer novo gráfico adicionado depois.
    // ============================================================================
    function bindPlotlyGraphs() {
        document
            .querySelectorAll(".js-plotly-plot")
            .forEach(bindPlotlyGraph);
    }

    const observer = new MutationObserver(bindPlotlyGraphs);

    function initialize() {
        bindPlotlyGraphs();
        observer.observe(document.body, {
            childList: true,
            subtree: true,
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initialize, {
            once: true,
        });
    } else {
        initialize();
    }
})();
