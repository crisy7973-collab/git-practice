const MAX_PROMPT = 200;
const photoInput = document.getElementById("photoInput");
const photoSlot = document.getElementById("photoSlot");
const photoPreview = document.getElementById("photoPreview");
const promptInput = document.getElementById("promptInput");
const promptCount = document.getElementById("promptCount");
const generateBtn = document.getElementById("generateBtn");
const note = document.getElementById("note");
const chipRow = document.getElementById("chipRow");

let photoFile = null;

function syncState() {
  const prompt = promptInput.value.trim();
  generateBtn.disabled = !(photoFile && prompt);
  promptCount.textContent = `${promptInput.value.length} / ${MAX_PROMPT}`;
  if (!photoFile) {
    note.textContent = "请先上传一张人物老照片";
  } else if (!prompt) {
    note.textContent = "写一句提示词，告诉 AI 人物如何动作";
  } else {
    note.textContent = "照片和提示词已备好，可交给后端生成";
  }
}

photoSlot.addEventListener("click", () => photoInput.click());

photoInput.addEventListener("change", () => {
  const file = photoInput.files && photoInput.files[0];
  if (!file) return;
  photoFile = file;
  photoPreview.src = URL.createObjectURL(file);
  photoSlot.classList.add("has-photo");
  syncState();
});

promptInput.addEventListener("input", () => {
  const current = promptInput.value.trim();
  chipRow.querySelectorAll(".chip").forEach((item) => {
    item.classList.toggle("is-on", (item.dataset.prompt || "") === current);
  });
  syncState();
});
promptInput.addEventListener("change", syncState);

chipRow.addEventListener("click", (event) => {
  const chip = event.target.closest(".chip");
  if (!chip) return;
  promptInput.value = chip.dataset.prompt || "";
  chipRow.querySelectorAll(".chip").forEach((item) => {
    item.classList.toggle("is-on", item === chip);
  });
  syncState();
});

generateBtn.addEventListener("click", () => {
  window.yiYingJob = {
    file: photoFile,
    prompt: promptInput.value.trim(),
  };
  note.textContent = `已打包：${photoFile.name} · 「${window.yiYingJob.prompt.slice(0, 18)}${window.yiYingJob.prompt.length > 18 ? "…" : ""}」`;
});

syncState();
