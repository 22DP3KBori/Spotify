function buyFrame(frameId) {
    fetch(`/frames/buy/${frameId}`, { method: "POST" })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert(`You bought ${data.frame}! Coins left: ${data.coins_left}`);
                location.reload();
            } else {
                alert(data.detail || "Error buying frame");
            }
        });
}


// Tabs
document.querySelectorAll(".store-tabs button").forEach(btn=>{
    btn.onclick = () => {
        document.querySelector(".store-tabs .active").classList.remove("active");
        btn.classList.add("active");

        document.querySelectorAll("[id^='tab-']").forEach(t=>t.classList.add("hidden"));
        document.getElementById(`tab-${btn.dataset.tab}`).classList.remove("hidden");
    }
})

// Tab buttons
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(`tab-${btn.dataset.tab}`).classList.add('active');
  });
});



// Equip frame
function equipFrame(frameId) {
  fetch(`/frames/equip/${frameId}`, {
    method: "POST",
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      alert("✅ Frame equipped!");
      location.reload();
    } else {
      alert("Something went wrong!");
    }
  })
  .catch(err => console.error(err));
}


