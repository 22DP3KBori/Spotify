console.log("STORE.JS VERSION 5 — ACTIVE");

// ----------------------
// BUY FRAME
// ----------------------
function buyFrame(id) {
    console.log("Buying frame:", id);

    fetch(`/store/buy-frame/${id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
    })
    .then(async r => {
        const data = await r.json().catch(() => ({}));
        console.log("Frame buy response:", data, "Status:", r.status);

        if (r.ok && data.success) {
            location.reload();
        } else {
            alert(data.detail || "Error");
        }
    })
    .catch(err => console.error("Buy frame error:", err));
}


// ----------------------
// BUY BADGE
// ----------------------
function buyBadge(id) {
    console.log("Buying badge:", id);

    fetch(`/store/buy-badge/${id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
    })
    .then(async r => {
        const data = await r.json().catch(() => ({}));
        console.log("Badge buy response:", data, "Status:", r.status);

        if (r.ok && data.success) {
            location.reload();
        } else {
            alert(data.detail || "Error");
        }
    })
    .catch(err => console.error("Buy badge error:", err));
}


// ----------------------
// TAB SYSTEM
// ----------------------
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {

        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));

        btn.classList.add('active');
        document.getElementById(`tab-${btn.dataset.tab}`).classList.add('active');
    });
});

