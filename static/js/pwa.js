// ULC-ICAM PWA JavaScript
// © 2024 Cognito Inc. - Tous droits réservés

class ULCICAMPwa {
    constructor() {
        this.deferredPrompt = null;
        this.isInstalled = false;
        this.init();
    }

    init() {
        this.registerServiceWorker();
        this.setupInstallPrompt();
        this.setupNotifications();
        this.setupOfflineSync();
        this.checkInstallStatus();
    }

    // Enregistrement du Service Worker
    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/static/sw.js');
                console.log('[PWA] Service Worker enregistré:', registration);
                
                // Écouter les mises à jour
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            this.showUpdateNotification();
                        }
                    });
                });
            } catch (error) {
                console.error('[PWA] Erreur Service Worker:', error);
            }
        }
    }

    // Configuration de l'installation PWA
    setupInstallPrompt() {
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallButton();
        });

        window.addEventListener('appinstalled', () => {
            console.log('[PWA] App installée');
            this.isInstalled = true;
            this.hideInstallButton();
            this.showWelcomeMessage();
        });
    }

    // Afficher le bouton d'installation
    showInstallButton() {
        const installBtn = document.createElement('button');
        installBtn.id = 'pwa-install-btn';
        installBtn.innerHTML = '📱 Installer l\'app';
        installBtn.className = 'pwa-install-button';
        installBtn.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #2563eb;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 25px;
            font-size: 14px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
            z-index: 1000;
            transition: all 0.3s ease;
        `;
        
        installBtn.addEventListener('click', () => this.installApp());
        installBtn.addEventListener('mouseenter', () => {
            installBtn.style.transform = 'translateY(-2px)';
            installBtn.style.boxShadow = '0 6px 16px rgba(37, 99, 235, 0.4)';
        });
        installBtn.addEventListener('mouseleave', () => {
            installBtn.style.transform = 'translateY(0)';
            installBtn.style.boxShadow = '0 4px 12px rgba(37, 99, 235, 0.3)';
        });
        
        document.body.appendChild(installBtn);
    }

    // Masquer le bouton d'installation
    hideInstallButton() {
        const installBtn = document.getElementById('pwa-install-btn');
        if (installBtn) {
            installBtn.remove();
        }
    }

    // Installer l'application
    async installApp() {
        if (this.deferredPrompt) {
            this.deferredPrompt.prompt();
            const { outcome } = await this.deferredPrompt.userChoice;
            console.log('[PWA] Choix utilisateur:', outcome);
            this.deferredPrompt = null;
            this.hideInstallButton();
        }
    }

    // Vérifier si l'app est déjà installée
    checkInstallStatus() {
        // Vérifier si lancé depuis l'écran d'accueil
        if (window.matchMedia('(display-mode: standalone)').matches || 
            window.navigator.standalone === true) {
            this.isInstalled = true;
            console.log('[PWA] App lancée en mode standalone');
        }
    }

    // Configuration des notifications
    async setupNotifications() {
        if ('Notification' in window && 'serviceWorker' in navigator) {
            const permission = await Notification.requestPermission();
            if (permission === 'granted') {
                console.log('[PWA] Notifications autorisées');
            }
        }
    }

    // Configuration de la synchronisation hors ligne
    setupOfflineSync() {
        // Écouter les événements de connexion
        window.addEventListener('online', () => {
            console.log('[PWA] Connexion rétablie');
            this.hideOfflineIndicator();
        });

        window.addEventListener('offline', () => {
            console.log('[PWA] Connexion perdue');
            this.showOfflineIndicator();
        });

        // Vérifier l'état initial
        if (!navigator.onLine) {
            this.showOfflineIndicator();
        }
    }

    // Afficher l'indicateur hors ligne
    showOfflineIndicator() {
        let indicator = document.getElementById('offline-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'offline-indicator';
            indicator.innerHTML = '📡 Mode hors ligne';
            indicator.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: #f59e0b;
                color: white;
                text-align: center;
                padding: 8px;
                font-size: 14px;
                z-index: 9999;
                transform: translateY(-100%);
                transition: transform 0.3s ease;
            `;
            document.body.appendChild(indicator);
        }
        
        setTimeout(() => {
            indicator.style.transform = 'translateY(0)';
        }, 100);
    }

    // Masquer l'indicateur hors ligne
    hideOfflineIndicator() {
        const indicator = document.getElementById('offline-indicator');
        if (indicator) {
            indicator.style.transform = 'translateY(-100%)';
            setTimeout(() => indicator.remove(), 300);
        }
    }

    // Afficher notification de mise à jour
    showUpdateNotification() {
        const notification = document.createElement('div');
        notification.innerHTML = `
            <div style="
                position: fixed;
                bottom: 20px;
                left: 20px;
                background: #10b981;
                color: white;
                padding: 16px 20px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 1000;
                max-width: 300px;
            ">
                <div style="font-weight: 600; margin-bottom: 8px;">
                    🔄 Mise à jour disponible
                </div>
                <div style="font-size: 14px; margin-bottom: 12px;">
                    Une nouvelle version de l'application est disponible.
                </div>
                <button onclick="window.location.reload()" style="
                    background: rgba(255,255,255,0.2);
                    border: 1px solid rgba(255,255,255,0.3);
                    color: white;
                    padding: 6px 12px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 12px;
                ">
                    Actualiser
                </button>
            </div>
        `;
        document.body.appendChild(notification);
    }

    // Afficher message de bienvenue après installation
    showWelcomeMessage() {
        const welcome = document.createElement('div');
        welcome.innerHTML = `
            <div style="
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                text-align: center;
                z-index: 10000;
                max-width: 400px;
            ">
                <div style="font-size: 48px; margin-bottom: 16px;">🎉</div>
                <h3 style="color: #1f2937; margin-bottom: 12px;">
                    Bienvenue dans ULC Turnin !
                </h3>
                <p style="color: #6b7280; margin-bottom: 20px;">
                    L'application a été installée avec succès. Vous pouvez maintenant l'utiliser hors ligne !
                </p>
                <button onclick="this.parentElement.parentElement.remove()" style="
                    background: #2563eb;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    cursor: pointer;
                ">
                    Commencer
                </button>
            </div>
        `;
        document.body.appendChild(welcome);
        
        setTimeout(() => welcome.remove(), 5000);
    }
}

// Initialiser la PWA quand le DOM est prêt
document.addEventListener('DOMContentLoaded', () => {
    window.ulcIcamPwa = new ULCICAMPwa();
});

// Exporter pour utilisation globale
window.ULCICAMPwa = ULCICAMPwa;