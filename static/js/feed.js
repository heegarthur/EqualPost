// Placeholder feed data, later filled by Flask API
let posts = [
    { title: "Stay active", content: "A little daily exercise keeps you healthy and sharp." },
    { title: "Read daily", content: "Reading daily expands your knowledge and perspective." }
];

function renderFeed() {
    const container = document.getElementById('feed-container');
    container.innerHTML = '';

    posts.forEach(post => {
        const postDiv = document.createElement('div');
        const h3 = document.createElement('h3');
        h3.textContent = post.title;
        const p = document.createElement('p');
        p.textContent = post.content;

        postDiv.appendChild(h3);
        postDiv.appendChild(p);
        container.appendChild(postDiv);
    });
}

document.addEventListener('DOMContentLoaded', renderFeed);
