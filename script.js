(function () {
  "use strict";

  const root = document.documentElement;
  const toggles = Array.from(document.querySelectorAll(".theme-toggle"));
  const uploadForm = document.getElementById("uploadForm");
  const fileInput = document.getElementById("fileInput");
  const dropZone = document.getElementById("dropZone");
  const selectedFile = document.getElementById("selectedFile");
  const pasteText = document.getElementById("pasteText");
  const processTextButton = document.getElementById("processTextButton");
  const clearTextButton = document.getElementById("clearTextButton");
  const results = document.getElementById("results");
  const chatForm = document.getElementById("chatForm");
  const chatWindow = document.getElementById("chatWindow");
  const aiQuestion = document.getElementById("aiQuestion");

  const samples = {
    insurance:
      "Dear Policyholder, your insurance policy renewal payment of Rs. 7,850 must be completed before 15 July 2026. If payment is not received, your coverage will lapse. For assistance call 1800-456-7890.",
    medical:
      "Patient discharge summary: The patient must take prescribed medicine twice daily for seven days. Follow-up consultation is required on 10 July 2026. Contact care desk at 1800-222-100.",
    government:
      "You are hereby notified that Aadhaar verification must be completed before 20 July 2026. Failure to complete verification may suspend benefit processing. Call 1947 for help.",
    electricity:
      "Electricity bill payment of Rs. 2,450 is due before 12 July 2026. Late payment may lead to a penalty or power disconnection. Contact 1912 for support.",
    bank:
      "Your loan EMI of Rs. 12,300 is due on 5 July 2026. Please maintain sufficient balance. If payment fails, charges may apply. Call 1800-300-900."
  };

  document.addEventListener("DOMContentLoaded", () => {
    setTheme(localStorage.getItem("claritydoc-theme") || "dark");
    refreshIcons();
    bindThemeToggles();
    bindUpload();
    bindPasteText();
    bindSamples();
    bindOfflineChat();
    bindKeyboardShortcuts();
  });

  function refreshIcons() {
    if (window.lucide) {
      window.lucide.createIcons();
    }
  }

  function setTheme(theme) {
    root.dataset.theme = theme;
    localStorage.setItem("claritydoc-theme", theme);
    toggles.forEach((toggle) => {
      toggle.setAttribute("aria-pressed", String(theme === "light"));
      const iconName = theme === "light" ? "sun" : "moon";
      if (toggle.classList.contains("icon-button")) {
        toggle.innerHTML = `<i data-lucide="${iconName}"></i>`;
      }
    });
    refreshIcons();
  }

  function bindThemeToggles() {
    toggles.forEach((toggle) => {
      toggle.addEventListener("click", () => {
        setTheme(root.dataset.theme === "dark" ? "light" : "dark");
      });
    });
  }

  function bindUpload() {
    if (!uploadForm || !fileInput || !dropZone) {
      return;
    }

    dropZone.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        fileInput.click();
      }
    });

    ["dragenter", "dragover"].forEach((eventName) => {
      dropZone.addEventListener(eventName, (event) => {
        event.preventDefault();
        dropZone.classList.add("is-dragging");
      });
    });

    ["dragleave", "drop"].forEach((eventName) => {
      dropZone.addEventListener(eventName, (event) => {
        event.preventDefault();
        dropZone.classList.remove("is-dragging");
      });
    });

    dropZone.addEventListener("drop", (event) => {
      const file = event.dataTransfer.files[0];
      if (!file) {
        return;
      }
      fileInput.files = event.dataTransfer.files;
      showSelectedFile(file);
      processFile(file);
    });

    fileInput.addEventListener("change", () => {
      const file = fileInput.files[0];
      showSelectedFile(file);
      if (file) {
        processFile(file);
      }
    });

    uploadForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const file = fileInput.files[0];
      if (!file) {
        renderError("Please choose a PDF, PNG, JPG, or JPEG file first.");
        return;
      }
      processFile(file);
    });
  }

  function bindPasteText() {
    if (!processTextButton || !pasteText) {
      return;
    }

    processTextButton.addEventListener("click", () => {
      processText(pasteText.value.trim());
    });

    clearTextButton?.addEventListener("click", () => {
      pasteText.value = "";
      renderEmpty();
    });
  }

  function bindSamples() {
    document.querySelectorAll("[data-sample]").forEach((button) => {
      button.addEventListener("click", () => {
        const key = button.getAttribute("data-sample");
        const text = samples[key] || samples.insurance;
        if (pasteText) {
          pasteText.value = text;
        }
        processText(text);
      });
    });
  }

  function bindKeyboardShortcuts() {
    document.addEventListener("keydown", (event) => {
      const isMeta = event.metaKey || event.ctrlKey;
      if (!isMeta) {
        return;
      }

      if (event.key.toLowerCase() === "n") {
        event.preventDefault();
        fileInput?.click();
      }

      if (event.key.toLowerCase() === "k") {
        event.preventDefault();
        document.querySelector(".search-box input")?.focus();
      }

      if (event.key === "/") {
        event.preventDefault();
        aiQuestion?.focus();
      }
    });
  }

  function bindOfflineChat() {
    if (!chatForm || !aiQuestion) {
      return;
    }

    chatForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const question = aiQuestion.value.trim();
      if (!question) {
        return;
      }

      appendChatMessage("user", question);
      aiQuestion.value = "";
      const loadingMessage = appendChatMessage("ai", "Thinking locally...");

      try {
        const response = await fetch("/ask-ai", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question })
        });
        const payload = await response.json();
        loadingMessage.remove();

        if (!response.ok || !payload.success) {
          const message = response.status === 404
            ? "Offline AI is not loaded in the running server yet. Stop the current Flask server and restart it, then ask again."
            : payload.error || "I could not answer that offline.";
          appendChatMessage("ai", message);
          return;
        }

        appendChatMessage("ai", payload.answer, payload.sources || []);
      } catch (error) {
        loadingMessage.remove();
        appendChatMessage("ai", `Offline AI failed: ${error.message}`);
      }
    });
  }

  async function processFile(file) {
    const data = new FormData();
    data.append("file", file);
    renderLoading("Running OCR and simplifying locally...");

    try {
      const response = await fetch("/upload", { method: "POST", body: data });
      const payload = await response.json();
      if (!response.ok || !payload.success) {
        renderError(payload.error || payload.message || "File processing failed.");
        return;
      }
      renderResult(payload);
    } catch (error) {
      renderError(`Upload failed: ${error.message}`);
    }
  }

  async function processText(text) {
    if (!text) {
      renderError("Paste document text before simplifying.");
      return;
    }

    renderLoading("Rewriting pasted text in simple words...");

    try {
      const response = await fetch("/process-text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      });
      const payload = await response.json();
      if (!response.ok || !payload.success) {
        renderError(payload.error || payload.message || "Text processing failed.");
        return;
      }
      renderResult(payload);
    } catch (error) {
      renderError(`Text processing failed: ${error.message}`);
    }
  }

  function showSelectedFile(file) {
    if (!selectedFile) {
      return;
    }
    selectedFile.textContent = file ? `Selected: ${file.name} (${formatBytes(file.size)})` : "";
  }

  function renderEmpty() {
    if (!results) {
      return;
    }
    results.innerHTML = `
      <div class="result-empty">
        <i data-lucide="file-search"></i>
        <p>Your simplified explanation will appear here after processing.</p>
      </div>
    `;
    refreshIcons();
  }

  function renderLoading(message) {
    if (!results) {
      return;
    }
    results.scrollIntoView({ behavior: "smooth", block: "nearest" });
    results.innerHTML = `
      <div class="loading-state">
        <div>
          <p>${escapeHtml(message)}</p>
          <div class="shimmer" style="margin-top:16px"></div>
        </div>
      </div>
    `;
  }

  function renderError(message) {
    if (!results) {
      return;
    }
    results.innerHTML = `
      <article class="result-card full">
        <div class="result-title"><i data-lucide="alert-triangle"></i> Needs attention</div>
        <p>${escapeHtml(message)}</p>
      </article>
    `;
    results.scrollIntoView({ behavior: "smooth", block: "nearest" });
    refreshIcons();
  }

  function renderResult(payload) {
    const result = payload.result || {};
    const priority = result.priority || "Low";
    const priorityClass = priority.toLowerCase().includes("high")
      ? "high"
      : priority.toLowerCase().includes("medium")
        ? "medium"
        : "low";

    results.innerHTML = `
      ${card("Document Type", "file-text", value(result.document_type || "General Document"))}
      ${card("Priority", priorityClass === "high" ? "alert-triangle" : "shield-check", `<span class="priority-badge ${priorityClass}">${escapeHtml(priority)}</span>`)}
      ${card("Easy Explanation", "sparkles", list(result.easy_explanation), "full")}
      ${card("Important Points", "check-circle-2", list(result.important_points), "full")}
      ${card("Action Required", "circle-alert", value(result.action_required || "No action found"))}
      ${card("Deadline", "calendar", value(result.deadline || "No deadline found"))}
      ${card("Amount Due", "wallet", value(result.amount_due || "No amount found"))}
      ${card("Contact Number", "phone", value(result.contact || "No contact found"))}
    `;
    results.scrollIntoView({ behavior: "smooth", block: "nearest" });
    refreshIcons();
  }

  function appendChatMessage(role, text, sources = []) {
    if (!chatWindow) {
      return document.createElement("div");
    }

    const message = document.createElement("div");
    message.className = `chat-message ${role}`;
    const icon = role === "user" ? "user" : "sparkles";
    const sourceHtml = sources.length
      ? `<span class="chat-sources">${sources
          .map((source) => `Source: ${escapeHtml(source.filename)} (${escapeHtml(source.document_type)})`)
          .join("<br>")}</span>`
      : "";
    message.innerHTML = `
      <span><i data-lucide="${icon}"></i></span>
      <p>${escapeHtml(text)}</p>
      ${sourceHtml}
    `;
    chatWindow.appendChild(message);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    refreshIcons();
    return message;
  }

  function card(title, icon, content, extraClass = "") {
    return `
      <article class="result-card ${extraClass}">
        <div class="result-title"><i data-lucide="${icon}"></i> ${escapeHtml(title)}</div>
        ${content}
      </article>
    `;
  }

  function list(items) {
    const clean = Array.isArray(items) ? items.filter(Boolean) : [];
    if (!clean.length) {
      return "<p>No details found.</p>";
    }
    return `<ul>${clean.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
  }

  function value(text) {
    return `<p class="result-value">${escapeHtml(text)}</p>`;
  }

  function escapeHtml(valueToEscape) {
    return String(valueToEscape ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function formatBytes(bytes) {
    if (!bytes) {
      return "0 KB";
    }
    const units = ["B", "KB", "MB", "GB"];
    const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
    return `${(bytes / Math.pow(1024, index)).toFixed(index ? 1 : 0)} ${units[index]}`;
  }
})();
