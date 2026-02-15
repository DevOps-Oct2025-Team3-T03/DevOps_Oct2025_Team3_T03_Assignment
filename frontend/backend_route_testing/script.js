const API_URL_AS = "http://127.0.0.1:5000";
const API_URL_FS = "http://127.0.0.1:5001";

// ---------- LOGIN ----------
document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await fetch(`${API_URL_AS}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
    credentials: "include",
  });

  const data = await res.json();
  if (res.ok) {
    localStorage.setItem("role", data.role);
    localStorage.setItem("username", data.username);
    localStorage.setItem("user_id", data.user_id);
    if (data.role === "admin") window.location.href = "admin_dashboard.html";
    else window.location.href = "user_dashboard.html";
  } else {
    document.getElementById("msg").innerText = data.error;
  }
});

// ---------- LOGOUT ----------
document.getElementById("logoutBtn")?.addEventListener("click", async () => {
  await fetch(`${API_URL_AS}/logout`, { credentials: 'include' });
  localStorage.clear();
  window.location.href = "index.html";
});

// ---------- ADMIN DASHBOARD ----------
async function loadUsers() {
  const res = await fetch(`${API_URL_AS}/admin`, {
    credentials: "include",
  });
  const users = await res.json();
  const list = document.getElementById("usersList");
  list.innerHTML = "";
  users.forEach((u) => {
    const li = document.createElement("li");
    li.textContent = `${u.username} (${u.role})`;

    // Only allow deleting non-admin users
    if (u.role !== "admin") {
      const delBtn = document.createElement("button");
      delBtn.textContent = "Delete";
      delBtn.style.marginLeft = "10px";
      delBtn.addEventListener("click", async () => {
        if (!confirm(`Delete user "${u.username}"?`)) return;

        const res = await fetch(
          `${API_URL_AS}/admin/delete_user/${u.user_id}`,
          {
            method: "POST",
            credentials: "include",
          },
        );

        const data = await res.json();

        if (!res.ok) {
          alert(data.error || "Failed to delete user");
          return;
        }

        loadUsers(); // refresh list
      });

      li.appendChild(delBtn);
    }
    list.appendChild(li);
  });
}

document
  .getElementById("createUserForm")
  ?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("newUsername").value;
    const password = document.getElementById("newPassword").value;
    const role = document.getElementById("newRole").value;

    const res = await fetch(`${API_URL_AS}/admin/create_user`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password, role }),
      credentials: "include",
    });

    if (res.ok) {
      loadUsers();
    } else {
      alert((await res.json()).error);
    }
  });

if (document.getElementById("usersList")) {
  loadUsers();
}

document.getElementById("refreshUsersBtn")?.addEventListener("click", () => {
  loadUsers();
});

// ---------- USER DASHBOARD ----------
async function loadFiles() {
  const res = await fetch(`${API_URL_FS}/dashboard`, {
    credentials: "include",
  });
  const files = await res.json();
  const list = document.getElementById("fileList");
  list.innerHTML = "";
  files.forEach((f) => {
    const li = document.createElement("li");
    li.textContent = f.filename;

    // Download button
    const downloadBtn = document.createElement("button");
    downloadBtn.textContent = "Download";
    downloadBtn.addEventListener("click", () => {
      window.open(`${API_URL_FS}/dashboard/download/${f.file_id}`, "_blank");
    });

    const delBtn = document.createElement("button");
    delBtn.textContent = "Delete";
    delBtn.addEventListener("click", async () => {
      await fetch(`${API_URL_FS}/dashboard/delete/${f.file_id}`, {
        method: "POST",
        credentials: "include",
      });
      loadFiles();
    });
    li.appendChild(downloadBtn);
    li.appendChild(delBtn);
    list.appendChild(li);
  });
}

document.getElementById("uploadForm")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  //const fileInput = document.getElementById("fileInput");
  const files = document.getElementById("fileInput").files;
  const formData = new FormData();
  //formData.append("file", fileInput.files[0]);
  for (let i = 0; i < files.length; i++) {
    formData.append("files", files[i]); // append each file under same key
  }

  await fetch(`${API_URL_FS}/dashboard/upload`, {
    method: "POST",
    body: formData,
    credentials: "include",
  });
  fileInput.value = "";
  loadFiles();
});

if (document.getElementById("fileList")) {
  loadFiles();
}

function formatTimestamp(isoString) {
    const d = new Date(isoString);
    const options = {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
    };
    return d.toLocaleString(undefined, options); // uses browser locale
}

// ---------- LOGS DASHBOARD ----------
async function loadAuthLogs() {
    const list = document.getElementById("authLogsList");
    if (!list) return;
    const res = await fetch(`${API_URL_AS}/admin/logs`, { credentials: "include" });
    const logs = await res.json();
    
    
    list.innerHTML = "";
    logs.forEach(log => {
        const li = document.createElement("li");
        li.textContent = `[${formatTimestamp(log.timestamp)}] ${log.username}: ${log.action} | ${log.details}`;
        list.appendChild(li);
    });
}

async function loadFileLogs() {
    const list = document.getElementById("fileLogsList");
    if (!list) return;
    const res = await fetch(`${API_URL_FS}/admin/logs`, { credentials: "include" });
    const logs = await res.json();
    
    list.innerHTML = "";
    logs.forEach(log => {
        const li = document.createElement("li");
        li.textContent = `[${formatTimestamp(log.timestamp)}] ${log.username}: ${log.action} | ${log.filename}`;
        list.appendChild(li);
    });
}

// Auto-load logs if dashboard is present
if(document.getElementById("authLogsList")) loadAuthLogs();
if(document.getElementById("fileLogsList")) loadFileLogs();

// Manual refresh buttons
document.getElementById("refreshAuthLogsBtn")?.addEventListener("click", () => {
    loadAuthLogs();
});

document.getElementById("refreshFileLogsBtn")?.addEventListener("click", () => {
    loadFileLogs();
});

// Set interval for refreshed updates
setInterval(() => {
    loadAuthLogs();
    loadFileLogs();
}, 10000); // every 10 seconds


