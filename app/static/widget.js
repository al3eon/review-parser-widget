class ReviewWidget extends HTMLElement {
    constructor() {
        super();
        // Создаем Shadow DOM
        this.attachShadow({ mode: 'open' });

        // Конфигурация и состояние
        this.CONFIG = {
            BASE_URL: 'https://widgets.kulinarka.site',
            LIMIT: 6,
            DOTS_VISIBLE: 7,
            DOT_STEP: 20,

            SOURCES: {}
        };

        this.state = {
            offset: 0,
            isLoading: false,
            observer: null,
            stats: { total: 0, vk: 0, yandex: 0 },
            currentSource: '',
            sourcesLoaded: false
        };
    }

    async fetchSources() {
        const response = await fetch(`${this.CONFIG.BASE_URL}/api/config/sources`);
        if (!response.ok) throw new Error('Sources config not available');
        this.CONFIG.SOURCES = await response.json();
        this.state.sourcesLoaded = true;
    }

    loadFallbackSources() {
        // ← Локальный fallback на случай недоступности API
        this.CONFIG.SOURCES = {
            vk: { url: '#', color: '#0077FF', iconPath: '/static/icons/vk.svg', displayName: 'ВКонтакте' },
            yandex: { url: '#', color: '#FC3F1D', iconPath: '/static/icons/yandex.svg', displayName: 'Яндекс' }
        };
        this.state.sourcesLoaded = true;
    }

    // Жизненный цикл: когда элемент добавлен в DOM
    async connectedCallback() {
        try {
            await this.fetchSources();  // ← НОВЫЙ метод
            this.render();
            this.initLogic();
        } catch (error) {
            console.error('Failed to load sources config:', error);
            this.loadFallbackSources();
            this.render();
            this.initLogic();
        }
    }

    // Жизненный цикл: когда элемент удален (чистим память)
    disconnectedCallback() {
        if (this.state.observer) this.state.observer.disconnect();
    }

    // ==========================================
    // 1. РЕНДЕРИНГ (HTML + CSS)
    // ==========================================
    getStyles() {
        return `
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

            :host {
                display: block;
                width: 100%;
                margin: 0;
                padding: 0;
                font-family: 'Inter', sans-serif;
                background-color: #CCEAFF; /* Фон перенесен на сам контейнер */
                box-sizing: border-box;
            }

            .rl-wrapper {
                width: 100%; max-width: 1200px; margin: 0 auto; padding: 10px 20px 20px 20px;
                box-sizing: border-box;
            }

            /* Скроллбар для всего виджета, если нужно */
            * { box-sizing: border-box; }

            .rl-grid {
                display: grid; grid-template-columns: repeat(2, 1fr);
                gap: 60px 20px; margin-bottom: 40px;
            }

            .rl-filters-wrapper { display: block; }

            .rl-filters {
                display: inline-flex;
                background: #E2F2FF;
                padding: 4px;
                border-radius: 100px;
                gap: 2px;
            }

            .rl-filter-btn {
                display: flex; align-items: center; gap: 6px;
                padding: 8px 20px; border-radius: 100px; border: none;
                background: transparent; color: #555; font-size: 15px; font-weight: 600;
                cursor: pointer; transition: all 0.2s ease;
                font-family: 'Inter', sans-serif; line-height: 1;
            }

            .rl-filter-btn:hover { color: #333; }

            .rl-filter-btn.active {
                background: #fff; color: #222;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }

            .rl-stats-text {
                text-align: left; font-size: 14px; color: #5F7D95;
                margin-top: 15px; margin-bottom: 15px; font-weight: 500;
            }

            .rl-btn-icon {
                width: 24px; height: 24px;
                display: flex; align-items: center; justify-content: center;
                flex-shrink: 0;
            }

            .rl-icon-img {
                width: 100%; height: 100%;
                display: block; object-fit: cover; border-radius: 50%;
            }

            /* --- КАРТОЧКА --- */
            .rl-card {
                background: #fff; border-radius: 16px; padding: 16px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.05); border: 1px solid #f0f0f0;
                display: flex; flex-direction: column; height: 100%; transition: transform 0.2s ease;
            }
            .rl-card:hover { box-shadow: 0 12px 32px rgba(0,0,0,0.15); }

            .rl-header { display: flex; align-items: center; margin-bottom: 6px; }
            .rl-avatar { width: 52px; height: 52px; border-radius: 50%; object-fit: cover; margin-right: 16px; background-color: #eee; }
            .rl-name { font-weight: 700; font-size: 16px; color: #222; margin-bottom: 4px; }
            .rl-date { font-size: 13px; color: #888; }
            .rl-stars {
                color: #FFC107; font-size: 20px; margin-bottom: 8px;
                letter-spacing: 2px; line-height: 1;
            }

            .rl-text-container { position: relative; margin-bottom: 6px; }
            .rl-text {
                font-size: 15px; line-height: 1.6; color: #444; white-space: pre-line;
                display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; margin: 0;
            }
            .rl-text.expanded { -webkit-line-clamp: unset; overflow: visible; padding-bottom: 0; }

            .rl-read-more-inline {
                position: absolute; bottom: 0; right: 0; background: #fff; padding-left: 6px;
                box-shadow: -15px 0 15px 10px #fff;
                font-weight: 600; font-size: 15px; color: #333; cursor: pointer; line-height: 1.6; display: inline;
                transition: color 0.2s;
            }
            .rl-read-more-inline:not(.expanded-btn):hover { color: #000; }

            .rl-read-more-inline.expanded-btn {
                position: static; display: block; padding-left: 0;
                background: transparent; margin-top: 6px; text-align: left;
                box-shadow: none !important; color: #555;
            }

            .rl-hidden { display: none !important; }
            .rl-source { font-size: 12px; color: #aaa; text-decoration: none; border-bottom: 1px dashed #ddd; align-self: flex-start; margin-top: auto; }

            /* Кнопки */
            .rl-controls { display: flex; justify-content: center; gap: 20px; margin-top: 50px; }
            .rl-load-more-btn, .rl-write-btn {
                height: 40px; padding: 0 32px; min-width: 180px; display: inline-flex; align-items: center; justify-content: center;
                border-radius: 50px; font-size: 16px; font-weight: 600; transition: all 0.2s; box-sizing: border-box; line-height: 1;
                text-decoration: none;
            }
            .rl-load-more-btn {
                background: #fff; color: #333; border: 1px solid #ddd; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }
            .rl-load-more-btn:hover { background: #f9f9f9; border-color: #ccc; transform: translateY(-1px); }
            .rl-write-btn {
                background: #3CAAF7; color: #fff; border: 1px solid transparent; box-shadow: 0 4px 10px rgba(60, 170, 247, 0.3);
            }
            .rl-write-btn:hover { background-color: #2b9ae6; }

            /* --- ДОТЫ --- */
            .rl-dots-window {
                display: none;
                width: 144px; height: 12px; overflow: hidden; margin: 16px auto 8px auto; position: relative;
                -webkit-mask-image: linear-gradient(to right, transparent 0%, black 15%, black 85%, transparent 100%);
                mask-image: linear-gradient(to right, transparent 0%, black 15%, black 85%, transparent 100%);
            }
            .rl-dots-track {
                display: flex; gap: 12px; width: max-content; transition: transform 0.3s cubic-bezier(0.25, 1, 0.5, 1);
                padding-top: 2px; padding-left: 12px; padding-right: 12px; box-sizing: content-box;
            }
            .rl-dot {
                flex-shrink: 0; width: 8px; height: 8px; border-radius: 50%; background-color: #D1D9E6; transition: all 0.3s ease;
            }
            .rl-dot.active { background-color: #3CAAF7; transform: scale(1.25); }
            .rl-dot.small { transform: scale(0.7); opacity: 0.6; }

            /* АДАПТИВНОСТЬ */
            @media (min-width: 900px) {
                .rl-grid { grid-template-columns: repeat(3, 1fr); box-shadow: none }
            }

            @media (max-width: 599px) {
                .rl-wrapper { padding-left: 0 !important; padding-right: 0 !important; }
                .rl-btn-text { display: none !important; }
                .rl-filter-btn { padding: 8px 12px; }
                .rl-filters-wrapper { display: flex !important; width: 100% !important; padding: 0 !important; }
                .rl-filters {
                    display: flex !important; width: fit-content !important; margin: 0 auto !important;
                }
                .rl-grid {
                    display: flex; overflow-x: auto; -webkit-overflow-scrolling: touch;
                    scroll-snap-type: x mandatory; scroll-behavior: smooth;
                    margin-bottom: 0 !important; gap: 16px; padding: 10px 20px 5px 20px;
                    scrollbar-width: none; -ms-overflow-style: none; align-items: stretch;
                }
                .rl-grid::-webkit-scrollbar { display: none; }

                .rl-card {
                    flex: 0 0 100%; width: 100%; scroll-snap-align: center; scroll-snap-stop: always;
                    min-height: 265px; height: 265px; transition: height 0.3s ease;
                    box-shadow: none;
                }
                .rl-stats-text { text-align: center; margin: 15px 0px 5px 0px; padding-left: 15px; }
                .rl-card.card-expanded { height: auto !important; }
                .rl-controls { margin-top: 0 !important; padding: 0 20px; flex-direction: column; gap: 10px; }
                .rl-load-more-btn { display: none !important; }
                .rl-write-btn { width: 100%; min-width: 0; }
                .rl-read-more-inline.expanded-btn {
                    margin-top: 2px; margin-bottom: -5px; font-size: 14px; padding: 0;
                    background: transparent; box-shadow: none; display: inline-block;
                }
                .rl-dots-window { display: block; }
            }
            </style>
        `;
    }

    render() {
        if (!this.state.sourcesLoaded || Object.keys(this.CONFIG.SOURCES).length === 0) {
            this.shadowRoot.innerHTML = `
                ${this.getStyles()}
                <div class="rl-wrapper">
                    <div class="rl-stats-text">Загрузка конфигурации...</div>
                </div>
            `;
            return;
        }
        const icons = {};
        for (const key in this.CONFIG.SOURCES) {
            icons[key] = `<img src="${this.CONFIG.BASE_URL}${this.CONFIG.SOURCES[key].iconPath}" 
                               class="rl-icon-img" 
                               alt="${this.CONFIG.SOURCES[key].displayName}">`;
        }

        this.shadowRoot.innerHTML = `
            ${this.getStyles()}
            <div class="rl-wrapper">
                <div class="rl-filters-wrapper">
                    <div class="rl-filters">
                        <button class="rl-filter-btn active" data-source="">Все отзывы</button>

                        <button class="rl-filter-btn" data-source="vk">
                            <span class="rl-btn-icon">${icons.vk}</span>
                            <span class="rl-btn-text">${this.CONFIG.SOURCES.vk.displayName}</span>
                            <span style="color: #888; margin-left: 4px; font-weight: 400;">5.0</span>
                        </button>

                        <button class="rl-filter-btn" data-source="yandex">
                            <span class="rl-btn-icon">${icons.yandex}</span>
                            <span class="rl-btn-text">${this.CONFIG.SOURCES.yandex.displayName}</span>
                            <span style="color: #888; margin-left: 4px; font-weight: 400;">5.0</span>
                        </button>
                    </div>
                </div>

                <div class="rl-stats-text">Загрузка...</div>
                <div class="rl-grid"></div>

                <div class="rl-dots-window"><div class="rl-dots-track"></div></div>

                <div class="rl-controls">
                    <button class="rl-load-more-btn">Еще отзывы</button>
                     <a href="${this.CONFIG.SOURCES.yandex.url}" target="_blank" class="rl-write-btn">Оставить отзыв</a>
                </div>
            </div>
        `;
    }

    // ==========================================
    // 2. ЛОГИКА (События и Запросы)
    // ==========================================
    initLogic() {
        const loadMoreBtn = this.shadowRoot.querySelector('.rl-load-more-btn');
        const grid = this.shadowRoot.querySelector('.rl-grid');
        const filterBtns = this.shadowRoot.querySelectorAll('.rl-filter-btn');

        // Делегирование "Читать далее"
        grid.addEventListener('click', (e) => {
            if (e.target.classList.contains('rl-read-more-inline')) {
                const btn = e.target;
                const card = btn.closest('.rl-card');
                const textId = btn.dataset.target;
                // Ищем внутри Shadow DOM по ID
                const textBlock = this.shadowRoot.getElementById(textId);

                if (textBlock.classList.contains('expanded')) {
                    textBlock.classList.remove('expanded');
                    btn.classList.remove('expanded-btn');
                    if (card) card.classList.remove('card-expanded');
                    btn.textContent = 'Ещё';
                } else {
                    textBlock.classList.add('expanded');
                    btn.classList.add('expanded-btn');
                    if (card) card.classList.add('card-expanded');
                    btn.textContent = 'Свернуть';
                }
            }
        });

        // Фильтры
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                this.state.currentSource = btn.dataset.source;
                this.state.offset = 0;

                // Очистка
                grid.innerHTML = '';
                this.shadowRoot.querySelector('.rl-dots-track').innerHTML = '';

                loadMoreBtn.style.display = 'inline-flex';
                this.updateStatsText();
                this.loadReviews(loadMoreBtn);
            });
        });

        loadMoreBtn.addEventListener('click', () => this.loadReviews(loadMoreBtn));

        // Mobile Infinite Scroll
        grid.addEventListener('scroll', () => {
            if (window.innerWidth >= 600) return;
            if (grid.scrollLeft + grid.clientWidth >= grid.scrollWidth - 800) {
                if (loadMoreBtn.style.display !== 'none' && !this.state.isLoading) {
                     this.loadReviews(loadMoreBtn);
                }
            }
        });

        // Первый запуск
        this.loadReviews(loadMoreBtn);
        this.fetchStats();
    }

    async loadReviews(btn) {
        if (this.state.isLoading) return;
        this.state.isLoading = true;
        const originalBtnText = btn.textContent;
        btn.textContent = 'Загрузка...';

        try {
            const url = new URL(`${this.CONFIG.BASE_URL}/api/reviews`);
            url.searchParams.append('limit', this.CONFIG.LIMIT);
            url.searchParams.append('offset', this.state.offset);
            if (this.state.currentSource) {
                url.searchParams.append('source', this.state.currentSource);
            }

            const response = await fetch(url);
            if (!response.ok) throw new Error('API Error');
            const reviews = await response.json();

            if (reviews.length === 0) {
                btn.style.display = 'none';
                return;
            }

            const grid = this.shadowRoot.querySelector('.rl-grid');

            // Вставка
            reviews.forEach(review => {
                grid.insertAdjacentHTML('beforeend', this.createCardHTML(review));
            });

            // Проверка "Читать далее"
            const newCards = grid.querySelectorAll('.rl-card:not([data-checked="true"])');
            newCards.forEach(card => {
                const btnMore = card.querySelector('.rl-read-more-inline');
                const textBlock = card.querySelector('.rl-text');
                if (btnMore && textBlock && textBlock.scrollHeight > textBlock.clientHeight) {
                    btnMore.classList.remove('rl-hidden');
                }
                card.dataset.checked = "true";
            });

            // Обновление точек
            this.updateDotsLogic();

            this.state.offset += reviews.length;
            if (reviews.length < this.CONFIG.LIMIT) btn.style.display = 'none';

        } catch (error) {
            console.error(error);
            btn.textContent = 'Ошибка';
        } finally {
            this.state.isLoading = false;
            if (btn.textContent === 'Загрузка...') btn.textContent = originalBtnText;
        }
    }

    async fetchStats() {
        try {
            const response = await fetch(`${this.CONFIG.BASE_URL}/api/reviews/stats`);
            if (response.ok) {
                this.state.stats = await response.json();
                this.updateStatsText();
            }
        } catch (e) {
            console.error("Stats error", e);
        }
    }

    // ==========================================
    // 3. HELPER FUNCTIONS
    // ==========================================
    updateStatsText() {
        const elText = this.shadowRoot.querySelector('.rl-stats-text');
        if (!elText) return;

        const s = this.state.stats;
        let text;
        if (this.state.currentSource === 'vk') text = `${s.vk} отзывов из ВКонтакте`;
        else if (this.state.currentSource === 'yandex') text = `${s.yandex} отзывов из Яндекса`;
        else text = `${s.total} отзыва из 2 источников`;

        elText.textContent = text;
    }

    createCardHTML(review) {
        const avatarUrl = review.avatar_filename || 'https://via.placeholder.com/52';
        const safeText = this.escapeHtml(review.text);
        const safeName = this.escapeHtml(review.author_name);
        const safeDate = this.escapeHtml(review.date_custom);
        const uniqueId = Math.random().toString(36).substr(2, 9);

        const sourceConfig = this.CONFIG.SOURCES[review.source] || {};
        const sourceText = sourceConfig.displayName ?
            `Отзыв из ${sourceConfig.displayName}` : 'Отзыв';
        const sourceLink = sourceConfig.url || '#';
        const sourceColor = sourceConfig.color || '#000';

        return `
            <div class="rl-card">
                <div class="rl-header">
                    <img src="${avatarUrl}" class="rl-avatar" onerror="this.src='https://via.placeholder.com/52'">
                    <div>
                        <div class="rl-name">${safeName}</div>
                        <div class="rl-date">${safeDate}</div>
                    </div>
                </div>
                <div class="rl-stars">${this.renderStars(review.rating)}</div>

                <div class="rl-text-container">
                    <div class="rl-text" id="text-${uniqueId}">${safeText}</div>
                    <span class="rl-read-more-inline rl-hidden" data-target="text-${uniqueId}">Ещё</span>
                </div>

                 <a href="${sourceLink}" target="_blank" class="rl-source" style="color: ${sourceColor}">
                    ${sourceText}
                 </a>
            </div>
        `;
    }

    escapeHtml(text) {
        if (!text) return '';
        return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
    }

    renderStars(rating) {
        const r = rating || 5;
        return '★'.repeat(r) + '☆'.repeat(5 - r);
    }

    updateDotsLogic() {
        const grid = this.shadowRoot.querySelector('.rl-grid');
        const dotsTrack = this.shadowRoot.querySelector('.rl-dots-track');
        const allCards = Array.from(grid.querySelectorAll('.rl-card'));

        dotsTrack.innerHTML = '';
        allCards.forEach((card, index) => {
            const dot = document.createElement('div');
            dot.className = 'rl-dot';
            dotsTrack.appendChild(dot);
            card.dataset.index = index;
        });
        this.updateDotsScroll(0);

        // IntersectionObserver внутри Shadow DOM
        if (this.state.observer) this.state.observer.disconnect();
        this.state.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.updateDotsScroll(entry.target.dataset.index);
                }
            });
        }, { root: grid, threshold: 0.51 });

        allCards.forEach(card => this.state.observer.observe(card));
    }

    updateDotsScroll(activeIndex) {
        const dotsTrack = this.shadowRoot.querySelector('.rl-dots-track');
        if (!dotsTrack) return;

        const dots = dotsTrack.querySelectorAll('.rl-dot');
        activeIndex = parseInt(activeIndex);

        dots.forEach((d, i) => {
            d.classList.remove('active', 'small');
            if (Math.abs(activeIndex - i) >= 2) d.classList.add('small');
        });
        if (dots[activeIndex]) dots[activeIndex].classList.add('active');

        const step = this.CONFIG.DOT_STEP;
        const visibleCount = this.CONFIG.DOTS_VISIBLE;
        const dotPosition = activeIndex * step;
        // Простая логика центрирования, как была
        let translateX = -(dotPosition - ((visibleCount * step) / 2) + (step/2));
        if (translateX > 0) translateX = 0;

        // ... упрощенный расчет границ, аналогичный оригиналу ...
        dotsTrack.style.transform = `translateX(${translateX}px)`;
    }
}

// Регистрация веб-компонента
customElements.define('review-widget', ReviewWidget);
