const API_URL = "/api/students";

async function loadStudents() {

    try {

        const response = await fetch(API_URL);

        if (!response.ok) {
            throw new Error("Failed to fetch student data");
        }

        const students = await response.json();

        const tbody = document.querySelector("#studentsTable tbody");

        tbody.innerHTML = "";

        students.forEach(student => {

            tbody.innerHTML += `
                <tr>
                    <td>${student.id}</td>
                    <td>${student.name}</td>
                    <td>${student.age}</td>
                    <td>${student.grade}</td>
                </tr>
            `;
        });

    } catch (error) {

        console.error(error);

        alert("Unable to reach the backend service.");
    }

}

window.onload = loadStudents;