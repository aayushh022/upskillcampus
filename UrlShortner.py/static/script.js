// =========================================
// Smart URL Shortener
// Developed by Ayush Kumar
// =========================================


// Copy URL Function
function copyURL() {

    const url = document.getElementById("shortURL");

    url.select();
    url.setSelectionRange(0, 99999);

    navigator.clipboard.writeText(url.value);

    showToast("✅ Link copied successfully!");

}


// Toast Notification
function showToast(message) {

    let toast = document.createElement("div");

    toast.innerHTML = message;

    toast.style.position = "fixed";
    toast.style.top = "20px";
    toast.style.right = "20px";
    toast.style.background = "#198754";
    toast.style.color = "white";
    toast.style.padding = "12px 20px";
    toast.style.borderRadius = "10px";
    toast.style.boxShadow = "0 5px 15px rgba(0,0,0,.2)";
    toast.style.zIndex = "9999";
    toast.style.fontWeight = "600";

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 2500);

}


// Loading Effect
document.addEventListener("DOMContentLoaded", () => {

    const form = document.querySelector("form");

    if (form) {

        form.addEventListener("submit", () => {

            const button = form.querySelector("button");

            button.disabled = true;

            button.innerHTML =
                '<i class="fa-solid fa-spinner fa-spin"></i> Generating...';

        });

    }

});