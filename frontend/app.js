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

let segmentsCache = [];
let currentJobId = null;

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
        });

        transcriptList.appendChild(item);
    });
    }

    uploadBtn.addEventListener("click", async () => {
    const file = fileInput.files[0];

    if (!file) {
        statusText.textContent = "Selecione um arquivo primeiro.";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("enable_diarization", diarizationCheck.checked);

    statusText.textContent = "Enviando e transcrevendo...";
    uploadBtn.disabled = true;
    downloadButtons.style.display = "none";

    try {
        const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
        throw new Error(data.detail || "Erro ao processar arquivo.");
        }

        currentJobId = data.job_id;
        videoPlayer.src = data.video_url;
        segmentsCache = data.segments || [];
        renderSegments(segmentsCache);

        downloadButtons.style.display = "flex";
        statusText.textContent = `Transcrição concluída. ${segmentsCache.length} trechos carregados.`;
    } catch (error) {
        statusText.textContent = `Erro: ${error.message}`;
        transcriptList.innerHTML = `<div class="empty-state">Falha ao carregar transcrição.</div>`;
    } finally {
        uploadBtn.disabled = false;
    }
});

// Botões de download
downloadTxt.addEventListener("click", () => {
    if (currentJobId) {
        window.location.href = `/api/download/${currentJobId}/txt`;
    }
});

downloadJson.addEventListener("click", () => {
    if (currentJobId) {
        window.location.href = `/api/download/${currentJobId}/json`;
    }
});

downloadSrt.addEventListener("click", () => {
    if (currentJobId) {
        window.location.href = `/api/download/${currentJobId}/srt`;
    }
});

searchInput.addEventListener("input", (event) => {
    renderSegments(segmentsCache, event.target.value);
});