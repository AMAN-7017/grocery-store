

// -------------------Alerts--------------------

function alert_cate(){
    alert('Are you sure you want to delete this category? All products associated with this category will also be deleted')
}

function alert_prod(){
    alert('Are you sure you want to delete this products?')
}

// --------------------User info-----------------------

const user = document.querySelector('.user');
const user_info = document.querySelector('.user_info');

user.addEventListener('click',()=>{
    user_info.classList.toggle('show_user_info')
}) 














// ---------------------User Validation---------------------

function seterror(id, error) {
    var input = document.getElementById(id);
    var small = input.parentElement.children[2];
    small.innerHTML = '<i class="bi me-1 bi-exclamation-circle-fill"></i>' + error
    var span = input.parentElement.children[1];
    span.style.color = "#dc3545"
    input.classList.add('invalid')
}

function unseterror(id) {
    var input = document.getElementById(id);
    var small = input.parentElement.children[2];
    small.innerHTML = ''
    var span = input.parentElement.children[1];
    span.style.color = "blueviolet"
    input.classList.remove('invalid')
}




function validation_email() {
    var email_error = document.getElementById('email_error');
    var email = document.getElementById('email').value;
    if (email.length == 0) {
        seterror('email', 'Please fill out the email!');
        return false;
    }
    if (!email.match(/^[a0-z9]+@[a0-z9]+\.com$/)) {
        seterror('email', ' Invalid email!');
        return false;
    }
    unseterror('email')
    return true;
}


function validation_pass() {
    var pass_error = document.getElementById('pass_error');
    var pass = document.getElementById('pass').value;
    console.log(pass)
    if (pass.length == 0) {
        seterror('pass', 'Please fill out the password!')
        return false;
    }
    if (pass.length < 6) {
        seterror('pass', 'Password must be atleast 6 charecters!')
        return false;
    }
    if (pass.length > 15) {
        seterror('pass', 'Password must be atmost 15 charecters!')
        return false;
    }
    unseterror('pass')
    return true;
}


function validation() {
    if (validation_email() == true && validation_pass() == true) {
        return true
    }
    return false
}
