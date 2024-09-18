document.addEventListener('DOMContentLoaded', function () {
    list_likes = document.querySelectorAll("#like_icon").forEach(icon => icon.addEventListener('click', (event) => like_post(event, icon.parentElement.id)))
    list_edit = document.querySelectorAll("#edit_post").forEach(button => button.addEventListener('click', (event) => enable_edit(event, button.dataset.postid)))
});

function like_post(event, post_id) {
    const like = event.target.getAttribute("fill") === 'white' || event.target.parentElement.getAttribute('fill') === 'white';
    let csrftoken = getCookie('csrftoken')
    let likes = parseInt(document.getElementById(`like_${post_id}`).innerHTML)
    if (like) {
        fetch('/like', {
            method: 'POST',
            body: JSON.stringify({
                "post_id": post_id,

            }),
            headers: { 'X-CSRFToken': csrftoken }
        }).then(response => {
            event.target.setAttribute("fill", "red")
            event.target.parentElement.setAttribute("fill", "red")
            likes = likes + 1
            document.getElementById(`like_${post_id}`).innerHTML = likes
        });
    } else {
        fetch('/like', {
            method: 'DELETE',
            body: JSON.stringify({
                "post_id": post_id,
            }),
            headers: { 'X-CSRFToken': csrftoken }
        }).then(response => {
            event.target.parentElement.setAttribute("fill", "white")
            if (event.target.hasAttribute("fill")) {
                event.target.setAttribute("fill", "white")
            }
            likes = likes - 1
            document.getElementById(`like_${post_id}`).innerHTML = likes
        })
    }

    feather.replace();

}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function enable_edit(event, post_id) {
    document.querySelectorAll("#edit_post").forEach(button => button.setAttribute("hidden", "true"))
    const text = document.querySelector(`#text-${post_id}`);
    const container = document.createElement("div");
    const text_area = document.createElement("textarea");
    text_area.setAttribute("class", "form-control");
    text_area.setAttribute("rows", 2);
    text_area.setAttribute("maxlength", 200);
    text_area.setAttribute("id", `text-area-${post_id}`);
    text_area.innerText = text.innerText;
    const cancel = document.createElement("button");
    cancel.setAttribute("class", "btn btn-danger btn-sm mt-1");
    cancel.setAttribute("id", "cancel")
    cancel.innerHTML = "Cancel"

    const save = document.createElement("button");
    save.setAttribute("class", "btn btn-primary btn-sm mt-1");
    save.setAttribute("id", "save")
    save.innerHTML = "Save"

    const box = document.createElement("div");
    box.setAttribute("class", "box");
    box.appendChild(cancel);
    box.appendChild(save);
    container.appendChild(text_area);
    container.appendChild(box);

    text.innerHTML = ""
    text.append(container)
    cancel.addEventListener('click', () => load_post(post_id));
    save.addEventListener('click', (event) => save_post(post_id));
}

function load_post(post_id) {
    const csrftoken = getCookie('csrftoken')
    fetch(`/post/${post_id}`, {
        method: 'GET',
        headers: { 'X-CSRFToken': csrftoken }
    }).then(response => response.json()).then(response => {
        const text = document.querySelector(`#text-${post_id}`);
        const post = document.createElement("p")
        post.setAttribute("class", "card-text")
        post.innerText = response.text
        text.innerHTML = post.outerHTML
        document.querySelectorAll("#edit_post").forEach(button => button.removeAttribute("hidden"))
    });
}
function save_post(post_id) {
    const csrftoken = getCookie('csrftoken')
    post_text = document.querySelector(`#text-area-${post_id}`).value;
    fetch(`/post/${post_id}`, {
        method: 'PUT',
        body: JSON.stringify({ "text": post_text }),
        headers: { 'X-CSRFToken': csrftoken }
    }).then(response => {
        load_post(post_id)
    });
}