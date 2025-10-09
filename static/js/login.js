   // Configuration Toastify personnalisée
        const toastConfig = {
            duration: 4000,
            close: true,
            gravity: "top",
            position: "right",
            stopOnFocus: true,
            style: {
                borderRadius: "12px",
                padding: "16px 20px",
                fontSize: "14px",
                fontWeight: "500",
            }
        };

        // Classe pour gérer les notifications
        class NotificationManager {
            static showSuccess(message) {
                Toastify({
                    text: `✅ ${message}`,
                    backgroundColor: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
                    ...toastConfig
                }).showToast();
            }

            static showError(message) {
                Toastify({
                    text: `❌ ${message}`,
                    backgroundColor: "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)",
                    ...toastConfig
                }).showToast();
            }

            static showInfo(message) {
                Toastify({
                    text: `ℹ️ ${message}`,
                    backgroundColor: "linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)",
                    ...toastConfig
                }).showToast();
            }

            static showWarning(message) {
                Toastify({
                    text: `⚠️ ${message}`,
                    backgroundColor: "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
                    ...toastConfig
                }).showToast();
            }
        }

        // Classe pour gérer les modales
        class ModalManager {
            constructor() {
                this.activeModal = null;
                this.initEventListeners();
            }

            showModal(modalId) {
                const modal = document.getElementById(modalId);
                if (!modal) return;

                modal.classList.remove('invisible', 'opacity-0');
                modal.querySelector('div').classList.remove('scale-95');
                modal.querySelector('div').classList.add('scale-100');
                document.body.style.overflow = 'hidden';
                this.activeModal = modalId;
            }

            hideModal(modalId) {
                const modal = document.getElementById(modalId);
                if (!modal) return;

                modal.classList.add('opacity-0');
                modal.querySelector('div').classList.remove('scale-100');
                modal.querySelector('div').classList.add('scale-95');
                
                setTimeout(() => {
                    modal.classList.add('invisible');
                    document.body.style.overflow = 'auto';
                    this.activeModal = null;
                }, 300);
            }

            switchModal(from, to) {
                this.hideModal(from);
                setTimeout(() => this.showModal(to), 300);
            }

            initEventListeners() {
                // Close buttons
                document.getElementById('closeLoginModal')?.addEventListener('click', () => this.hideModal('loginModal'));
                document.getElementById('closeRegisterModal')?.addEventListener('click', () => this.hideModal('registerModal'));
                
                // Switch modals
                document.getElementById('showRegisterModal')?.addEventListener('click', () => this.switchModal('loginModal', 'registerModal'));
                document.getElementById('showLoginModal')?.addEventListener('click', () => this.switchModal('registerModal', 'loginModal'));

                // Close on outside click
                document.getElementById('loginModal')?.addEventListener('click', (e) => {
                    if (e.target === e.currentTarget) this.hideModal('loginModal');
                });
                
                document.getElementById('registerModal')?.addEventListener('click', (e) => {
                    if (e.target === e.currentTarget) this.hideModal('registerModal');
                });

                // ESC key to close
                document.addEventListener('keydown', (e) => {
                    if (e.key === 'Escape' && this.activeModal) {
                        this.hideModal(this.activeModal);
                    }
                });
            }
        }

        // Classe pour la validation des formulaires
        class FormValidator {
            static validateEmail(email) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                return emailRegex.test(email);
            }

            static validatePassword(password) {
                const minLength = password.length >= 8;
                const hasLower = /[a-z]/.test(password);
                const hasUpper = /[A-Z]/.test(password);
                const hasNumber = /[0-9]/.test(password);
                const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);

                return {
                    isValid: minLength && hasLower && (hasUpper || hasNumber || hasSpecial),
                    strength: this.calculatePasswordStrength(password),
                    feedback: this.getPasswordFeedback(password)
                };
            }

            static calculatePasswordStrength(password) {
                let strength = 0;
                if (password.length >= 8) strength += 25;
                if (/[a-z]/.test(password)) strength += 25;
                if (/[A-Z]/.test(password)) strength += 25;
                if (/[0-9]/.test(password) || /[^A-Za-z0-9]/.test(password)) strength += 25;
                return strength;
            }

            static getPasswordFeedback(password) {
                if (password.length === 0) return { text: 'Choisissez un mot de passe fort', class: 'text-gray-400' };
                if (password.length < 8) return { text: 'Au moins 8 caractères requis', class: 'text-red-400' };
                
                const strength = this.calculatePasswordStrength(password);
                if (strength <= 50) return { text: 'Faible', class: 'text-red-400' };
                if (strength <= 75) return { text: 'Moyen', class: 'text-yellow-400' };
                return { text: 'Fort', class: 'text-emerald-400' };
            }

            static getStrengthBarClass(strength) {
                if (strength === 0) return 'h-1 bg-gray-400 rounded-full transition-all duration-300';
                if (strength <= 50) return 'h-1 bg-red-500 rounded-full transition-all duration-300';
                if (strength <= 75) return 'h-1 bg-yellow-500 rounded-full transition-all duration-300';
                return 'h-1 bg-emerald-500 rounded-full transition-all duration-300';
            }
        }

        // Classe pour gérer l'authentification
        class AuthManager {
            constructor() {
                this.loginForm = document.getElementById('loginForm');
                this.registerForm = document.getElementById('registerForm');
                this.initEventListeners();
                this.initPasswordFeatures();
            }

            async login(credentials) {
                try {
                    // Simulation d'une requête API - remplacez par votre endpoint Django
                    NotificationManager.showInfo("Connexion en cours...");
                    
                    // Ici vous feriez appel à votre API Django
                    const response = await this.simulateApiCall('/api/login/', credentials);
                    
                    if (response.success) {
                        NotificationManager.showSuccess("Connexion réussie ! Bienvenue !");
                        modalManager.hideModal('loginModal');
                        
                        // Redirection après succès
                        setTimeout(() => {
                            // window.location.href = '/dashboard/';
                            console.log('Redirection vers le dashboard...');
                        }, 1500);
                        
                        return { success: true };
                    } else {
                        NotificationManager.showError(response.error || "Identifiants invalides");
                        return { success: false, error: response.error };
                    }
                } catch (error) {
                    NotificationManager.showError("Erreur de connexion. Veuillez réessayer.");
                    console.error('Login error:', error);
                    return { success: false, error: error.message };
                }
            }

            async register(userData) {
                try {
                    NotificationManager.showInfo("Création du compte en cours...");
                    
                    // Ici vous feriez appel à votre API Django
                    const response = await this.simulateApiCall('/api/register/', userData);
                    
                    if (response.success) {
                        NotificationManager.showSuccess("Compte créé avec succès ! Vous pouvez maintenant vous connecter.");
                        modalManager.hideModal('registerModal');
                        
                        // Optionnel: ouvrir automatiquement la modal de connexion
                        setTimeout(() => {
                            modalManager.showModal('loginModal');
                        }, 1000);
                        
                        return { success: true };
                    } else {
                        NotificationManager.showError(response.error || "Erreur lors de la création du compte");
                        return { success: false, error: response.error };
                    }
                } catch (error) {
                    NotificationManager.showError("Erreur lors de l'inscription. Veuillez réessayer.");
                    console.error('Register error:', error);
                    return { success: false, error: error.message };
                }
            }

            // Simulation d'appel API - remplacez par de vrais appels fetch()
            async simulateApiCall(endpoint, data) {
                return new Promise((resolve) => {
                    setTimeout(() => {
                        // Simulation de validation
                        if (endpoint === '/api/login/') {
                            // Simule une connexion réussie si email contient "test"
                            if (data.email.includes('test')) {
                                resolve({ success: true, user: { email: data.email } });
                            } else {
                                resolve({ success: false, error: "Email ou mot de passe incorrect" });
                            }
                        } else if (endpoint === '/api/register/') {
                            // Simule une inscription réussie si l'email est unique
                            if (data.email === 'admin@test.com') {
                                resolve({ success: false, error: "Cette adresse email est déjà utilisée" });
                            } else {
                                resolve({ success: true, user: { id: 1, email: data.email, full_name: data.full_name } });
                            }
                        }
                    }, 1500); // Simule une latence réseau
                });
            }

            // Vraie implémentation pour Django (commentée)
            /*
            async makeApiCall(endpoint, data) {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCsrfToken()
                    },
                    body: JSON.stringify(data)
                });
                
                return await response.json();
            }

            getCsrfToken() {
                return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
            }
            */

            initEventListeners() {
                // Gestion du formulaire de connexion
                this.loginForm?.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    
                    const formData = new FormData(this.loginForm);
                    const credentials = {
                        email: formData.get('email'),
                        password: formData.get('password'),
                        remember_me: formData.get('remember_me') === 'on'
                    };

                    // Validation côté client
                    if (!FormValidator.validateEmail(credentials.email)) {
                        NotificationManager.showWarning("Veuillez saisir une adresse email valide");
                        return;
                    }

                    if (credentials.password.length < 3) {
                        NotificationManager.showWarning("Le mot de passe est trop court");
                        return;
                    }

                    await this.login(credentials);
                });

                // Gestion du formulaire d'inscription
                this.registerForm?.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    
                    const formData = new FormData(this.registerForm);
                    const userData = {
                        full_name: formData.get('full_name'),
                        email: formData.get('email'),
                        password: formData.get('password'),
                        confirm_password: formData.get('confirm_password')
                    };

                    // Validations côté client
                    if (!userData.full_name.trim()) {
                        NotificationManager.showWarning("Veuillez saisir votre nom complet");
                        return;
                    }

                    if (!FormValidator.validateEmail(userData.email)) {
                        NotificationManager.showWarning("Veuillez saisir une adresse email valide");
                        return;
                    }

                    const passwordValidation = FormValidator.validatePassword(userData.password);
                    if (!passwordValidation.isValid) {
                        NotificationManager.showWarning("Le mot de passe doit contenir au moins 8 caractères avec lettres et chiffres");
                        return;
                    }

                    if (userData.password !== userData.confirm_password) {
                        NotificationManager.showWarning("Les mots de passe ne correspondent pas");
                        return;
                    }

                    if (!formData.get('agree_terms')) {
                        NotificationManager.showWarning("Vous devez accepter les conditions d'utilisation");
                        return;
                    }

                    await this.register(userData);
                });
            }

            initPasswordFeatures() {
                // Toggle password visibility
                document.getElementById('toggleLoginPassword')?.addEventListener('click', () => {
                    this.togglePasswordVisibility('loginPassword', 'toggleLoginPassword');
                });

                document.getElementById('toggleRegisterPassword')?.addEventListener('click', () => {
                    this.togglePasswordVisibility('registerPassword', 'toggleRegisterPassword');
                });

                // Password strength checker
                document.getElementById('registerPassword')?.addEventListener('input', (e) => {
                    this.updatePasswordStrength(e.target.value);
                });

                // Password confirmation checker
                document.getElementById('confirmPassword')?.addEventListener('input', (e) => {
                    this.checkPasswordMatch(e.target.value);
                });
            }

            togglePasswordVisibility(inputId, buttonId) {
                const passwordInput = document.getElementById(inputId);
                const toggleButton = document.getElementById(buttonId);
                const icon = toggleButton.querySelector('i');
                
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                } else {
                    passwordInput.type = 'password';
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
            }

            updatePasswordStrength(password) {
                const strengthBar = document.getElementById('strengthBar');
                const strengthText = document.getElementById('strengthText');
                
                const validation = FormValidator.validatePassword(password);
                const strength = validation.strength;
                const feedback = FormValidator.getPasswordFeedback(password);
                
                strengthBar.style.width = strength + '%';
                strengthBar.className = FormValidator.getStrengthBarClass(strength);
                strengthText.textContent = feedback.text;
                strengthText.className = `text-xs ${feedback.class}`;
            }

            checkPasswordMatch(confirmPassword) {
                const password = document.getElementById('registerPassword').value;
                const matchText = document.getElementById('passwordMatch');
                
                if (confirmPassword === '') {
                    matchText.textContent = '';
                    matchText.className = 'text-xs text-gray-400';
                } else if (password === confirmPassword) {
                    matchText.textContent = '✓ Les mots de passe correspondent';
                    matchText.className = 'text-xs text-emerald-400';
                } else {
                    matchText.textContent = '✗ Les mots de passe ne correspondent pas';
                    matchText.className = 'text-xs text-red-400';
                }
            }
        }

        // Classe principale de l'application
        class CVBotApp {
            constructor() {
                this.modalManager = new ModalManager();
                this.authManager = new AuthManager();
                this.initCarousel();
                this.initScrollAnimations();
                this.initNavigation();
            }

            initCarousel() {
                let currentSlide = 0;
                const slides = document.querySelectorAll('.carousel-slide');
                
                const nextSlide = () => {
                    slides[currentSlide].classList.remove('active');
                    slides[currentSlide].style.opacity = '0';
                    
                    currentSlide = (currentSlide + 1) % slides.length;
                    
                    slides[currentSlide].classList.add('active');
                    slides[currentSlide].style.opacity = '1';
                };
                
                setInterval(nextSlide, 5000);
            }

            initScrollAnimations() {
                const observerOptions = {
                    threshold: 0.1,
                    rootMargin: '0px 0px -50px 0px'
                };

                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            entry.target.style.animationDelay = '0s';
                            entry.target.classList.add('animate-fade-in-up');
                        }
                    });
                }, observerOptions);

                document.querySelectorAll('#features > div > div > div').forEach(card => {
                    observer.observe(card);
                });
            }

            initNavigation() {
                // Smooth scrolling
                document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                    anchor.addEventListener('click', function (e) {
                        e.preventDefault();
                        const target = document.querySelector(this.getAttribute('href'));
                        if (target) {
                            target.scrollIntoView({
                                behavior: 'smooth',
                                block: 'start'
                            });
                        }
                    });
                });

                // Navigation buttons
                document.getElementById('startBtn')?.addEventListener('click', () => {
                    NotificationManager.showInfo("Fonctionnalité bientôt disponible !");
                    console.log('Redirecting to CV generator...');
                });

                document.getElementById('loginBtn')?.addEventListener('click', () => {
                    this.modalManager.showModal('loginModal');
                });

                document.getElementById('contactUsBtn')?.addEventListener('click', () => {
                    NotificationManager.showInfo("Formulaire de contact bientôt disponible !");
                });

                document.getElementById('myAccountBtn')?.addEventListener('click', () => {
                    NotificationManager.showInfo("Veuillez vous connecter pour accéder à votre compte");
                    this.modalManager.showModal('loginModal');
                });
            }
        }

        // Initialisation de l'application
        let modalManager, authManager, app;

        document.addEventListener('DOMContentLoaded', () => {
            app = new CVBotApp();
            modalManager = app.modalManager;
            authManager = app.authManager;
            
            NotificationManager.showSuccess("Bienvenue sur CVBot ! 🚀");
        });