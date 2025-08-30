document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('post-form');
    const status = document.getElementById('status');

    form.addEventListener('submit', (e) => {
        e.preventDefault();

        submit_true = confirm("are you sure?")
        if (submit_true) {
            const title = document.getElementById('title').value.trim();
            const content = document.getElementById('content').value.trim();

            if (title && content) {
                // Later, send via fetch to Flask backend
                console.log({ title, content });
                status.style.background = "#9ff087";
                status.style.display = "block";
                status.textContent = 'Post created successfully!';


                form.reset();
            } else {
                status.style.background = "#da2e0348";
                status.style.display = "block";
                status.textContent = 'Please fill in all fields!';
            }
        }else{
            console.log("cancel post")
            status.style.display = "none"
        }


    });
});
