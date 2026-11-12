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

function getFoodProbability(score) {
    try {
        if (score == null) return "-";

        // 숫자로 변환 후 유효한 숫자인지(NaN 여부) 확인
        const numScore = Number(score);
        if (Number.isNaN(numScore)) return "-";

        // 확률 계산 및 반환
        const result = ((1 - numScore) * 100).toFixed(2) + "%";
        return result;

    } catch (error) {
        // 예외 발생 시 콘솔에 로그 출력 후 기본값 반환
        console.error("음식 확률 계산 중 오류 발생:", error);
        return "-";
    }
}

document.addEventListener("DOMContentLoaded", loadSidebar);