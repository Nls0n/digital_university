// teacher-app.js - итоговый файл для панели преподавателя

document.addEventListener("DOMContentLoaded", () => {
    initApp();
});

// Глобальная переменная для teacherId
let teacherId = null;

// Функция инициализации приложения
function initApp() {
    if (window.WebApp) {
        // Сообщаем Max, что приложение готово
        window.WebApp.ready();
        
        // Получаем ID пользователя
        if (window.WebApp.initDataUnsafe && window.WebApp.initDataUnsafe.user) {
            const user = window.WebApp.initDataUnsafe.user;
            teacherId = user.id;
            
            
            // Показываем информацию о пользователе
            showUserInfo(user);
            
            // Загружаем данные преподавателя
            loadTeacherData();
            
        } else {
            showError('Данные пользователя недоступны');
            tryFallbackTeacherId();
        }
    } else {
        showError('Max Web App SDK не загружен');
        tryFallbackTeacherId();
    }
}

// Показать информацию о пользователе
function showUserInfo(user) {
    const userInfoElement = document.getElementById('user-info');
    if (userInfoElement) {
        userInfoElement.innerHTML = `
            <div class="list-item">
                <strong>Преподаватель:</strong> ${user.first_name || ''} ${user.last_name || ''}<br>
                <strong>ID:</strong> ${teacherId}<br>
                <strong>Платформа:</strong> ${window.WebApp.platform || 'Неизвестно'}
            </div>
        `;
    }
}

// Попытка использовать fallback ID для тестирования
function tryFallbackTeacherId() {
    teacherId = getTestTeacherId();
    if (teacherId) {
        loadTeacherData();
    } else {
        showError('Не удалось получить ID преподавателя');
    }
}

// Функция для тестирования (если Max Web App недоступен)
function getTestTeacherId() {
    const urlParams = new URLSearchParams(window.location.search);
    const testId = urlParams.get('teacher_id');
    if (testId) {
        const userInfoElement = document.getElementById('user-info');
        if (userInfoElement) {
            userInfoElement.innerHTML += `
                <div class="error">⚠ Режим тестирования (ID: ${testId})</div>
            `;
        }
        return testId;
    }
    return null;
}

// Загрузка данных преподавателя
function loadTeacherData() {
    // Показываем разделы интерфейса
    const requestsElement = document.getElementById('teacher-requests');
    const groupsElement = document.getElementById('groups');
    
    if (requestsElement) requestsElement.style.display = 'block';
    if (groupsElement) groupsElement.style.display = 'block';
    
    // Загружаем данные
    if (document.getElementById("teacher-requests")) loadTeacherRequests();
    if (document.getElementById("groups")) loadGroups();
    if (document.querySelector("[data-group-page]")) loadGroupPage();
}

// ------------ Заявки преподавателя ------------
async function loadTeacherRequests() {
    if (!teacherId) return;
    
    try {
        const data = await apiGet(`/teacher/${teacherId}/requests`);
        const box = document.getElementById("teacher-requests");

        // Очищаем контейнер перед добавлением
        const existingContent = box.querySelector('.list-item') ? '' : '<h2>Мои заявки</h2>';
        box.innerHTML = existingContent;

        data.requests.forEach(r => {
            box.innerHTML += `
                <div class="list-item">
                    <b>${r.type}</b><br>
                    Статус: ${r.status}<br>
                    Дата: ${r.date}
                </div>
            `;
        });
    } catch (error) {
        console.error("Ошибка загрузки заявок:", error);
        showError("Не удалось загрузить заявки");
    }
}

// ------------ Список групп ------------
async function loadGroups() {
    if (!teacherId) return;
    
    try {
        const data = await apiGet(`/teacher/${teacherId}/groups`);
        const box = document.getElementById("groups");

        // Очищаем контейнер перед добавлением
        const existingContent = box.querySelector('.list-item') ? '' : '<h2>Мои группы</h2>';
        box.innerHTML = existingContent;

        data.groups.forEach(g => {
            box.innerHTML += `
                <a class="list-item" href="group.html?id=${g.id}&teacher_id=${teacherId}">
                    ${g.name}
                </a>
            `;
        });
    } catch (error) {
        console.error("Ошибка загрузки групп:", error);
        showError("Не удалось загрузить группы");
    }
}

// ------------ Страница группы ------------
async function loadGroupPage() {
    if (!teacherId) return;
    
    const params = new URLSearchParams(location.search);
    const groupId = params.get("id");

    if (!groupId) {
        showError("ID группы не указан");
        return;
    }

    try {
        const group = await apiGet(`/groups/${groupId}`);

        // Устанавливаем заголовок группы
        const titleElement = document.getElementById("group-title");
        if (titleElement) {
            titleElement.innerText = group.name;
        }

        // ======= студенты =======
        const studentsBox = document.getElementById("students");
        if (studentsBox) {
            studentsBox.innerHTML = '<h3>Студенты</h3>';
            
            group.students.forEach(s => {
                studentsBox.innerHTML += `
                    <div class="list-item">
                        <b>${s.name}</b><br>
                        Оценка: <input type="number" min="0" max="10" value="${s.grade}" 
                               onchange="updateGrade(${s.id}, this.value, ${groupId})">
                    </div>
                `;
            });
        }

        // ======= задания =======
        const assignBox = document.getElementById("assignments");
        if (assignBox) {
            assignBox.innerHTML = '<h3>Задания</h3>';
            
            group.assignments.forEach(a => {
                assignBox.innerHTML += `
                    <div class="list-item">
                        <b>${a.title}</b>
                        <button onclick="deleteAssignment(${groupId}, ${a.id})">Удалить</button>
                    </div>
                `;
            });
        }

        // ======= кнопка создания задания =======
        const createBtn = document.getElementById("create-btn");
        if (createBtn) {
            createBtn.onclick = () => {
                const inputElement = document.getElementById("new-assignment");
                const val = inputElement ? inputElement.value : '';
                
                if (val.trim()) {
                    createAssignment(groupId, val.trim());
                } else {
                    alert("Введите название задания");
                }
            };
        }

    } catch (error) {
        console.error("Ошибка загрузки страницы группы:", error);
        showError("Не удалось загрузить данные группы");
    }
}

// ------------ Обновление оценки студента ------------
async function updateGrade(studentId, grade, groupId) {
    if (!teacherId) return;
    
    try {
        await apiPost(`/students/${studentId}/grade`, { 
            grade: parseInt(grade),
            teacher_id: teacherId,
            group_id: groupId
        });
        showStatus("Оценка обновлена");
    } catch (error) {
        console.error("Ошибка обновления оценки:", error);
        showError("Ошибка при обновлении оценки");
    }
}

// ------------ Создание задания ------------
async function createAssignment(groupId, title) {
    if (!teacherId) return;
    
    try {
        await apiPost(`/groups/${groupId}/assignments`, { 
            title,
            teacher_id: teacherId
        });
        showStatus("Задание создано!");
        setTimeout(() => location.reload(), 1000);
    } catch (error) {
        console.error("Ошибка создания задания:", error);
        showError("Ошибка при создании задания");
    }
}

// ------------ Удаление задания ------------
async function deleteAssignment(groupId, assignmentId) {
    if (!teacherId) return;
    
    if (!confirm("Вы уверены, что хотите удалить это задание?")) {
        return;
    }
    
    try {
        await apiDelete(`/groups/${groupId}/assignments/${assignmentId}`, {
            teacher_id: teacherId
        });
        showStatus("Задание удалено");
        setTimeout(() => location.reload(), 1000);
    } catch (error) {
        console.error("Ошибка удаления задания:", error);
        showError("Ошибка при удалении задания");
    }
}

// ------------ Вспомогательные функции ------------

// Показать сообщение об ошибке
function showError(message) {
    console.error(message);
    
    // Создаем элемент ошибки
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = `❌ ${message}`;
    errorDiv.style.cssText = `
        background: #ffebee;
        color: #c62828;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        border: 1px solid #ffcdd2;
    `;
    
    // Добавляем в начало контейнера
    const container = document.querySelector('.container') || document.getElementById('app') || document.body;
    if (container) {
        container.prepend(errorDiv);
        setTimeout(() => errorDiv.remove(), 5000);
    }
}

// Показать статус сообщение
function showStatus(message) {
    console.log(message);
    
    const statusDiv = document.createElement('div');
    statusDiv.className = 'status-message';
    statusDiv.textContent = `✅ ${message}`;
    statusDiv.style.cssText = `
        background: #e8f5e8;
        color: #2e7d32;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        border: 1px solid #c8e6c9;
    `;
    
    const container = document.querySelector('.container') || document.getElementById('app') || document.body;
    if (container) {
        container.prepend(statusDiv);
        setTimeout(() => statusDiv.remove(), 3000);
    }
}

// Базовые API функции (заглушки - замените на реальные)
async function apiGet(url) {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
}

async function apiPost(url, data) {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
}

async function apiDelete(url, data = null) {
    const config = {
        method: 'DELETE',
    };
    
    if (data) {
        config.headers = {
            'Content-Type': 'application/json',
        };
        config.body = JSON.stringify(data);
    }
    
    const response = await fetch(url, config);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
}