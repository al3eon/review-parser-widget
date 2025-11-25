(function() {
    // ==========================================
    // 1. КОНСТАНТЫ И НАСТРОЙКИ
    // ==========================================
    const CONFIG = {
        API_URL: 'http://127.0.0.1:8000/api/reviews',
        LIMIT: 6,
        WIDGET_ID: 'lev-lab',
        DOTS_VISIBLE: 7, // Количество видимых точек в слайдере
        DOT_STEP: 20     // 8px точка + 12px отступ
    };

    let state = {
        offset: 0,
        isLoading: false,
        observer: null,
        allCards: [] // Храним список всех карточек для observer
    };

    // ==========================================
    // 2. CSS СТИЛИ (Минифицировано и структурировано)
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

        /* --- КАРТОЧКА --- */
        .rl-card {
            background: #fff; border-radius: 16px; padding: 16px; 
            box-shadow: 0 8px 24px rgba(0,0,0,0.05); border: 1px solid #f0f0f0;
            display: flex; flex-direction: column; height: 100%; transition: transform 0.2s ease;
        }
        .rl-card:hover { box-shadow: 0 12px 32px rgba(0,0,0,0.15); }

        /* Шапка */
        .rl-header { display: flex; align-items: center; margin-bottom: 6px; }
        .rl-avatar { width: 52px; height: 52px; border-radius: 50%; object-fit: cover; margin-right: 16px; background-color: #eee; }
        .rl-name { font-weight: 700; font-size: 16px; color: #222; margin-bottom: 4px; }
        .rl-date { font-size: 13px; color: #888; }
        .rl-stars { color: #FFC107; font-size: 22px; margin-bottom: 6px; letter-spacing: 1px; }

        /* Текст */
        .rl-text-container { position: relative; margin-bottom: 6px; }
        .rl-text {
            font-size: 15px; line-height: 1.6; color: #444; white-space: pre-line;
            display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; margin: 0; 
        }
        .rl-text.expanded { -webkit-line-clamp: unset; overflow: visible; padding-bottom: 0; }

        /* Кнопка Ещё/Свернуть */
        .rl-read-more-inline {
            position: absolute; bottom: 0; right: 0; background: #fff; padding-left: 6px;
            box-shadow: -15px 0 15px 10px #fff; font-weight: 600; font-size: 15px; color: #333; cursor: pointer; line-height: 1.6; display: inline; 
        }
        .rl-read-more-inline.expanded-btn {
            position: static; display: block; padding-left: 0; background: transparent; margin-top: 4px; text-align: left; 
        }
        .rl-read-more-inline:hover { text-decoration: underline; box-shadow: none; }
        .rl-hidden { display: none !important; }

        /* Подвал */
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
            display: none; /* Скрыто на десктопе */
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

    // Вставляем стили
    const styleSheet = document.createElement("style");
    styleSheet.innerText = styles;
    document.head.appendChild(styleSheet);


    // ==========================================
    // 3. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
    // ==========================================

    // Генерация звездочек
    function renderStars(rating) {
        return '★'.repeat(rating) + '☆'.repeat(5 - rating);
    }

    // Обновление позиции ленты точек (Карусель)
    function updateDotsScroll(activeIndex, container) {
        const dotsTrack = container.querySelector('.rl-dots-track');
        if (!dotsTrack) return;

        const dots = dotsTrack.querySelectorAll('.rl-dot');
        activeIndex = parseInt(activeIndex);

        // 1. Обновляем стили
        dots.forEach((d, i) => {
            d.classList.remove('active', 'small');
            if (Math.abs(activeIndex - i) >= 2) d.classList.add('small');
        });
        if (dots[activeIndex]) dots[activeIndex].classList.add('active');

        // 2. Математика сдвига
        const step = CONFIG.DOT_STEP;
        const visibleCount = CONFIG.DOTS_VISIBLE;

        // Позиция точки на ленте
        const dotPosition = activeIndex * step;
        // Центр окна
        const windowHalfWidth = (visibleCount * step) / 2 - (step / 2);

        // Сдвиг
        let translateX = -(dotPosition - windowHalfWidth);

        // Ограничители
        if (translateX > 0) translateX = 0; // Левый край

        const maxScroll = -((dots.length * step) - (visibleCount * step) + 12);

        // Если точек мало - центрируем
        if (dots.length <= visibleCount) {
            const trackWidth = dots.length * step - 12;
            const windowWidth = visibleCount * step - 12;
            translateX = (windowWidth - trackWidth) / 2;
        } else {
            if (translateX < maxScroll) translateX = maxScroll; // Правый край
        }

        dotsTrack.style.transform = `translateX(${translateX}px)`;
    }

    // Генерация HTML карточки
    function createCardHTML(review) {
        const avatarUrl = review.avatar_filename || 'https://via.placeholder.com/52';
        const safeText = review.text.replace(/</g, "&lt;").replace(/>/g, "&gt;");
        const uniqueId = Math.random().toString(36).substr(2, 9);

        return `
            <div class="rl-card">
                <div class="rl-header">
                    <img src="${avatarUrl}" class="rl-avatar" onerror="this.src='https://via.placeholder.com/52'">
                    <div>
                        <div class="rl-name">${review.author_name}</div>
                        <div class="rl-date">${review.date_custom}</div>
                    </div>
                </div>
                <div class="rl-stars">${renderStars(review.rating)}</div>
                
                <div class="rl-text-container">
                    <div class="rl-text" id="text-${uniqueId}">${safeText}</div>
                    <span class="rl-read-more-inline rl-hidden" data-target="text-${uniqueId}">Ещё</span>
                </div>
                <a href="https://yandex.ru/maps/?ll=38.830530%2C48.471092&mode=poi&poi%5Bpoint%5D=38.830193%2C48.471345&poi%5Buri%5D=ymapsbm1%3A%2F%2Forg%3Foid%3D175874439005&tab=reviews&z=19" target="_blank" class="rl-source">Отзыв из Яндекса</a>
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
            const response = await fetch(`${CONFIG.API_URL}?limit=${CONFIG.LIMIT}&offset=${state.offset}`);
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

            // 2. Обновляем точки
            const dotsTrack = container.querySelector('.rl-dots-track');
            const allCards = Array.from(grid.querySelectorAll('.rl-card'));

            // Очищаем и рендерим заново (простой надежный способ)
            dotsTrack.innerHTML = '';
            allCards.forEach((card, index) => {
                const dot = document.createElement('div');
                dot.className = 'rl-dot';
                dotsTrack.appendChild(dot);
                card.dataset.index = index;
            });

            // Обновляем позицию (начинаем с 0 или текущей)
            updateDotsScroll(0, container);


            // 3. Настраиваем Observer (Следим за прокруткой)
            if (state.observer) state.observer.disconnect();

            state.observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        updateDotsScroll(entry.target.dataset.index, container);
                    }
                });
            }, { root: grid, threshold: 0.51 });

            allCards.forEach(card => state.observer.observe(card));


            // 4. Настраиваем кнопки "Читать далее"
            grid.querySelectorAll('.rl-read-more-inline').forEach(btnMore => {
                // Пропускаем уже обработанные (если вдруг)
                if (btnMore.dataset.processed) return;

                const textBlock = document.getElementById(btnMore.dataset.target);
                if (textBlock.scrollHeight > textBlock.clientHeight) {
                    btnMore.classList.remove('rl-hidden');
                    btnMore.onclick = function() {
                        const card = this.closest('.rl-card');
                        const isExpanded = textBlock.classList.contains('expanded');
                        if (isExpanded) {
                            textBlock.classList.remove('expanded');
                            this.classList.remove('expanded-btn');
                            if (card) card.classList.remove('card-expanded');
                            this.textContent = 'Ещё';
                        } else {
                            textBlock.classList.add('expanded');
                            this.classList.add('expanded-btn');
                            if (card) card.classList.add('card-expanded');
                            this.textContent = 'Свернуть';
                        }
                    };
                }
                btnMore.dataset.processed = "true";
            });

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

    // ==========================================
    // 5. ИНИЦИАЛИЗАЦИЯ
    // ==========================================
    function init() {
        const container = document.querySelector('lev-lab') || document.getElementById(CONFIG.WIDGET_ID);
        if (!container) return;

        container.innerHTML = `
            <div class="rl-wrapper">
                <div class="rl-grid"></div>
                <div class="rl-dots-window">
                    <div class="rl-dots-track"></div>
                </div> 
                <div class="rl-controls">
                    <button class="rl-load-more-btn">Еще отзывы</button>
                    <a href="https://yandex.ru/maps/?ll=38.830530%2C48.471092&mode=poi&poi%5Bpoint%5D=38.830193%2C48.471345&poi%5Buri%5D=ymapsbm1%3A%2F%2Forg%3Foid%3D175874439005&tab=reviews&z=19" target="_blank" class="rl-write-btn">Оставить отзыв</a>
                </div>
            </div>
        `;

        const loadMoreBtn = container.querySelector('.rl-load-more-btn');

        // Вешаем обработчики
        loadMoreBtn.addEventListener('click', () => loadReviews(container, loadMoreBtn));
        initInfiniteScrollForMobile(container, loadMoreBtn);

        // Первая загрузка
        loadReviews(container, loadMoreBtn);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
