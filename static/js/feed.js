const API_URL = "http://127.0.0.1:5000/api/feed";
let offset = 0;
const limit = 10;
let loading = false;
let allLoaded = false;

async function loadFeed() {
    if (loading || allLoaded) return;
    loading = true;

    try {
        const response = await fetch(`${API_URL}?limit=${limit}&offset=${offset}`);
        const posts = await response.json();

        if (posts.length === 0) {
            allLoaded = true;
            return;
        }

        const container = document.getElementById('feed-container');

        posts.forEach(post => {
            const postDiv = document.createElement('div');
            postDiv.style.border = "1px solid #ccc";
            postDiv.style.margin = "10px";
            postDiv.style.padding = "10px";
            postDiv.style.borderRadius = "5px";

            const h3 = document.createElement('h3');
            h3.textContent = post.title;
            const p = document.createElement('p');
            p.textContent = post.content;

            const small = document.createElement('small');
            small.textContent = `Posted on: ${new Date(post.created_at).toLocaleString()}`;

            postDiv.appendChild(h3);
            postDiv.appendChild(p);
            postDiv.appendChild(small);

            container.appendChild(postDiv);
        });

        offset += posts.length;
        loading = false;
    } catch (err) {
        console.error("Failed to load feed:", err);
        loading = false;
    }
}

window.addEventListener("scroll", () => {
    if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 100) {
        loadFeed();
    }
});

document.addEventListener('DOMContentLoaded', loadFeed);
