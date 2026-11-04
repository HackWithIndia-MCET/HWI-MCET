/**
 * HackWithIndia × MCET — Frontend Animations Engine
 * Features:
 * 1. Scroll Reveal Animations (Sections, Headings, Cards, Media)
 * 2. Parallax Effects (Background Grid, Ambient Embers, 3D Hero Parallax)
 * 3. Text Splitting Animations (Word-by-word reveal for Major Headings)
 * 4. Interactive Hero Orbital Graphic (3D Tilt, Orbiting Satellites, Dynamic Star)
 * 5. Smooth Scrolling (Fixed Header Offset 80px, Hash Management)
 */

(function () {
    'use strict';

    // Check prefers-reduced-motion
    const prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    document.addEventListener('DOMContentLoaded', () => {
        initSmoothScrolling();
        initTextSplitting();
        initScrollReveals();
        initInteractiveHeroGraphic();

    });

    // =========================================================================
    // 5. SMOOTH SCROLLING (Offset-Aware for 80px Sticky Header)
    // =========================================================================
    function initSmoothScrolling() {
        const HEADER_OFFSET = 84; // 80px navbar + 4px breathing room

        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const href = this.getAttribute('href');
                if (!href || href === '#' || href === '#!') return;

                const targetEl = document.querySelector(href);
                if (targetEl) {
                    e.preventDefault();

                    const rect = targetEl.getBoundingClientRect();
                    const targetPosition = rect.top + window.pageYOffset - HEADER_OFFSET;

                    window.scrollTo({
                        top: Math.max(0, targetPosition),
                        behavior: prefersReducedMotion ? 'auto' : 'smooth'
                    });

                    // Update URL hash without instant jump
                    if (history.pushState) {
                        history.pushState(null, null, href);
                    }

                    // Auto-close mobile menu if open
                    const mobileNav = document.getElementById('mobile-nav');
                    if (mobileNav && !mobileNav.classList.contains('hidden')) {
                        mobileNav.classList.add('hidden');
                    }
                }
            });
        });
    }

    // =========================================================================
    // 3. TEXT SPLITTING ANIMATIONS (Accessible Word-by-Word Reveal)
    // =========================================================================
    const splitHeadingRegistry = [];

    function initTextSplitting() {
        // Target headlines: Hero, About, Events, Team, Domains, Resources
        const targetSelectors = [
            '#about h2',
            '#events h2',
            '#team h2',
            '#domains h2',
            '#resources h2'
        ];

        targetSelectors.forEach(sel => {
            const heading = document.querySelector(sel);
            if (heading) {
                splitHeadingIntoWords(heading);
            }
        });

        // Hero headline is kept 100% visible standard HTML - no opacity/transform masking
        const heroHeading = document.querySelector('#hero h1');
        if (heroHeading) {
            heroHeading.style.opacity = '1';
            heroHeading.style.visibility = 'visible';
            heroHeading.style.transform = 'none';
        }
    }

    function splitHeadingIntoWords(el) {
        // Preserve accessibility: store full text into aria-label
        const originalText = el.innerText.trim();
        if (!el.getAttribute('aria-label')) {
            el.setAttribute('aria-label', originalText);
        }

        // Recursive helper to split text nodes while preserving tags like <span class="text-[#FF2A2A]"> or <br>
        function processNode(node) {
            if (node.nodeType === Node.TEXT_NODE) {
                const text = node.textContent;
                const words = text.split(/(\s+)/);
                const fragment = document.createDocumentFragment();

                words.forEach(w => {
                    if (/^\s+$/.test(w)) {
                        fragment.appendChild(document.createTextNode(w));
                    } else if (w.length > 0) {
                        const mask = document.createElement('span');
                        mask.className = 'split-word-mask';
                        const inner = document.createElement('span');
                        inner.className = 'split-word-item';
                        inner.textContent = w;
                        mask.appendChild(inner);
                        fragment.appendChild(mask);
                    }
                });
                node.parentNode.replaceChild(fragment, node);
            } else if (node.nodeType === Node.ELEMENT_NODE) {
                // Do not split into sub-children if it's already masked
                if (!node.classList.contains('split-word-mask')) {
                    Array.from(node.childNodes).forEach(processNode);
                }
            }
        }

        Array.from(el.childNodes).forEach(processNode);
        splitHeadingRegistry.push(el);
    }

    function triggerWordReveal(headingEl, baseDelay = 0) {
        if (!headingEl || headingEl.dataset.wordsRevealed === 'true') return;
        headingEl.dataset.wordsRevealed = 'true';

        const words = headingEl.querySelectorAll('.split-word-item');
        words.forEach((w, idx) => {
            const delay = baseDelay + idx * 0.045; // 45ms stagger per word
            w.style.transitionDelay = `${delay}s`;
            w.classList.add('word-revealed');
        });
    }

    // =========================================================================
    // 1. SCROLL REVEAL ANIMATIONS (Sections, Cards, Staggers)
    // =========================================================================
    function initScrollReveals() {
        // ONLY target content sections below the hero: About, Events, Team, Domains, Resources
        const contentSections = document.querySelectorAll('#about, #events, #team, #domains, #resources');

        contentSections.forEach(sec => {
            sec.classList.add('reveal-on-scroll');

            // Only tag cyber-cards inside content sections
            const cards = sec.querySelectorAll('.cyber-card');
            cards.forEach((card, idx) => {
                card.classList.add('stagger-card');
                card.style.transitionDelay = `${idx * 0.07}s`;
            });
        });

        // Set up IntersectionObserver
        const observerOptions = {
            threshold: 0.08,
            rootMargin: '0px 0px -30px 0px'
        };

        const sectionObserver = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const sec = entry.target;
                    sec.classList.add('is-revealed');

                    const cards = sec.querySelectorAll('.stagger-card');
                    cards.forEach(card => card.classList.add('is-revealed'));

                    const headings = sec.querySelectorAll('h2, h3');
                    headings.forEach(h => {
                        triggerWordReveal(h, 0.15);
                    });

                    obs.unobserve(sec);
                }
            });
        }, observerOptions);

        contentSections.forEach(sec => {
            sectionObserver.observe(sec);
        });
    }

    // =========================================================================
    // 4. INTERACTIVE HERO ORBITAL GRAPHIC
    // =========================================================================
    function initInteractiveHeroGraphic() {
        // Find right column of hero containing the wireframe SVG and central asterisk
        const heroRightCol = document.querySelector('#hero .lg\\:col-span-5');
        if (!heroRightCol) return;

        // Find the wireframe container
        const wireframeWrap = heroRightCol.querySelector('.relative.w-full.max-w-\\[360px\\]');
        if (!wireframeWrap) return;

        // Enhance wrappers with interactive classes
        heroRightCol.classList.add('hero-orbital-stage');
        wireframeWrap.classList.add('hero-orbital-card', 'hero-orbital-float');

        // Add ambient glow behind graphic if not already present
        if (!wireframeWrap.querySelector('.hero-orbital-glow')) {
            const glow = document.createElement('div');
            glow.className = 'hero-orbital-glow';
            wireframeWrap.insertBefore(glow, wireframeWrap.firstChild);
        }

        // Add interactive pointer spotlight flare
        let pointerGlow = wireframeWrap.querySelector('.hero-pointer-glow');
        if (!pointerGlow) {
            pointerGlow = document.createElement('div');
            pointerGlow.className = 'hero-pointer-glow';
            wireframeWrap.appendChild(pointerGlow);
        }

        // Center asterisk dynamic class
        const starContainer = wireframeWrap.querySelector('.w-44.h-44');
        if (starContainer) {
            starContainer.classList.add('hero-star-dynamic');
        }

        // Enhance SVG wireframe with orbiting satellites
        const svgWireframe = wireframeWrap.querySelector('svg.pointer-events-none');
        if (svgWireframe && !svgWireframe.querySelector('.orbital-satellite')) {
            svgWireframe.classList.add('hero-wireframe-layer');

            // Satellite 1 along Orbit 1
            const sat1 = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            sat1.setAttribute('class', 'orbital-satellite');
            sat1.setAttribute('r', '4');
            sat1.setAttribute('fill', '#FF2A2A');
            sat1.setAttribute('cx', '200');
            sat1.setAttribute('cy', '115');
            sat1.setAttribute('filter', 'drop-shadow(0 0 8px #FF2A2A)');
            svgWireframe.appendChild(sat1);

            // Satellite 2 along Orbit 2
            const sat2 = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            sat2.setAttribute('class', 'orbital-satellite');
            sat2.setAttribute('r', '3');
            sat2.setAttribute('fill', '#FFFFFF');
            sat2.setAttribute('cx', '200');
            sat2.setAttribute('cy', '290');
            sat2.setAttribute('filter', 'drop-shadow(0 0 6px #FFFFFF)');
            svgWireframe.appendChild(sat2);

            // Parametric orbital animation loop for satellites
            let satAngle1 = 0;
            let satAngle2 = Math.PI;

            function animateSatellites() {
                satAngle1 += 0.016;
                satAngle2 -= 0.021;

                // Orbit 1: rx=180, ry=85, rotated -25deg around (200, 200)
                const rad1 = -25 * (Math.PI / 180);
                const x1Raw = Math.cos(satAngle1) * 180;
                const y1Raw = Math.sin(satAngle1) * 85;
                const x1 = 200 + x1Raw * Math.cos(rad1) - y1Raw * Math.sin(rad1);
                const y1 = 200 + x1Raw * Math.sin(rad1) + y1Raw * Math.cos(rad1);
                sat1.setAttribute('cx', x1);
                sat1.setAttribute('cy', y1);

                // Orbit 2: rx=175, ry=90, rotated +38deg around (200, 200)
                const rad2 = 38 * (Math.PI / 180);
                const x2Raw = Math.cos(satAngle2) * 175;
                const y2Raw = Math.sin(satAngle2) * 90;
                const x2 = 200 + x2Raw * Math.cos(rad2) - y2Raw * Math.sin(rad2);
                const y2 = 200 + x2Raw * Math.sin(rad2) + y2Raw * Math.cos(rad2);
                sat2.setAttribute('cx', x2);
                sat2.setAttribute('cy', y2);

                requestAnimationFrame(animateSatellites);
            }
            animateSatellites();
        }

        // Mouse 3D Tilt and Parallax Interaction on Desktop
        let mouseX = 0, mouseY = 0;
        let currentTiltX = 0, currentTiltY = 0;
        let isHovered = false;

        heroRightCol.addEventListener('mouseenter', () => {
            isHovered = true;
            wireframeWrap.classList.remove('hero-orbital-float'); // Pause float while interacting
        });

        heroRightCol.addEventListener('mousemove', (e) => {
            const rect = heroRightCol.getBoundingClientRect();
            const relX = e.clientX - rect.left;
            const relY = e.clientY - rect.top;

            // Normalized -1 to +1
            mouseX = (relX / rect.width) * 2 - 1;
            mouseY = (relY / rect.height) * 2 - 1;

            // Update pointer glow position
            if (pointerGlow) {
                pointerGlow.style.left = `${relX}px`;
                pointerGlow.style.top = `${relY}px`;
            }
        });

        heroRightCol.addEventListener('mouseleave', () => {
            isHovered = false;
            mouseX = 0;
            mouseY = 0;
            wireframeWrap.classList.add('hero-orbital-float'); // Resume float
        });

        // Smooth Lerp Tilt Animation Loop
        function render3DTilt() {
            if (!prefersReducedMotion) {
                const targetTiltX = isHovered ? -mouseY * 18 : 0;
                const targetTiltY = isHovered ? mouseX * 18 : 0;

                currentTiltX += (targetTiltX - currentTiltX) * 0.12;
                currentTiltY += (targetTiltY - currentTiltY) * 0.12;

                wireframeWrap.style.transform = `rotateX(${currentTiltX.toFixed(2)}deg) rotateY(${currentTiltY.toFixed(2)}deg)`;
            }
            requestAnimationFrame(render3DTilt);
        }
        render3DTilt();
    }

    })();
