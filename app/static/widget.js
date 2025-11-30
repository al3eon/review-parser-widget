(function() {
    // ==========================================
    // 1. КОНСТАНТЫ И НАСТРОЙКИ
    // ==========================================
    const CONFIG = {
        BASE_URL: 'https://widgets.kulinarka.site',
        LIMIT: 6,
        WIDGET_ID: 'review-widget',
        DOTS_VISIBLE: 7,
        DOT_STEP: 20
    };

    // Собираем полные пути
    const API = {
        REVIEWS: `${CONFIG.BASE_URL}/api/reviews`,
        STATS: `${CONFIG.BASE_URL}/api/reviews/stats`
    };

    let state = {
        offset: 0,
        isLoading: false,
        observer: null,
        // allCards удален, так как не использовался
        stats: { total: 0, vk: 0, yandex: 0 },
        currentSource: ''
    };

    const ICONS = {
        vk: `<img src="${CONFIG.BASE_URL}/static/icons/vk.svg" class="rl-icon-img" alt="VK">`,
        yandex: `<img src="${CONFIG.BASE_URL}/static/icons/yandex.svg" class="rl-icon-img" alt="Yandex">`
    };

    // ==========================================
    // 2. CSS СТИЛИ (Оптимизировано)
    // ==========================================
    const styles = `
        body { margin: 0; padding: 0; }
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        /* --- БАЗОВЫЕ СТИЛИ --- */
        .rl-wrapper {
            width: 100%; max-width: 1200px; margin: 0 auto; padding: 0 20px;
            font-family: 'Inter', sans-serif; background-color: #CCEAFF;
            padding-top: 10px; padding-bottom: 20px; box-sizing: border-box;
        }

        .rl-grid {
            display: grid; grid-template-columns: repeat(2, 1fr); 
            gap: 60px 20px; margin-bottom: 40px;
        }
        
        .rl-filters-wrapper {
            display: block;
        }
        
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
        
        /* Объединенный стиль для иконок */
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
            color: #FFC107;       /* Желтый цвет */
            font-size: 20px;      /* Вернул крупный размер */
            margin-bottom: 8px;   /* Отступ снизу до текста */
            letter-spacing: 2px;  /* Расстояние между звездами, чтобы не слипались */
            line-height: 1;       /* Чтобы не распирало строку по высоте */
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
        .rl-review-photo { width: 100%; border-radius: 8px; margin-top: 8px; cursor: pointer; max-height: 200px; object-fit: cover; }

        .rl-source { font-size: 12px; color: #aaa; text-decoration: none; border-bottom: 1px dashed #ddd; align-self: flex-start; margin-top: auto; }

        /* Кнопки управления */
        .rl-controls { display: flex; justify-content: center; gap: 20px; margin-top: 50px; }
        .rl-load-more-btn, .rl-write-btn {
            height: 40px; padding: 0 32px; min-width: 180px; display: inline-flex; align-items: center; justify-content: center;
            border-radius: 50px; font-size: 16px; font-weight: 600; transition: all 0.2s; box-sizing: border-box; line-height: 1;
        }
        .rl-load-more-btn {
            background: #fff; color: #333; border: 1px solid #ddd; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .rl-load-more-btn:hover { background: #f9f9f9; border-color: #ccc; transform: translateY(-1px); }
        .rl-write-btn {
            background: #3CAAF7; color: #fff; border: 1px solid transparent; text-decoration: none; box-shadow: 0 4px 10px rgba(60, 170, 247, 0.3);
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

        /* ========================================== */
        /*            АДАПТИВНОСТЬ                    */
        /* ========================================== */
        @media (min-width: 900px) {
            .rl-grid { grid-template-columns: repeat(3, 1fr); }
        }

        @media (max-width: 599px) {
            .rl-wrapper { padding-left: 0 !important; padding-right: 0 !important; }
            .rl-btn-text { display: none !important; }
            .rl-filter-btn { padding: 8px 12px; }
            .rl-filters-wrapper {
                display: flex !important;
                width: 100% !important;
                padding: 0 !important;
            }
            
            .rl-filters {
                display: flex !important;
                width: -moz-fit-content !important;
                width: fit-content !important;
                margin-left: auto !important;
                margin-right: auto !important;
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
                display: flex; flex-direction: column; box-sizing: border-box;
                box-shadow: none;
            }
            .rl-stats-text {
                text-align: center; margin: 15px 0px 5px 0px; padding-left: 15px;
            }
            .rl-card:hover { box-shadow: none; }
            .rl-card.card-expanded { height: auto !important; }

            .rl-controls { margin-top: 0 !important; padding: 0 20px; flex-direction: column; gap: 10px; }
            .rl-load-more-btn { display: none !important; }
            .rl-write-btn { width: 100%; min-width: 0; }

            .rl-read-more-inline.expanded-btn {
                margin-top: 2px; margin-bottom: -5px; font-size: 14px; padding: 0; background: transparent; box-shadow: none; display: inline-block;
            }
            .rl-dots-window { display: block; }
        }
    `;

    const styleSheet = document.createElement("style");
    styleSheet.innerText = styles;
    document.head.appendChild(styleSheet);


    // ==========================================
    // 3. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
    // ==========================================

    // Функция для безопасности (Sanitization)
    function escapeHtml(text) {
        if (!text) return '';
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function renderStars(rating) {
        // Рейтинг может прийти null или undefined, ставим дефолт 5
        const r = rating || 5;
        return '★'.repeat(r) + '☆'.repeat(5 - r);
    }

    function updateDotsScroll(activeIndex, container) {
        const dotsTrack = container.querySelector('.rl-dots-track');
        if (!dotsTrack) return;

        const dots = dotsTrack.querySelectorAll('.rl-dot');
        activeIndex = parseInt(activeIndex);

        dots.forEach((d, i) => {
            d.classList.remove('active', 'small');
            if (Math.abs(activeIndex - i) >= 2) d.classList.add('small');
        });
        if (dots[activeIndex]) dots[activeIndex].classList.add('active');

        const step = CONFIG.DOT_STEP;
        const visibleCount = CONFIG.DOTS_VISIBLE;
        const dotPosition = activeIndex * step;
        const windowHalfWidth = (visibleCount * step) / 2 - (step / 2);
        let translateX = -(dotPosition - windowHalfWidth);

        if (translateX > 0) translateX = 0;

        const maxScroll = -((dots.length * step) - (visibleCount * step) + 12);

        if (dots.length <= visibleCount) {
            const trackWidth = dots.length * step - 12;
            const windowWidth = visibleCount * step - 12;
            translateX = (windowWidth - trackWidth) / 2;
        } else {
            if (translateX < maxScroll) translateX = maxScroll;
        }

        dotsTrack.style.transform = `translateX(${translateX}px)`;
    }

function createCardHTML(review) {
    const avatarUrl = review.avatar_filename || 'https://via.placeholder.com/52';
    const safeText = escapeHtml(review.text);
    const safeName = escapeHtml(review.author_name);
    const safeDate = escapeHtml(review.date_custom);
    const uniqueId = Math.random().toString(36).substr(2, 9);


    const isVk = review.source === 'vk';
    const sourceText = isVk ? 'Отзыв из ВКонтакте' : 'Отзыв из Яндекс.Карт';
    const sourceLink = isVk ? 'https://vk.com/reviews-120145172' : 'https://yandex.ru/maps/org/viantur/175874439005/reviews/?ll=38.830316%2C48.471413&z=17';
    const sourceColor = isVk ? '#0077FF' : '#FC3F1D';

    const starsHtml = `<div class="rl-stars">${renderStars(review.rating)}</div>`;

    return `
        <div class="rl-card">
            <div class="rl-header">
                <img src="${avatarUrl}" class="rl-avatar" onerror="this.src='https://via.placeholder.com/52'">
                <div>
                    <div class="rl-name">${safeName}</div>
                    <div class="rl-date">${safeDate}</div>
                </div>
            </div>
            ${starsHtml}
            
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

    // ==========================================
    // 4. ОСНОВНАЯ ЛОГИКА
    // ==========================================

    function initInfiniteScrollForMobile(container, loadMoreBtn) {
        const grid = container.querySelector('.rl-grid');
        grid.addEventListener('scroll', () => {
            if (window.innerWidth >= 600) return;
            // Грузим, когда до конца осталось 800px
            if (grid.scrollLeft + grid.clientWidth >= grid.scrollWidth - 800) {
                if (loadMoreBtn.style.display !== 'none' && !state.isLoading) {
                     loadReviews(container, loadMoreBtn);
                }
            }
        });
    }

    async function loadReviews(container, btn) {
        if (state.isLoading) return;
        state.isLoading = true;
        const originalBtnText = btn.textContent;
        btn.textContent = 'Загрузка...';

        try {
            // Используем URLSearchParams для чистоты
            const url = new URL(API.REVIEWS);
            url.searchParams.append('limit', CONFIG.LIMIT);
            url.searchParams.append('offset', state.offset);
            if (state.currentSource) {
                url.searchParams.append('source', state.currentSource);
            }

            const response = await fetch(url);
            if (!response.ok) throw new Error('Network error');
            const reviews = await response.json();

            if (reviews.length === 0) {
                btn.style.display = 'none';
                return;
            }

            const grid = container.querySelector('.rl-grid');

            // 1. Вставляем карточки
            reviews.forEach(review => {
                grid.insertAdjacentHTML('beforeend', createCardHTML(review));
            });

            // 2. Логика "Читать далее" (Только проверка высоты, клик обрабатывается делегированием)
            const newCards = grid.querySelectorAll('.rl-card:not([data-checked="true"])');
            newCards.forEach(card => {
                const btnMore = card.querySelector('.rl-read-more-inline');
                const textBlock = card.querySelector('.rl-text');

                if (btnMore && textBlock && textBlock.scrollHeight > textBlock.clientHeight) {
                    btnMore.classList.remove('rl-hidden');
                }
                card.dataset.checked = "true"; // Помечаем как проверенную
            });

            // 3. Обновляем точки (для мобилки)
            const dotsTrack = container.querySelector('.rl-dots-track');
            const allCards = Array.from(grid.querySelectorAll('.rl-card'));

            dotsTrack.innerHTML = '';
            allCards.forEach((card, index) => {
                const dot = document.createElement('div');
                dot.className = 'rl-dot';
                dotsTrack.appendChild(dot);
                card.dataset.index = index;
            });
            updateDotsScroll(0, container);

            // 4. IntersectionObserver
            if (state.observer) state.observer.disconnect();
            state.observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        updateDotsScroll(entry.target.dataset.index, container);
                    }
                });
            }, { root: grid, threshold: 0.51 });
            allCards.forEach(card => state.observer.observe(card));

            state.offset += reviews.length;
            if (reviews.length < CONFIG.LIMIT) btn.style.display = 'none';

        } catch (error) {
            console.error(error);
            btn.textContent = 'Ошибка';
        } finally {
            state.isLoading = false;
            if (btn.textContent === 'Загрузка...') btn.textContent = originalBtnText;
        }
    }

    async function fetchStats(container) {
        try {
            const response = await fetch(API.STATS);
            if (!response.ok) return;

            state.stats = await response.json();
            updateStatsText(container);
        } catch (e) {
            console.error("Не удалось загрузить статистику", e);
        }
    }

    function updateStatsText(container) {
        const elText = container.querySelector('.rl-stats-text');
        if (!elText) return;

        const s = state.stats;
        let text;

        if (state.currentSource === 'vk') {
            text = `${s.vk} отзывов из ВКонтакте`;
        } else if (state.currentSource === 'yandex') {
            text = `${s.yandex} отзывов из Яндекса`;
        } else {
            text = `${s.total} отзыва из 2 источников`;
        }
        elText.textContent = text;
    }

    // ==========================================
    // 5. ИНИЦИАЛИЗАЦИЯ
    // ==========================================
    function init() {
        const container = document.querySelector('lev-lab') || document.getElementById(CONFIG.WIDGET_ID);
        if (!container) return;

        container.innerHTML = `
            <div class="rl-wrapper">
                <div class="rl-filters-wrapper">
                    <div class="rl-filters">
                        <button class="rl-filter-btn active" data-source="">
                            Все отзывы
                        </button>
                        
                        <button class="rl-filter-btn" data-source="vk">
                            <span class="rl-btn-icon">${ICONS.vk}</span>
                            <span class="rl-btn-text">ВКонтакте</span>
                            <span style="color: #888; margin-left: 4px; font-weight: 400;">5.0</span>
                        </button>
                        
                        <button class="rl-filter-btn" data-source="yandex">
                            <span class="rl-btn-icon">${ICONS.yandex}</span>
                            <span class="rl-btn-text">Яндекс</span>
                            <span style="color: #888; margin-left: 4px; font-weight: 400;">5.0</span>
                        </button>
                    </div>
                </div>
                
                <div class="rl-stats-text">Загрузка...</div>
                <div class="rl-grid"></div>
                
                <div class="rl-dots-window"><div class="rl-dots-track"></div></div> 
                
                <div class="rl-controls">
                    <button class="rl-load-more-btn">Еще отзывы</button>
                    <a href="https://yandex.ru/maps" target="_blank" class="rl-write-btn">Оставить отзыв</a>
                </div>
            </div>
        `;

        const loadMoreBtn = container.querySelector('.rl-load-more-btn');
        const grid = container.querySelector('.rl-grid');

        // Делегирование событий для кнопок "Еще/Свернуть"
        // Это более производительно, чем вешать onclick на каждую кнопку
        grid.addEventListener('click', function(e) {
            if (e.target.classList.contains('rl-read-more-inline')) {
                const btn = e.target;
                const card = btn.closest('.rl-card');
                const textId = btn.dataset.target;
                const textBlock = document.getElementById(textId);

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

        // Табы фильтров
        const filterBtns = container.querySelectorAll('.rl-filter-btn');
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                state.currentSource = btn.dataset.source;
                state.offset = 0;
                // Очистка
                grid.innerHTML = '';
                container.querySelector('.rl-dots-track').innerHTML = ''; // Очищаем и точки

                loadMoreBtn.style.display = 'inline-flex';
                updateStatsText(container);
                loadReviews(container, loadMoreBtn);
            });
        });

        loadMoreBtn.addEventListener('click', () => loadReviews(container, loadMoreBtn));
        initInfiniteScrollForMobile(container, loadMoreBtn);

        loadReviews(container, loadMoreBtn);
        fetchStats(container);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
