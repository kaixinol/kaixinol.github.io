const themeToggle = document.querySelector("#theme-toggle");
function toggleGistTheme() {
    document.querySelectorAll("div.gist-file").forEach((el) => {
        if (sessionStorage.getItem("theme") === "dark") {
            el.setAttribute("data-color-mode", "dark");
        }
    });
}
themeToggle.addEventListener("click", () => {
    toggleGistTheme();
});
toggleGistTheme();
