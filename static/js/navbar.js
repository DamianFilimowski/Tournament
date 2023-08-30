const loginButton = document.getElementById('login')
const joinButton = document.getElementById('register')
const profileButton = document.getElementById('profile-button')
const logoutButton = document.getElementById('logout-button')
if (loginButton!==null){
    loginButton.addEventListener("click", function() {
            window.location.href = "/accounts/login";
        });

joinButton.addEventListener("click", function() {
            window.location.href = "/accounts/register";
        });
}

profileButton.addEventListener("click", function() {
            window.location.href = "/accounts/profile";
        });

logoutButton.addEventListener("click", function() {
            window.location.href = "/accounts/logout";
        });