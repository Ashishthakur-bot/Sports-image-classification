const dropArea = document.getElementById("drop-area");
const fileElem = document.getElementById("fileElem");
const preview = document.getElementById("preview");
const result = document.getElementById("result");

// Prevent default drag behavior
["dragenter", "dragover", "dragleave", "drop"].forEach(eventName => {
    dropArea.addEventListener(eventName, e => e.preventDefault());
});

// Highlight effect
dropArea.addEventListener("dragover", () => {
    dropArea.style.background = "#ddd";
});

dropArea.addEventListener("dragleave", () => {
    dropArea.style.background = "white";
});

// Drop event
dropArea.addEventListener("drop", e => {
    const file = e.dataTransfer.files[0];
    handleFile(file);
});

// File select
fileElem.addEventListener("change", () => {
    handleFile(fileElem.files[0]);
});

function handleFile(file) {
    if (!file) return;

    // Preview image
    preview.src = URL.createObjectURL(file);
    preview.style.display = "block";   // 👈 ADD THIS LINE HERE

    // Send to backend
    let formData = new FormData();
    formData.append("file", file);

fetch("http://127.0.0.1:5000/predict", {
    method: "POST",
    body: formData
})
.then(res => res.json())   // ✅ THIS LINE IS MISSING
.then(data => {
    console.log(data);

    if (data.error) {
        result.innerText = "Error: " + data.error;
        return;
    }

    result.innerText = `Prediction: ${data.prediction}`;

    const barsDiv = document.getElementById("bars");
    barsDiv.innerHTML = "";

    // Use top3 from backend
    data.top3.forEach(item => {

        let bar = document.createElement("div");
        bar.className = "bar";

        bar.innerHTML = `
            <span>${item.class} (${item.confidence}%)</span>
            <div class="progress">
                <div class="progress-fill"></div>
            </div>
        `;

        barsDiv.appendChild(bar);

        // 🔥 Animate width
        setTimeout(() => {
            bar.querySelector(".progress-fill").style.width = item.confidence + "%";
        }, 100);
    });
})
}