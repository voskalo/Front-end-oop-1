const form = document.getElementById("register-form");

form.addEventListener("submit", function (event) {
    event.preventDefault();

    const username = document.getElementById("nickname").value;
    const password = document.getElementById("password").value;

    fetch("http://localhost:8000/user", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(response => {
        if (response.ok) {
            // якщо сервер відповів 200
            window.location.href = "success.html";
        } else {
            alert("Помилка ❌");
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Сервер недоступний");
    });
});
