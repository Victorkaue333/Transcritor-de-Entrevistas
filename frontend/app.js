const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const statusText = document.getElementById("statusText");
const videoPlayer = document.getElementById("videoPlayer");
const transcriptList = document.getElementById("transcriptList");
const searchInput = document.getElementById("searchInput");
const diarizationCheck = document.getElementById("diarizationCheck");
const downloadButtons = document.getElementById("downloadButtons");
const downloadTxt = document.getElementById("downloadTxt");
const downloadJson = document.getElementById("downloadJson");
const downloadSrt = document.getElementById("downloadSrt");
const logsPanel = document.getElementById("logsPanel");
const logsList = document.getElementById("logsList");
const clearLogsBtn = document.getElementById("clearLogsBtn");

let segmentsCache = [];
let currentJobId = null;
let lastActiveSegment = null;

// Funções de persistência
function saveToLocalStorage() {
    if (currentJobId && segmentsCache.length > 0) {
        const data = {
            jobId: currentJobId,
            segments: segmentsCache,
            videoUrl: videoPlayer.src
        };
        localStorage.setItem('whisper_transcription', JSON.stringify(data));
        addLog("info", "Dados salvos automaticamente");
    }
}

function loadFromLocalStorage() {
    const saved = localStorage.getItem('whisper_transcription');
    if (saved) {
        try {
            const data = JSON.parse(saved);
            currentJobId = data.jobId;
            segmentsCache = data.segments || [];
            
            if (data.videoUrl) {
                videoPlayer.src = data.videoUrl;
                renderSegments(segmentsCache);
                downloadButtons.style.display = "flex";
                statusText.textContent = `Transcrição carregada. ${segmentsCache.length} trechos disponíveis.`;
                addLog("success", `Transcrição anterior restaurada (${segmentsCache.length} segmentos)`);
            }
        } catch (error) {
            console.error("Erro ao carregar dados salvos:", error);
            localStorage.removeItem('whisper_transcription');
        }
    }
}

// Sistema de Logs
function addLog(level, message) {
    const now = new Date();
    const time = now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    
    const logEntry = document.createElement("div");
    logEntry.className = "log-entry";
    
    logEntry.innerHTML = `
        <span class="log-time">${time}</span>
        <span class="log-level ${level}">[${level.toUpperCase()}]</span>
        <span class="log-message">${message}</span>
    `;
    
    logsList.appendChild(logEntry);
    logsList.scrollTop = logsList.scrollHeight;
    
    // Mostra o painel se estiver oculto
    if (logsPanel.style.display === "none") {
        logsPanel.style.display = "block";
    }
}

clearLogsBtn.addEventListener("click", () => {
    logsList.innerHTML = "";
    addLog("info", "Logs limpos");
});

function formatTime(seconds) {
    const total = Math.floor(seconds);
    const hrs = Math.floor(total / 3600);
    const mins = Math.floor((total % 3600) / 60);
    const secs = total % 60;

    if (hrs > 0) {
        return `${String(hrs).padStart(2, "0")}:${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
    }

    return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
    }

    function renderSegments(segments, filter = "") {
    transcriptList.innerHTML = "";

    const filtered = segments.filter((segment) =>
        segment.text.toLowerCase().includes(filter.toLowerCase())
    );

    if (!filtered.length) {
        transcriptList.innerHTML = `<div class="empty-state">Nenhum trecho encontrado.</div>`;
        return;
    }

    filtered.forEach((segment, index) => {
        const item = document.createElement("div");
        item.className = "segment";
        item.dataset.start = segment.start;
        item.dataset.end = segment.end;
        item.dataset.index = index;

        item.innerHTML = `
        <div class="segment-header">
            <span class="timestamp">[${formatTime(segment.start)} - ${formatTime(segment.end)}]</span>
            <span class="speaker">${segment.speaker || "Desconhecido"}</span>
        </div>
        <div class="segment-text">${segment.text}</div>
        `;

        item.addEventListener("click", () => {
        videoPlayer.currentTime = Number(segment.start);
        videoPlayer.play();

        document.querySelectorAll(".segment").forEach((el) => el.classList.remove("active"));
        item.classList.add("active");
        lastActiveSegment = item;
        });

        transcriptList.appendChild(item);
    });
    
    // Reset do último segmento ativo ao re-renderizar
    lastActiveSegment = null;
    }

    uploadBtn.addEventListener("click", async () => {
    const file = fileInput.files[0];

    if (!file) {
        statusText.textContent = "Selecione um arquivo primeiro.";
        addLog("warning", "Nenhum arquivo selecionado");
        return;
    }

    addLog("info", `Arquivo selecionado: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("enable_diarization", diarizationCheck.checked);

    if (diarizationCheck.checked) {
        addLog("info", "Identificação de speakers habilitada");
    }

    statusText.textContent = "Enviando arquivo...";
    addLog("info", "Enviando arquivo para o servidor...");
    uploadBtn.disabled = true;
    downloadButtons.style.display = "none";

    try {
        addLog("info", "Aguardando processamento (isso pode demorar alguns minutos)...");
        
        const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
        throw new Error(data.detail || "Erro ao processar arquivo.");
        }

        addLog("success", `Transcrição concluída! Job ID: ${data.job_id}`);
        addLog("success", `${data.segments.length} segmentos gerados`);

        currentJobId = data.job_id;
        videoPlayer.src = data.video_url;
        segmentsCache = data.segments || [];
        renderSegments(segmentsCache);

        downloadButtons.style.display = "flex";
        statusText.textContent = `Transcrição concluída. ${segmentsCache.length} trechos carregados.`;
        addLog("info", "Arquivos de download prontos (TXT, JSON, SRT)");
        
        // Salva os dados no localStorage
        saveToLocalStorage();
    } catch (error) {
        statusText.textContent = `Erro: ${error.message}`;
        transcriptList.innerHTML = `<div class="empty-state">Falha ao carregar transcrição.</div>`;
        addLog("error", `Erro ao processar: ${error.message}`);
    } finally {
        uploadBtn.disabled = false;
    }
});

// Botões de download
downloadTxt.addEventListener("click", () => {
    if (currentJobId) {
        addLog("info", "Baixando arquivo TXT...");
        window.location.href = `/api/download/${currentJobId}/txt`;
    }
});

downloadJson.addEventListener("click", () => {
    if (currentJobId) {
        addLog("info", "Baixando arquivo JSON...");
        window.location.href = `/api/download/${currentJobId}/json`;
    }
});

downloadSrt.addEventListener("click", () => {
    if (currentJobId) {
        addLog("info", "Baixando arquivo SRT...");
        window.location.href = `/api/download/${currentJobId}/srt`;
    }
});

searchInput.addEventListener("input", (event) => {
    renderSegments(segmentsCache, event.target.value);
});

// Sincronização automática do vídeo com os segmentos
videoPlayer.addEventListener("timeupdate", () => {
    const currentTime = videoPlayer.currentTime;
    
    // Encontra o segmento ativo baseado no tempo atual
    const allSegments = document.querySelectorAll(".segment");
    let activeSegment = null;
    
    for (const segment of allSegments) {
        const start = parseFloat(segment.dataset.start);
        const end = parseFloat(segment.dataset.end);
        
        if (currentTime >= start && currentTime <= end) {
            activeSegment = segment;
            break;
        }
    }
    
    // Só atualiza se mudou o segmento ativo
    if (activeSegment !== lastActiveSegment) {
        // Remove a classe active de todos os segmentos
        document.querySelectorAll(".segment").forEach((el) => el.classList.remove("active"));
        
        if (activeSegment) {
            activeSegment.classList.add("active");
            
            // Scroll automático para o segmento ativo (com offset para centralizar)
            const transcriptContainer = transcriptList;
            const segmentTop = activeSegment.offsetTop;
            const containerHeight = transcriptContainer.clientHeight;
            const segmentHeight = activeSegment.clientHeight;
            
            // Centraliza o segmento na tela
            transcriptContainer.scrollTo({
                top: segmentTop - (containerHeight / 2) + (segmentHeight / 2),
                behavior: "smooth"
            });
        }
        
        lastActiveSegment = activeSegment;
    }
});

// Inicialização: carrega dados salvos (se existirem)
loadFromLocalStorage();

// Log inicial
if (!currentJobId) {
    addLog("info", "Sistema iniciado. Aguardando upload de arquivo...");
}