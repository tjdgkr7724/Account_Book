const passwordHelp = document.getElementById("password-help");
if (passwordHelp) {
  passwordHelp.addEventListener("click", () => {
    document.getElementById("password-notice").hidden = false;
    passwordHelp.setAttribute("aria-expanded", "true");
  });
}
