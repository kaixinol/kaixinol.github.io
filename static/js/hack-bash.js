document.querySelectorAll("pre.language-bash ~ button.copy").forEach((btn) => {
  // 检查是否已经处理过，防止重复绑定监听器
  if (btn.dataset.initialized) return;
  btn.dataset.initialized = "true";

  btn.addEventListener("click", async () => {
    const pre = btn.previousElementSibling;
    if (!pre) return;

    const codeEl = pre.querySelector("code");
    if (!codeEl) return;

    // 处理 Bash 提示符
    const text = codeEl.innerText
      .split("\n")
      .map((line) => line.replace(/^(?:\$|#)\s+/, ""))
      .join("\n");

    try {
      await navigator.clipboard.writeText(text);

      // 直接在原按钮上操作类名
      btn.classList.add("copied");

      // 提示：确保 CSS 中 .copy.copied 包含了对号的样式
      setTimeout(() => {
        btn.classList.remove("copied");
      }, 800);
    } catch (err) {
      console.error("复制失败:", err);
    }
  });
});
