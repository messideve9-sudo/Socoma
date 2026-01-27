// Fonctions utilitaires
function formatCFA(amount) {
    return new Intl.NumberFormat('fr-FR').format(Math.round(amount)) + ' FCFA';
}

function formatDate(date) {
    if (!date) return '';
    return new Date(date).toLocaleDateString('fr-FR');
}

// Gestion des filtres
function applyFilters() {
    const commercial = document.getElementById('filterCommercial')?.value;
    const statut = document.getElementById('filterStatut')?.value;
    const client = document.getElementById('filterClient')?.value;
    
    const params = new URLSearchParams();
    if (commercial) params.append('commercial', commercial);
    if (statut) params.append('statut', statut);
    if (client) params.append('client', client);
    
    window.location.search = params.toString();
}

function resetFilters() {
    window.location.search = '';
}

// Tri des tables
function sortTable(columnIndex) {
    const table = document.querySelector('table');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    const isAscending = table.dataset.sortColumn === columnIndex.toString() 
        ? table.dataset.sortOrder === 'desc'
        : true;
    
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        
        // Essayer de convertir en nombre
        const aNum = parseFloat(aValue.replace(/[^\d.-]/g, ''));
        const bNum = parseFloat(bValue.replace(/[^\d.-]/g, ''));
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAscending ? aNum - bNum : bNum - aNum;
        }
        
        // Sinon tri alphabétique
        return isAscending 
            ? aValue.localeCompare(bValue, 'fr')
            : bValue.localeCompare(aValue, 'fr');
    });
    
    // Réorganiser les lignes
    rows.forEach(row => tbody.appendChild(row));
    
    // Mettre à jour les indicateurs de tri
    table.dataset.sortColumn = columnIndex;
    table.dataset.sortOrder = isAscending ? 'asc' : 'desc';
}

// Confirmation de suppression
function confirmDelete(message) {
    return confirm(message || 'Êtes-vous sûr de vouloir supprimer cet élément ? Cette action est irréversible.');
}

// Calculatrice de montants
function calculerSolde() {
    const montant = parseFloat(document.getElementById('montant')?.value) || 0;
    const versement = parseFloat(document.getElementById('versement')?.value) || 0;
    const solde = montant - versement;
    
    const soldeElement = document.getElementById('solde_calcule');
    if (soldeElement) {
        soldeElement.textContent = formatCFA(solde);
    }
}

// Gestion des dates
function calculerDateEcheance() {
    const dateFacturation = document.getElementById('date_facturation')?.value;
    const dateEcheance = document.getElementById('date_echeance');
    
    if (dateFacturation && dateEcheance) {
        const date = new Date(dateFacturation);
        date.setDate(date.getDate() + 10); // 10 jours après
        dateEcheance.value = date.toISOString().split('T')[0];
    }
}

// Mode sombre/clair
function toggleTheme() {
    const body = document.body;
    const currentTheme = localStorage.getItem('theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Mettre à jour l'icône
    const themeIcon = document.getElementById('themeIcon');
    if (themeIcon) {
        themeIcon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

// Initialisation du thème
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.setAttribute('data-theme', savedTheme);
    
    // Ajouter le bouton de thème si non présent
    if (!document.getElementById('themeToggle')) {
        const themeToggle = document.createElement('button');
        themeToggle.id = 'themeToggle';
        themeToggle.className = 'btn btn-small btn-light';
        themeToggle.innerHTML = '<i id="themeIcon" class="fas fa-moon"></i>';
        themeToggle.onclick = toggleTheme;
        
        const userInfo = document.querySelector('.user-info');
        if (userInfo) {
            userInfo.insertBefore(themeToggle, userInfo.firstChild);
        }
        
        // Mettre à jour l'icône
        const themeIcon = document.getElementById('themeIcon');
        if (themeIcon && savedTheme === 'dark') {
            themeIcon.className = 'fas fa-sun';
        }
    }
}

// Export en PDF
function exportToPDF() {
    alert('Fonctionnalité d\'export PDF à implémenter');
    // À implémenter avec une bibliothèque comme jsPDF
}

// Recherche en temps réel
function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const table = document.querySelector('table');
        if (!table) return;
        
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });
}

// Validation des formulaires
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.style.borderColor = '#e74c3c';
            isValid = false;
        } else {
            field.style.borderColor = '';
        }
    });
    
    if (!isValid) {
        alert('Veuillez remplir tous les champs obligatoires.');
    }
    
    return isValid;
}

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser le thème
    initTheme();
    
    // Configurer la recherche
    setupSearch();
    
    // Mettre à jour la date et l'heure
    function updateDateTime() {
        const now = new Date();
        const dateTimeElements = document.querySelectorAll('.current-datetime');
        dateTimeElements.forEach(el => {
            el.textContent = now.toLocaleString('fr-FR', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        });
    }
    
    updateDateTime();
    setInterval(updateDateTime, 60000); // Mettre à jour toutes les minutes
    
    // Ajouter des événements aux boutons de tri
    const sortableHeaders = document.querySelectorAll('th[data-sortable]');
    sortableHeaders.forEach((th, index) => {
        th.style.cursor = 'pointer';
        th.addEventListener('click', () => sortTable(index));
    });
    
    // Gestion des onglets
    const tabs = document.querySelectorAll('.tab-button');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const tabId = this.dataset.tab;
            
            // Désactiver tous les onglets
            tabs.forEach(t => t.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            // Activer l'onglet courant
            this.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // Calculer les soldes initiaux
    calculerSolde();
    
    // Initialiser les datepickers
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (!input.value) {
            input.value = new Date().toISOString().split('T')[0];
        }
    });
    
    // Notifications
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
});

// Service Worker pour PWA
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js').then(
            function(registration) {
                console.log('ServiceWorker registration successful');
            },
            function(err) {
                console.log('ServiceWorker registration failed: ', err);
            }
        );
    });
}

// Mode hors ligne
window.addEventListener('online', function() {
    document.body.classList.remove('offline');
    showToast('Connexion rétablie', 'success');
});

window.addEventListener('offline', function() {
    document.body.classList.add('offline');
    showToast('Mode hors ligne activé', 'warning');
});

// Toast notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : '#3498db'};
        color: white;
        border-radius: 10px;
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// CSS pour les animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    body[data-theme="dark"] {
        background: #1a1a2e;
        color: #e6e6e6;
    }
    
    body[data-theme="dark"] .content {
        background: #16213e;
        color: #e6e6e6;
    }
    
    body[data-theme="dark"] .card {
        background: #0f3460;
        border-color: #1a1a2e;
    }
    
    body[data-theme="dark"] table {
        background: #0f3460;
    }
    
    body[data-theme="dark"] th {
        background: #16213e;
        color: #e6e6e6;
    }
    
    body[data-theme="dark"] td {
        color: #e6e6e6;
        border-color: #1a1a2e;
    }
    
    .offline {
        filter: grayscale(1);
    }
    
    .offline::before {
        content: '⚫ Mode hors ligne';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: #f39c12;
        color: white;
        text-align: center;
        padding: 10px;
        z-index: 9999;
        font-weight: bold;
    }
`;
document.head.appendChild(style);