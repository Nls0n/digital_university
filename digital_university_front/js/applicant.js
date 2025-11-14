document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("open-days")) loadOpenDays();
    if (document.getElementById("directions")) loadDirections();
    if (document.getElementById("about")) loadAbout();
    if (document.getElementById("admission-form")) initAdmissionForm();
});

// ------------ Дни открытых дверей ------------
async function loadOpenDays() {
    const data = await apiGet("/applicant/open-days");
    const box = document.getElementById("open-days");

    data.forEach(ev => {
        box.innerHTML += `
            <div class="list-item">
                <b>${ev.date}</b> — ${ev.time}<br>
                Место: ${ev.place}
            </div>
        `;
    });
}

// ------------ Направления подготовки ------------
async function loadDirections() {
    const data = await apiGet("/applicant/directions");
    const box = document.getElementById("directions");

    data.forEach(d => {
        box.innerHTML += `
            <div class="list-item">
                <b>${d.code}</b> — ${d.name}
            </div>
        `;
    });
}

// ------------ Описание университета ------------
async function loadAbout() {
    const data = await apiGet("/applicant/about");

    document.getElementById("about").innerHTML = `
        <p>${data.description}</p>
    `;
}

// ------------ Подать заявление ------------
function initAdmissionForm() {
    document
        .getElementById("admission-form")
        .addEventListener("submit", async (e) => {
            e.preventDefault();

            const name = document.getElementById("name").value;
            const email = document.getElementById("email").value;
            const direction = document.getElementById("direction").value;

            const res = await apiPost("/admission", {
                name,
                email,
                direction
            });

            alert("Заявка отправлена!");
        });
}
