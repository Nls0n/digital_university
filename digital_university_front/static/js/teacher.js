document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("teacher-requests")) loadTeacherRequests();
    if (document.getElementById("groups")) loadGroups();
    if (document.querySelector("[data-group-page]")) loadGroupPage();
});

const teacherId = 501;

// ------------ Заявки преподавателя ------------
async function loadTeacherRequests() {
    const data = await apiGet(`/teacher/${teacherId}/requests`);
    const box = document.getElementById("teacher-requests");

    data.requests.forEach(r => {
        box.innerHTML += `
            <div class="list-item">
                <b>${r.type}</b><br>
                ${r.status}<br>
                ${r.date}
            </div>
        `;
    });
}

// ------------ Список групп ------------
async function loadGroups() {
    const data = await apiGet(`/teacher/${teacherId}/groups`);
    const box = document.getElementById("groups");

    data.groups.forEach(g => {
        box.innerHTML += `
            <a class="list-item" href="group.html?id=${g.id}">
                ${g.name}
            </a>
        `;
    });
}

// ------------ Страница группы ------------
async function loadGroupPage() {
    const params = new URLSearchParams(location.search);
    const groupId = params.get("id");

    const group = await apiGet(`/groups/${groupId}`);

    document.getElementById("group-title").innerText = group.name;

    // ======= студенты =======
    const studentsBox = document.getElementById("students");

    group.students.forEach(s => {
        studentsBox.innerHTML += `
            <div class="list-item">
                <b>${s.name}</b><br>
                Оценка: <input type="number" min="0" max="10" value="${s.grade}">
            </div>
        `;
    });

    // ======= задания =======
    const assignBox = document.getElementById("assignments");

    group.assignments.forEach(a => {
        assignBox.innerHTML += `
            <div class="list-item">
                <b>${a.title}</b>
                <button onclick="deleteAssignment(${groupId}, ${a.id})">Удалить</button>
            </div>
        `;
    });

    // ======= кнопка создания задания =======
    document.getElementById("create-btn").onclick = () => {
        const val = document.getElementById("new-assignment").value;
        createAssignment(groupId, val);
    };
}

// ------------ Создание задания ------------
async function createAssignment(groupId, title) {
    await apiPost(`/groups/${groupId}/assignments`, { title });
    alert("Создано!");
    location.reload();
}

// ------------ Удаление задания ------------
async function deleteAssignment(groupId, assignmentId) {
    await apiDelete(`/groups/${groupId}/assignments/${assignmentId}`);
    alert("Удалено");
    location.reload();
}
