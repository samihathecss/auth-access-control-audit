const recordOwners = {
    A1: "alice",
    A2: "alice",
    B1: "bob",
    B2: "bob"
};

const recordTitles = {
    A1: "Alice's Note 1",
    A2: "Alice's Note 2",
    B1: "Bob's Note 1",
    B2: "Bob's Note 2"
};

let session = {
    authenticated: false,
    user_id: null,
    role: null
};

const userSelect = document.getElementById("userSelect");
const loginBtn = document.getElementById("loginBtn");
const logoutBtn = document.getElementById("logoutBtn");
const authStatus = document.getElementById("authStatus");
const sessionUser = document.getElementById("sessionUser");
const sessionRole = document.getElementById("sessionRole");

const targetRecord = document.getElementById("targetRecord");
const checkOwnership = document.getElementById("checkOwnership");
const ownershipOutcome = document.getElementById("ownershipOutcome");
const ownershipStatus = document.getElementById("ownershipStatus");
const ownershipResponse = document.getElementById("ownershipResponse");

const checkAdmin = document.getElementById("checkAdmin");
const adminOutcome = document.getElementById("adminOutcome");
const adminStatus = document.getElementById("adminStatus");
const adminResponse = document.getElementById("adminResponse");

function updateSessionUI() {
    if (session.authenticated && session.user_id) {
        authStatus.textContent = "YES";
        authStatus.className = "badge badge--success";
        sessionUser.textContent = session.user_id;
        sessionRole.textContent = session.role || "—";
    } else {
        authStatus.textContent = "NO";
        authStatus.className = "badge badge--muted";
        sessionUser.textContent = "—";
        sessionRole.textContent = "—";
    }
}

function setBadge(el, variant, text) {
    el.textContent = text;
    el.className = `badge badge--${variant}`;
}

loginBtn.addEventListener("click", () => {
    const selected = userSelect.value;
    session = {
        authenticated: true,
        user_id: selected,
        role: selected === "admin" ? "admin" : "user"
    };
    updateSessionUI();
});

logoutBtn.addEventListener("click", () => {
    session = {
        authenticated: false,
        user_id: null,
        role: null
    };
    updateSessionUI();
    setBadge(ownershipOutcome, "muted", "—");
    ownershipStatus.textContent = "—";
    ownershipResponse.textContent = "—";
    setBadge(adminOutcome, "muted", "—");
    adminStatus.textContent = "—";
    adminResponse.textContent = "—";
});

checkOwnership.addEventListener("click", () => {
    const recordId = targetRecord.value;
    const owner = recordOwners[recordId];

    if (!session.authenticated || !session.user_id) {
        setBadge(ownershipOutcome, "warning", "DENIED");
        ownershipStatus.textContent = "302";
        ownershipResponse.textContent = JSON.stringify({ note: "Unauthenticated - login_required would redirect (documented behavior)" }, null, 2);
        return;
    }

    if (session.user_id === owner) {
        setBadge(ownershipOutcome, "success", "ALLOWED");
        ownershipStatus.textContent = "200";
        ownershipResponse.textContent = JSON.stringify({
            id: recordId,
            title: recordTitles[recordId],
            content: "Synthetic private content for record " + recordId + "."
        }, null, 2);
    } else {
        setBadge(ownershipOutcome, "danger", "DENIED");
        ownershipStatus.textContent = "404";
        ownershipResponse.textContent = JSON.stringify({ error: "Record not found" }, null, 2);
    }
});

checkAdmin.addEventListener("click", () => {
    if (!session.authenticated || !session.user_id) {
        setBadge(adminOutcome, "warning", "DENIED");
        adminStatus.textContent = "302";
        adminResponse.textContent = JSON.stringify({ note: "Unauthenticated - admin_required would redirect to login (documented behavior)" }, null, 2);
        return;
    }

    if (session.role === "admin" && session.user_id === "admin") {
        setBadge(adminOutcome, "success", "ALLOWED");
        adminStatus.textContent = "200";
        adminResponse.textContent = JSON.stringify({
            message: "Administrator access granted",
            section: "admin"
        }, null, 2);
        return;
    }

    if (session.role === "admin" && session.user_id !== "admin") {
        setBadge(adminOutcome, "danger", "DENIED");
        adminStatus.textContent = "403";
        adminResponse.textContent = JSON.stringify({ error: "Forbidden" }, null, 2);
        return;
    }

    if (session.role === "user") {
        setBadge(adminOutcome, "danger", "DENIED");
        adminStatus.textContent = "403";
        adminResponse.textContent = JSON.stringify({ error: "Forbidden" }, null, 2);
        return;
    }

    setBadge(adminOutcome, "danger", "DENIED");
    adminStatus.textContent = "403";
    adminResponse.textContent = JSON.stringify({ error: "Forbidden" }, null, 2);
});

updateSessionUI();
setBadge(ownershipOutcome, "muted", "—");
ownershipStatus.textContent = "—";
ownershipResponse.textContent = "—";
setBadge(adminOutcome, "muted", "—");
adminStatus.textContent = "—";
adminResponse.textContent = "—";
