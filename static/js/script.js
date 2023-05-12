const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    if(scrollY >= 40){
        navbar.classList.add('bg');
    } else{
        navbar.classList.remove('bg');
    }
})

const resp = document.querySelector('.resp');
const linkscontainer = document.querySelector('.links-container');

resp.addEventListener('click', () => {
    resp.classList.toggle('active');
    linkscontainer.classList.toggle('active');
})

document.querySelectorAll('.link-item').forEach(n => n.
    addEventListener('click', () => {
        resp.classList.remove('active');
        linkscontainer.classList.remove('active');
    }))



let output = document.getElementById('dd');
let dropdownList = document.getElementById("alarm");
let dropdownList2 = document.getElementById("profile");
dropdownList.style.display = "none";
dropdownList2.style.display = "none";
function openDropdown() {
    if (dropdownList.style.display != "none") {
        dropdownList.style.display = "none";
    }
    else {
          dropdownList.style.display = "block";
    }
}
function openDropdown2() {
    if (dropdownList2.style.display != "none") {
        dropdownList2.style.display = "none";
    }
    else {
        dropdownList2.style.display = "block";
    }
}

const inputs = document.querySelectorAll(".a-input");

function focusFunc(){
    let parent = this.parentNode;
    parent.classList.add("focus");
}

function blurFunc(){
    let parent = this.parentNode;
    if(this.value == ""){
        parent.classList.remove("focus");
    }
}

inputs.forEach((input) => {
    input.addEventListener("focus", focusFunc);
    input.addEventListener("blur", blurFunc);
})


let modal = document.getElementById('contact-modal'),
    openModal = document.getElementById('edit'),
    closeModal = document.querySelector('.close-modal');

openModal.addEventListener('click', function(){
  modal.style.display = 'block';
})
closeModal.addEventListener('click', function(){
  modal.style.display = 'none'
})

window.addEventListener('click', function(e){
    if(e.target == modal){
      modal.style.display = 'none';
    }
})


