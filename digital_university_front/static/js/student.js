document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("student-info")) loadStudentInfo();
    if (document.getElementById("schedule")) loadSchedule();
    if (document.getElementById("grades")) loadGrades();
    if (document.getElementById("achievements")) loadAchievements();
    if (document.getElementById("communities")) loadCommunities();
    if (document.getElementById("scholarship")) loadScholarship();
    if (document.getElementById("requests")) loadRequests();
});

const studentId = 1201;

// ------------ Личная информация студента ------------
async function loadStudentInfo() {
    const data = await apiGet(`/student/${studentId}`);

    document.getElementById("student-info").innerHTML = `
        <h2>${data.name}</h2>
        <p>Группа: ${data.group}</p>
        <p>Email: ${data.email}</p>
    `;
}

// ------------ Расписание ------------
async function loadSchedule() {
    const data = await apiGet(`/student/${studentId}/schedule`);
    const box = document.getElementById("schedule");

    data.schedule.forEach(day => {
        const div = document.createElement("div");
        div.className = "list-item";

        let items = day.items.map(
            i => `${i.time} — ${i.subject} (${i.room})`
        ).join("<br>");

        div.innerHTML = `<b>${day.day}</b><br>${items}`;
        box.appendChild(div);
    });
}

// ------------ Успеваемость ------------
async function loadGrades() {
    const data = await apiGet(`/student/${studentId}/grades`);
    const box = document.getElementById("grades");

    data.grades.forEach(g => {
        box.innerHTML += `
            <div class="list-item">
                <b>${g.subject}</b> (${g.type})<br>
                Оценка: ${g.grade}<br>
                ${g.date}
            </div>
        `;
    });
}

// ------------ Достижения ------------
async function loadAchievements() {
    const data = await apiGet(`/student/${studentId}/achievements`);
    const box = document.getElementById("achievements");

    data.achievements.forEach(a => {
        box.innerHTML += `
            <div class="list-item">
                <b>${a.title}</b><br>
                ${a.description}<br>
                ${a.date}
            </div>
        `;
    });
}

// ------------ Сообщества ------------
async function loadCommunities() {
    const data = await apiGet(`/student/${studentId}/communities`);
    const box = document.getElementById("communities");

    data.communities.forEach(c => {
        box.innerHTML += `
            <div class="list-item">
                <b>${c.name}</b><br>
                Роль: ${c.role}<br>
                ${c.meetings}
            </div>
        `;
    });
}

// ------------ Стипендия ------------
async function loadScholarship() {
    const data = await apiGet(`/student/${studentId}/scholarship`);
    const box = document.getElementById("scholarship");

    box.innerHTML = `
        <b>${data.type}</b><br>
        Текущая: ${data.current_amount} ₽<br>
        Следующая выплата: ${data.next_payment}<br><br>
        <b>История:</b><br>
    `;

    data.history.forEach(h => {
        box.innerHTML += `${h.date}: ${h.amount} ₽<br>`;
    });
}

// ------------ Заявки ------------
async function loadRequests() {
    const data = await apiGet(`/student/${studentId}/requests`);
    const box = document.getElementById("requests");

    data.requests.forEach(r => {
        box.innerHTML += `
            <div class="list-item">
                <b>${r.type}</b><br>
                Статус: ${r.status}<br>
                ${r.date}
            </div>
        `;
    });
}
