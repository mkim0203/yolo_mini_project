const API_BASE_URL = "http://localhost:8000";

async function loadSidebar() {
    const response = await fetch("/view/components/sidebar.html");

    if (!response.ok) {
        throw new Error("메뉴를 불러오지 못했습니다.");
    }

    const html = await response.text();

    document.getElementById("sidebar-container").innerHTML = html;

    setActiveMenu();
}

function setActiveMenu() {
    const currentPage = document.body.dataset.page;

    document.querySelectorAll(".menu").forEach(menu => {
        menu.classList.toggle(
            "active",
            menu.dataset.page === currentPage
        );
    });
}

function formatDate(date) {
    return new Date(date).toLocaleString("ko-KR", {
        timeZone: "Asia/Seoul",
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        hour12: false
    });
}

document.addEventListener("DOMContentLoaded", loadSidebar);