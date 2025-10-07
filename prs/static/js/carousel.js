/**
 * ===================================
 * CARROSSEL SUAVE - SMOOTH CAROUSEL
 * ===================================
 * Sistema de carrossel com transições suaves e controles inteligentes
 */

class SmoothCarousel {
    constructor() {
        this.currentSlide = 0;
        this.slideInterval = null;
        this.isTransitioning = false;
        
        this.track = document.querySelector('.carousel-track');
        this.slides = document.querySelectorAll('.carousel-slide');
        this.indicators = document.querySelectorAll('.indicator');
        this.container = document.querySelector('.carousel-container');
        
        if (!this.track || this.slides.length === 0) return;
        
        this.init();
    }
    
    /**
     * Inicializa o carrossel com todos os event listeners e configurações
     */
    init() {
        // Configurar posição inicial
        this.updateTrackPosition();
        this.updateIndicators();
        
        // Event listeners para indicadores
        this.indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => {
                this.goToSlide(index);
            });
        });
        
        // Event listeners para hover (pausar/retomar)
        if (this.container) {
            this.container.addEventListener('mouseenter', () => {
                this.pauseAutoAdvance();
            });
            
            this.container.addEventListener('mouseleave', () => {
                this.startAutoAdvance();
            });
        }
        
        // Iniciar auto-advance
        this.startAutoAdvance();
    }
    
    /**
     * Atualiza a posição do track do carrossel
     */
    updateTrackPosition() {
        if (!this.track) return;
        
        const translateX = -this.currentSlide * 100;
        this.track.style.transform = `translateX(${translateX}%)`;
    }
    
    /**
     * Atualiza os indicadores visuais
     */
    updateIndicators() {
        this.indicators.forEach((indicator, index) => {
            indicator.classList.toggle('active', index === this.currentSlide);
        });
    }
    
    /**
     * Navega para um slide específico
     * @param {number} index - Índice do slide de destino
     */
    goToSlide(index) {
        if (this.isTransitioning || index === this.currentSlide) return;
        
        // Garantir que o índice está dentro dos limites
        if (index < 0) index = this.slides.length - 1;
        if (index >= this.slides.length) index = 0;
        
        this.isTransitioning = true;
        this.currentSlide = index;
        
        this.updateTrackPosition();
        this.updateIndicators();
        
        // Reset do timer de auto-advance
        this.resetAutoAdvance();
        
        // Permitir nova transição após a animação
        setTimeout(() => {
            this.isTransitioning = false;
        }, 600); // Duração da transição CSS
    }
    
    /**
     * Avança para o próximo slide
     */
    nextSlide() {
        const nextIndex = (this.currentSlide + 1) % this.slides.length;
        this.goToSlide(nextIndex);
    }
    
    /**
     * Volta para o slide anterior
     */
    prevSlide() {
        const prevIndex = (this.currentSlide - 1 + this.slides.length) % this.slides.length;
        this.goToSlide(prevIndex);
    }
    
    /**
     * Inicia o avanço automático do carrossel
     */
    startAutoAdvance() {
        if (this.slides.length <= 1) return;
        
        this.slideInterval = setInterval(() => {
            this.nextSlide();
        }, 5000); // 5 segundos
    }
    
    /**
     * Pausa o avanço automático
     */
    pauseAutoAdvance() {
        if (this.slideInterval) {
            clearInterval(this.slideInterval);
            this.slideInterval = null;
        }
    }
    
    /**
     * Reinicia o timer de avanço automático
     */
    resetAutoAdvance() {
        this.pauseAutoAdvance();
        this.startAutoAdvance();
    }
}

/**
 * Função global para os botões de navegação
 * @param {number} direction - Direção da navegação (1 para próximo, -1 para anterior)
 */
function changeSlide(direction) {
    if (window.carousel) {
        if (direction === 1) {
            window.carousel.nextSlide();
        } else {
            window.carousel.prevSlide();
        }
    }
}

/**
 * Inicialização do carrossel quando o DOM estiver carregado
 */
document.addEventListener('DOMContentLoaded', () => {
    window.carousel = new SmoothCarousel();
});