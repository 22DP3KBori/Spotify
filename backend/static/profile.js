async function equipFrame(frameId) {
  try {
    const response = await fetch(`/frames/equip/${frameId}`, {
      method: "POST",
    });

    const data = await response.json();
    if (response.ok) {
      alert("✅ " + data.message);
      location.reload(); // перезагружаем, чтобы показать новую рамку
    } else {
      alert("❌ " + data.detail || "Error equipping frame");
    }
  } catch (error) {
    alert("⚠️ Something went wrong");
    console.error(error);
  }
}
