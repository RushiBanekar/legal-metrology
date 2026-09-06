const API_BASE = "http://localhost:8000/api/v1";

// State
let currentSessionId = localStorage.getItem("lm_current_session_id") || null;
let mediaStream = null;

// Initialize Camera
async function initCamera(videoElementId) {
  const video = document.getElementById(videoElementId);
  if (!video) return;

  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "environment", width: { ideal: 1920 }, height: { ideal: 1080 } },
    });
    video.srcObject = mediaStream;
    video.play();
  } catch (err) {
    console.warn("Camera access failed or not permitted:", err);
  }
}

// Capture frame from video to Blob
async function captureVideoFrame(videoElementId) {
  const video = document.getElementById(videoElementId);
  if (!video) return null;

  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth || 640;
  canvas.height = video.videoHeight || 480;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  return new Promise((resolve) => {
    canvas.toBlob((blob) => resolve(blob), "image/jpeg", 0.95);
  });
}

// Create New Session
async function createSession(category = "packaged_food") {
  try {
    const res = await fetch(`${API_BASE}/sessions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ category, rule_version: "1.0.0", metadata: { created_via: "web_ui" } }),
    });
    if (!res.ok) throw new Error("Failed to initialize session");
    const data = await res.json();
    currentSessionId = data.session_id;
    localStorage.setItem("lm_current_session_id", currentSessionId);
    return data;
  } catch (err) {
    console.error("Session creation error:", err);
    alert("Could not create session: " + err.message);
  }
}

// Upload Panel Image
async function uploadPanel(fileBlob, panelType = "front") {
  if (!currentSessionId) {
    await createSession();
  }

  const formData = new FormData();
  formData.append("file", fileBlob, `capture_${panelType}_${Date.now()}.jpg`);
  formData.append("panel_type", panelType);

  try {
    const res = await fetch(`${API_BASE}/sessions/${currentSessionId}/upload`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Upload failed");
    return await res.json();
  } catch (err) {
    console.error("Upload error:", err);
    throw err;
  }
}

// Evaluate Current Session
async function evaluateSession() {
  if (!currentSessionId) return null;

  try {
    const res = await fetch(`${API_BASE}/sessions/${currentSessionId}/evaluate`, {
      method: "POST",
    });
    if (!res.ok) throw new Error("Evaluation failed");
    return await res.json();
  } catch (err) {
    console.error("Evaluation error:", err);
    throw err;
  }
}

// Fetch Session Details
async function fetchSession(sessionId) {
  try {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}`);
    if (!res.ok) throw new Error("Session fetch failed");
    return await res.json();
  } catch (err) {
    console.error("Fetch session error:", err);
    return null;
  }
}

// Fetch All Sessions
async function fetchAllSessions() {
  try {
    const res = await fetch(`${API_BASE}/sessions`);
    if (!res.ok) throw new Error("Failed to fetch sessions");
    return await res.json();
  } catch (err) {
    console.error("Fetch sessions error:", err);
    return [];
  }
}
