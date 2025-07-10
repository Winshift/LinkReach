// LinkedIn Connections Filter - Frontend Application
class LinkedInFilterApp {
    constructor() {
        this.currentFile = null;
        this.apiBaseUrl = '/api';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
    }

    setupEventListeners() {
        // File input change
        document.getElementById('fileInput').addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files[0]);
        });

        // Enter key in prompt
        document.getElementById('promptInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                this.filterConnections();
            }
        });
    }

    setupDragAndDrop() {
        const uploadArea = document.getElementById('uploadArea');
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.add('dragover');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.remove('dragover');
            });
        });

        uploadArea.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        });
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    async handleFileSelect(file) {
        if (!file) return;

        if (!file.name.toLowerCase().endsWith('.csv')) {
            this.showToast('Please select a CSV file', 'error');
            return;
        }

        this.currentFile = file;
        this.updateFileInfo(file);
        
        try {
            this.showLoading('Uploading file...');
            await this.uploadFile(file);
            this.showToast('File uploaded successfully!', 'success');
            this.showFilterSection();
        } catch (error) {
            this.showToast(`Upload failed: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    updateFileInfo(file) {
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');

        fileName.textContent = file.name;
        fileSize.textContent = this.formatFileSize(file.size);
        fileInfo.style.display = 'flex';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${this.apiBaseUrl}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        const result = await response.json();
        return result;
    }

    showFilterSection() {
        document.getElementById('uploadSection').style.display = 'none';
        document.getElementById('filterSection').style.display = 'block';
    }

    async filterConnections() {
        const prompt = document.getElementById('promptInput').value.trim();
        
        if (!prompt) {
            this.showToast('Please enter a filter prompt', 'error');
            return;
        }

        try {
            this.showLoading('Generating filter code...');
            
            const response = await fetch(`${this.apiBaseUrl}/filter`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Filtering failed');
            }

            const result = await response.json();
            this.showResults(result);
            this.showToast('Filtering completed successfully!', 'success');
            
        } catch (error) {
            this.showToast(`Filtering failed: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    showResults(result) {
        const resultsSection = document.getElementById('resultsSection');
        const resultsSummary = document.getElementById('resultsSummary');
        const resultsPreview = document.getElementById('resultsPreview');
        const downloadBtn = document.getElementById('downloadBtn');

        // Update summary
        resultsSummary.innerHTML = `
            <i class="fas fa-users"></i>
            Found ${result.filtered_count} connections out of ${result.total_count} total
        `;

        // Update preview
        if (result.preview_data && result.preview_data.length > 0) {
            const table = this.createResultsTable(result.preview_data);
            resultsPreview.innerHTML = '';
            resultsPreview.appendChild(table);
        } else {
            resultsPreview.innerHTML = '<p>No results to display</p>';
        }

        // Update download button
        if (result.download_url) {
            downloadBtn.onclick = () => this.downloadResults(result.download_url);
            downloadBtn.style.display = 'inline-flex';
        } else {
            downloadBtn.style.display = 'none';
        }

        // Show results section
        document.getElementById('filterSection').style.display = 'none';
        resultsSection.style.display = 'block';
    }

    createResultsTable(data) {
        const table = document.createElement('table');
        table.style.width = '100%';
        table.style.borderCollapse = 'collapse';
        table.style.fontSize = '0.9rem';

        // Create header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        
        Object.keys(data[0]).forEach(key => {
            const th = document.createElement('th');
            th.textContent = key;
            th.style.padding = '0.75rem';
            th.style.textAlign = 'left';
            th.style.borderBottom = '2px solid #e2e8f0';
            th.style.backgroundColor = '#f7fafc';
            th.style.fontWeight = '600';
            headerRow.appendChild(th);
        });
        
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Create body
        const tbody = document.createElement('tbody');
        data.forEach(row => {
            const tr = document.createElement('tr');
            Object.values(row).forEach(value => {
                const td = document.createElement('td');
                td.textContent = value || '';
                td.style.padding = '0.75rem';
                td.style.borderBottom = '1px solid #e2e8f0';
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        
        table.appendChild(tbody);
        return table;
    }

    async downloadResults(downloadUrl) {
        try {
            const response = await fetch(downloadUrl);
            if (!response.ok) throw new Error('Download failed');
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'filtered_connections.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            this.showToast('Download started!', 'success');
        } catch (error) {
            this.showToast(`Download failed: ${error.message}`, 'error');
        }
    }

    resetApp() {
        this.currentFile = null;
        document.getElementById('fileInput').value = '';
        document.getElementById('promptInput').value = '';
        document.getElementById('fileInfo').style.display = 'none';
        document.getElementById('uploadSection').style.display = 'block';
        document.getElementById('filterSection').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'none';
    }

    showLoading(message = 'Processing...') {
        document.getElementById('loadingMessage').textContent = message;
        document.getElementById('loadingOverlay').style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = document.createElement('i');
        icon.className = this.getToastIcon(type);
        
        const text = document.createElement('span');
        text.textContent = message;
        
        toast.appendChild(icon);
        toast.appendChild(text);
        container.appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }

    getToastIcon(type) {
        switch (type) {
            case 'success': return 'fas fa-check-circle';
            case 'error': return 'fas fa-exclamation-circle';
            default: return 'fas fa-info-circle';
        }
    }
}

// Global functions for HTML onclick handlers
function removeFile() {
    app.currentFile = null;
    document.getElementById('fileInput').value = '';
    document.getElementById('fileInfo').style.display = 'none';
}

function filterConnections() {
    app.filterConnections();
}

function downloadResults() {
    // This will be set by the results
}

function resetApp() {
    app.resetApp();
}

function toggleHelp() {
    const helpSection = document.getElementById('helpSection');
    const showInstructionsSection = document.getElementById('showInstructionsSection');
    const button = event.target.closest('button');
    const icon = button.querySelector('i');
    const text = button.querySelector('span');
    
    if (helpSection.style.display === 'none') {
        // Show instructions
        helpSection.style.display = 'block';
        showInstructionsSection.style.display = 'none';
        icon.className = 'fas fa-eye-slash';
        text.textContent = 'Hide Instructions';
    } else {
        // Hide instructions
        helpSection.style.display = 'none';
        showInstructionsSection.style.display = 'block';
        icon.className = 'fas fa-eye';
        text.textContent = 'Show Instructions';
    }
}

// Initialize the application
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new LinkedInFilterApp();
}); 