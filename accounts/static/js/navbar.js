const loginButton = document.querySelector(".login-button");
const joinButton = document.querySelector(".join-button");

loginButton.addEventListener("click", function() {
            window.location.href = "/accounts/login";
        });

joinButton.addEventListener("click", function() {
            window.location.href = "/accounts/register";
        });