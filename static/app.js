let mediaRecorder;
let audioChunks = [];
let currentLanguage = "hi";
let currentSubmissionId = null;
let currentFormData = {};

document.querySelectorAll(".lang-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".lang-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        currentLanguage = btn.dataset.lang;
    });
});

const recordBtn = document.getElementById("recordBtn");
const recordStatus = document.getElementById("recordStatus");

recordBtn.addEventListener("click", async () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        return;
    }
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
        mediaRecorder.onstop = async () => {
            const blob = new Blob(audioChunks, { type: "audio/wav" });
            await sendAudio(blob);
        };
        mediaRecorder.start();
        recordBtn.classList.add("recording");
        recordStatus.textContent = "🔴 Recording... Tap again to stop";
    } catch (err) {
        alert("Microphone access denied: " + err.message);
    }
});

document.getElementById("uploadBtn").addEventListener("click", async () => {
    const file = document.getElementById("audioFile").files[0];
    if (!file) return alert("Please select an audio file first.");
    await sendAudio(file);
});

async function sendAudio(blob) {
    recordStatus.textContent = "⏳ Processing...";
    recordBtn.classList.remove("recording");
    const formData = new FormData();
    formData.append("audio", blob, "recording.wav");
    formData.append("language", currentLanguage);
    try {
        const res = await fetch("/api/transcribe", { method: "POST", body: formData });
        const data = await res.json();
        if (!data.success) {
            recordStatus.textContent = "❌ " + (data.error || "Failed");
            return;
        }
        currentSubmissionId = data.submission_id;
        currentFormData = data.mapped.form;
        renderForm(data);
        recordStatus.textContent = "✅ Done! Review the form below.";
    } catch (err) {
        recordStatus.textContent = "❌ Error: " + err.message;
    }
}

function renderForm(data) {
    const formSection = document.getElementById("formSection");
    const fieldsDiv = document.getElementById("formFields");
    const debugSection = document.getElementById("debugSection");
    const debugOutput = document.getElementById("debugOutput");

    fieldsDiv.innerHTML = "";
    const form = data.mapped.form;
    for (const [fieldId, field] of Object.entries(form)) {
        const div = document.createElement("div");
        div.className = "form-field" + (field.needs_review ? " needs-review" : "");
        div.innerHTML = `
            <label>${field.label} ${field.required ? "*" : ""}
                <span class="conf-badge ${field.confidence > 0.75 ? 'high' : field.confidence > 0.5 ? 'mid' : 'low'}">
                    ${(field.confidence * 100).toFixed(0)}%
                </span>
            </label>
            <input type="text" data-field="${fieldId}" value="${field.value || ''}"
                   placeholder="Not detected — please fill manually">
            ${field.needs_review ? '<p class="review-hint">⚠️ Low confidence — please verify</p>' : ''}
        `;
        fieldsDiv.appendChild(div);
    }
    const conf = data.mapped.overall_confidence;
    document.getElementById("confidenceFill").style.width = (conf * 100) + "%";
    document.getElementById("confidenceText").textContent =
        `Overall Confidence: ${(conf * 100).toFixed(0)}% | Completion: ${(data.mapped.completion * 100).toFixed(0)}%`;

    debugOutput.textContent = JSON.stringify({
        transcription: data.asr,
        extracted: data.extracted,
    }, null, 2);

    formSection.style.display = "block";
    debugSection.style.display = "block";
    formSection.scrollIntoView({ behavior: "smooth" });
}

document.getElementById("submitBtn").addEventListener("click", async () => {
    const inputs = document.querySelectorAll("#formFields input");
    for (const input of inputs) {
        const fieldId = input.dataset.field;
        const original = currentFormData[fieldId]?.value || "";
        const corrected = input.value;
        if (corrected !== original) {
            await fetch("/api/correct", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    submission_id: currentSubmissionId,
                    field_id: fieldId,
                    original_value: original,
                    corrected_value: corrected,
                }),
            });
        }
    }
    alert("✅ Form submitted! Corrections saved for improving accuracy.");
});

document.getElementById("resetBtn").addEventListener("click", () => {
    document.getElementById("formSection").style.display = "none";
    document.getElementById("debugSection").style.display = "none";
    recordStatus.textContent = "Tap to start recording";
    window.scrollTo({ top: 0, behavior: "smooth" });
});