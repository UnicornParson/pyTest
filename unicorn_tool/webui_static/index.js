
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
            content: '',
            summary_project_name: '',
            summary_project_src: '',
            summary_project_lang: '',
            summary_project_ctag: '',
            summary_project_lastindex: '',
            summary_can_run_ctag: false,
            summary_ctag_btn_class: "tags" 
        };
    },
    mounted() {
        this.fetchSummary();
        this.startPolling();
    },
    methods: {
        fetchSummary() {
            fetch('/api/v1/project')
                .then(response => response.json())
                .then(data => {
                    this.logo = data.project_name;
                    this.title = "Unicorn Tool:" + data.project_name;
                    this.summary_project_name = data.project_name;
                    this.summary_project_src = data.source;
                    this.summary_project_lang = data.lang;
                    this.summary_project_ctag = data.ctags_state;
                    this.summary_can_run_ctag = (data.ctags_state === "Idle")
                    this.summary_project_lastindex = data.last_indexed;
                    this.summary_ctag_btn_class = this.summary_can_run_ctag ? "btn_enabled": "btn_disabled";   
                })
                .catch(error => console.error('Error fetching project name:', error));
        },
        runCtags() {
            if (!(this.summary_can_run_ctag && (this.summary_project_ctag === "Idle")))
            {
                // just ignore
                //alert("ctag not ready. state: " + this.summary_project_ctag);
                return;
            }
            fetch('/api/v1/act?act=run_ctags')
                .then(response => response.json())
                .then(data => console.log('CTags started:', data))
                .catch(error => console.error('Error starting CTags:', error));
        },
        startPolling() {
            this.pollInterval = setInterval(() => {

                this.fetchSummary();
            }, 1000);
        }
    }
}).mount('#app');



createApp({
    data() {
        return {
            terminalContent: 'term',
        };
    },
    mounted() {
        this.fetchConsole();
        this.startPolling();
    },
    methods: {
        fetchSummary() {
            fetch('/api/v1/project')
                .then(response => response.json())
                .then(data => {
                    //this.logo = data.project_name;
                    this.title = "Unicorn Tool:" + data.project_name;
                    this.content = `Hello from ${data.project_name}`;
                })
                .catch(error => console.error('Error fetching project name:', error));
        },
        highlightCode() {
            document.addEventListener('DOMContentLoaded', (event) => {
                document.querySelectorAll('code').forEach((el) => {
                  hljs.highlightElement(el);
                });
              });
        },
        fetchConsole() {
            fetch('/api/v1/console')
                .then(response => response.text())
                .then(data => {
                    this.terminalContent = data; 
                    hljs.highlightAll();
                    this.highlightCode();
                })
                .catch(error => console.error('Error:', error));
            
        },
        
        startPolling() {
            this.pollInterval = setInterval(() => {
                this.fetchConsole();
            }, 1000);
        }
    }
}).mount('#terminal-container');