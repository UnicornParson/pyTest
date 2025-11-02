//const { createApp } = Vue;

createApp({
    data() {
        return {
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
}).mount('#content');