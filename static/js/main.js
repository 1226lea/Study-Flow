function announce(msg){
  const el = document.getElementById("statusMsg");
  if (!el) return;
  el.textContent = msg;
}

document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", (e) => {
      const captcha = document.getElementById("captcha");
      const err = document.getElementById("captchaErr");
      err.textContent = "";

      if (!captcha.value.trim()) {
        e.preventDefault();
        err.textContent = "Captcha is required.";
        captcha.setAttribute("aria-invalid", "true");
        captcha.focus();
        announce("Login error: captcha is required.");
      } else {
        captcha.removeAttribute("aria-invalid");
      }
    });
  }

 
  const filesInput = document.getElementById("files");
  const fileList = document.getElementById("fileList");

  if (filesInput && fileList) {
    let files = [];

    const render = () => {
      fileList.innerHTML = "";
      if (files.length === 0) {
        fileList.innerHTML = `<div class="text-muted small">No files selected.</div>`;
        return;
      }
      files.forEach((f, idx) => {
        const row = document.createElement("div");
        row.className = "d-flex justify-content-between align-items-center border rounded p-2 mb-2";
        row.innerHTML = `
          <div>
            <div class="fw-semibold">${f.name}</div>
            <div class="small text-muted">${Math.round(f.size/1024)} KB</div>
          </div>
          <button class="btn btn-outline-danger btn-sm" type="button" aria-label="Delete ${f.name}">Delete</button>
        `;
        row.querySelector("button").addEventListener("click", () => {
          files.splice(idx, 1);
          render();
          announce("File removed.");
        });
        fileList.appendChild(row);
      });
    };

    filesInput.addEventListener("change", () => {
      files = Array.from(filesInput.files || []);
      render();
      announce("Files selected.");
    });

    render();
  }
});