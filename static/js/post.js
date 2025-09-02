document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('post-form');
    const status = document.getElementById('status');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submit_true = confirm("Are you sure?");
        if (!submit_true) {
            console.log("cancel post");
            status.style.display = "none";
            return;
        }
        const title = document.getElementById('title').value.trim();
        const content = document.getElementById('content').value.trim();
        if (title && content) {
            try {
                const response = await fetch("http://127.0.0.1:5000/api/posts", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ title, content })
                });
                const result = await response.json();
                status.style.display = "block";
                if (result.status === "approved") {
                    status.style.background = "#9ff087";
                    status.textContent = result.message;
                    form.reset();
                } else if (result.status === "rejected") {
                    status.style.background = "#da2e0348";
                    status.textContent = "❌ " + result.reason;
                } else {
                    status.style.background = "#da2e0348";
                    status.textContent = "⚠️ " + result.reason;
                }
            } catch (err) {
                console.error(err);
                status.style.background = "#da2e0348";
                status.style.display = "block";
                status.textContent = 'Error connecting to server!';
            }
        } else {
            status.style.background = "#da2e0348";
            status.style.display = "block";
            status.textContent = 'Please fill in all fields!';
        }

    });
});
