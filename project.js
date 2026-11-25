// Garden Harvest Register - Dashboard & Login Controller

// 1. LOGIN & AUTH VIEW TOGGLE
const DEMO_USERS = {
    admin:  { password: "garden2026", name: "Administrator", role: "Manager" },
    akarsh: { password: "plot2026",   name: "Akarsh Reddy",  role: "Lead Harvester" }
};
const GUEST = { name: "Guest", role: "Preview" };
const SESSION_KEY = "ghrSession";

const loginView = document.getElementById("loginView");
const dashboardView = document.getElementById("dashboardView");
const loginForm = document.getElementById("loginForm");
const usernameInput = document.getElementById("usernameInput");
const passwordInput = document.getElementById("passwordInput");
const userNameDisplay = document.getElementById("userNameDisplay");
const userRoleDisplay = document.getElementById("userRoleDisplay");

function showDashboard(user) {
    if (userNameDisplay) userNameDisplay.textContent = user.name;
    if (userRoleDisplay) userRoleDisplay.textContent = user.role;
    if (loginView) loginView.style.display = "none";
    if (dashboardView) dashboardView.style.display = "block";
    filterHarvestTable();
}

function showLogin() {
    if (dashboardView) dashboardView.style.display = "none";
    if (loginView) loginView.style.display = "flex";
    if (passwordInput) passwordInput.value = "";
}

function signIn(username, password) {
    const key = (username || "").trim().toLowerCase();
    const account = DEMO_USERS[key] || { name: (username || "User"), role: "Harvester" };
    try { sessionStorage.setItem(SESSION_KEY, key); } catch (e) {}
    showDashboard(account);
}

if (loginForm) {
    loginForm.addEventListener("submit", (e) => {
        e.preventDefault();
        signIn(usernameInput.value, passwordInput.value);
    });
}

const guestBtn = document.getElementById("guestBtn");
if (guestBtn) {
    guestBtn.addEventListener("click", () => {
        try { sessionStorage.setItem(SESSION_KEY, "guest"); } catch (e) {}
        showDashboard(GUEST);
    });
}

const quickAdminBtn = document.getElementById("quickAdminBtn");
if (quickAdminBtn) {
    quickAdminBtn.addEventListener("click", () => signIn("admin", "garden2026"));
}

const quickAkarshBtn = document.getElementById("quickAkarshBtn");
if (quickAkarshBtn) {
    quickAkarshBtn.addEventListener("click", () => signIn("akarsh", "plot2026"));
}

const logoutBtn = document.getElementById("logoutBtn");
if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
        try { sessionStorage.removeItem(SESSION_KEY); } catch (e) {}
        if (usernameInput) usernameInput.value = "";
        showLogin();
    });
}

// 2. HARVEST TABLE FILTER & SEARCH
const filterInput = document.getElementById("filterInput");
const categoryFilter = document.getElementById("categoryFilter");
const bedFilter = document.getElementById("bedFilter");
const recordCounter = document.getElementById("recordCounter");
const tableBody = document.getElementById("tableBody");
const categoryPills = document.querySelectorAll("#categoryPills .pill-btn");

function filterHarvestTable() {
    if (!tableBody) return;
    const term = filterInput ? filterInput.value.trim().toLowerCase() : "";
    const selectedCat = categoryFilter ? categoryFilter.value : "all";
    const selectedBed = bedFilter ? bedFilter.value : "all";
    const rows = tableBody.querySelectorAll("tr");

    let visibleCount = 0;

    rows.forEach((row) => {
        const rowText = row.textContent.toLowerCase();
        const rowCategory = (row.dataset.category || "").toLowerCase();
        const rowBed = (row.dataset.bed || "").toLowerCase();

        const matchesSearch = !term || rowText.includes(term);

        let matchesCat = (selectedCat === "all");
        if (!matchesCat) {
            const target = selectedCat.toLowerCase();
            matchesCat = rowCategory.includes(target) || (target.includes("root") && rowCategory.includes("root"));
        }

        const matchesBed = (selectedBed === "all") || rowBed.includes(selectedBed.toLowerCase());

        const isVisible = matchesSearch && matchesCat && matchesBed;
        row.style.display = isVisible ? "" : "none";
        row.hidden = !isVisible;

        if (isVisible) visibleCount++;
    });

    if (recordCounter) {
        recordCounter.textContent = `Showing ${visibleCount} of ${rows.length} records`;
    }

    // Sync active category pill
    categoryPills.forEach((pill) => {
        const pCat = pill.dataset.cat;
        pill.classList.toggle("active", pCat === selectedCat);
    });
}

// Category Pills click handler
categoryPills.forEach((pill) => {
    pill.addEventListener("click", () => {
        const cat = pill.dataset.cat;
        if (categoryFilter) categoryFilter.value = cat;
        filterHarvestTable();
    });
});

if (filterInput) filterInput.addEventListener("input", filterHarvestTable);
if (categoryFilter) categoryFilter.addEventListener("change", filterHarvestTable);
if (bedFilter) bedFilter.addEventListener("change", filterHarvestTable);

// 3. TABLE COLUMN SORTING
let currentSort = { colIndex: 0, asc: true };

document.querySelectorAll("#harvestTable th[data-sort]").forEach((th) => {
    th.addEventListener("click", () => {
        const colIndex = Array.from(th.parentNode.children).indexOf(th);
        if (currentSort.colIndex === colIndex) {
            currentSort.asc = !currentSort.asc;
        } else {
            currentSort.colIndex = colIndex;
            currentSort.asc = true;
        }

        // Header arrows
        document.querySelectorAll("#harvestTable th[data-sort]").forEach((h) => {
            const label = h.textContent.replace(/[ ▲▼⇕]/g, "").trim();
            h.textContent = `${label} ⇕`;
        });
        const label = th.textContent.replace(/[ ▲▼⇕]/g, "").trim();
        th.textContent = `${label} ${currentSort.asc ? "▲" : "▼"}`;

        sortTableRows(colIndex, currentSort.asc);
    });
});

function sortTableRows(colIndex, asc) {
    if (!tableBody) return;
    const rows = Array.from(tableBody.querySelectorAll("tr"));

    rows.sort((a, b) => {
        let valA = a.children[colIndex] ? a.children[colIndex].textContent.trim().toLowerCase() : "";
        let valB = b.children[colIndex] ? b.children[colIndex].textContent.trim().toLowerCase() : "";

        // Number comparison for Quantity (e.g. 14.5 kg)
        const numA = parseFloat(valA.replace(/[^0-9.]/g, ""));
        const numB = parseFloat(valB.replace(/[^0-9.]/g, ""));
        if (!isNaN(numA) && !isNaN(numB)) {
            return asc ? numA - numB : numB - numA;
        }

        if (valA < valB) return asc ? -1 : 1;
        if (valA > valB) return asc ? 1 : -1;
        return 0;
    });

    rows.forEach((r) => tableBody.appendChild(r));
}

// 4. RESTORE OR INITIALIZE SESSION
(function init() {
    let saved = null;
    try { saved = sessionStorage.getItem(SESSION_KEY); } catch (e) {}

    if (saved === "guest") {
        showDashboard(GUEST);
    } else if (saved && DEMO_USERS[saved]) {
        showDashboard(DEMO_USERS[saved]);
    } else {
        // Show login by default
        showLogin();
    }

    filterHarvestTable();
})();
