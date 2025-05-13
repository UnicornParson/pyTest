
document.addEventListener('DOMContentLoaded', function() {
    const resizer = document.querySelector('.terminal-resizer');
    const terminalContainer = document.querySelector('.terminal-container');
    let isResizing = false;
    let startY, startHeight;

    resizer.addEventListener('mousedown', function(e) {
        isResizing = true;
        startY = e.clientY;
        startHeight = parseInt(document.defaultView.getComputedStyle(terminalContainer).height, 10);
        e.preventDefault(); // Prevent text selection
    });

    document.addEventListener('mousemove', function(e) {
        if (!isResizing) return;
        const deltaY = startY - e.clientY;
        terminalContainer.style.height = (startHeight + deltaY) + 'px';
    });

    document.addEventListener('mouseup', function() {
        isResizing = false;
    });
});

const { createApp } = Vue;

createApp({
    data() {
        return {
            logo: 'Project',
            title: 'Unicorn Tool',
            content: ''
        };
    },
    mounted() {
        fetch('/api/v1/project')
            .then(response => response.json())
            .then(data => {
                this.logo = data.project_name;
                this.title = "Unicorn Tool:" + data.project_name;
                this.content = `Hello from ${data.project_name}`;
            })
            .catch(error => console.error('Error fetching project name:', error));
    }
}).mount('#app');