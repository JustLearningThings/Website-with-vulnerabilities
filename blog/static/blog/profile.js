let posts = document.getElementById('posts-dropdown-content')
let dropdown = document.getElementById('posts-dropdown')
let dropdownIcon = document.getElementById('dropdown-icon')

if (dropdown) dropdown.onclick = () => {
    posts.classList.toggle('hidden')
    dropdownIcon.classList.toggle('dropdown-icon-active')
}
