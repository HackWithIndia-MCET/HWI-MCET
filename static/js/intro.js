/**
 * HackWithIndia × MCET — Premium 14.5-Second Immersive Cinematic Brand Intro
 * STRICTLY NO LOADING INDICATORS / NO SPINNERS / NO PERCENTAGES / NO PROGRESS BARS
 * Visual Identity Reference: Deep Black (#080808), Electric Red (#F32936), Off-White (#F5F3EF)
 * Technologies: Three.js + WebGL Fluid Shader Ribbons + 3D Particle Engine + GSAP Timeline + SVG
 */

(function () {
    'use strict';

    const STORAGE_KEY = 'hwi_mcet_intro_seen';
    let isIntroActive = false;
    let mainTl = null;
    let visualEngine = null;

    function shouldPlayIntro() {
        // Respect prefers-reduced-motion
        if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            return false;
        }

        // Allow force replay via URL param (?intro=1 or ?replay=1)
        const params = new URLSearchParams(window.location.search);
        if (params.get('intro') === '1' || params.get('replay') === '1') {
            return true;
        }

        // The website UI is always visible by default.
        // Intro triggers when explicitly requested via ?intro=1 or ?replay=1 or the Replay button
        return false;
    }

    function initIntro(force = false) {
        const overlay = document.getElementById('cinematic-intro');
        if (!overlay) return;

        if (!force && !shouldPlayIntro()) {
            overlay.classList.add('intro-hidden');
            document.body.classList.remove('intro-active');

        // Guarantee hero headline is 100% visible when intro finishes
        const heroH1 = document.querySelector('#hero h1');
        if (heroH1) {
            heroH1.style.opacity = '1';
            heroH1.style.visibility = 'visible';
            heroH1.style.transform = 'none';
            heroH1.querySelectorAll('*').forEach(el => {
                el.style.opacity = '1';
                el.style.visibility = 'visible';
                el.style.transform = 'none';
            });
        }
            return;
        }

        // Hard failsafe: guarantee intro NEVER blocks UI for more than 15s under any condition
        setTimeout(() => {
            if (isIntroActive) {
                console.warn('[Intro] Failsafe timer fired, dismissing intro');
                finishIntro(true);
            }
        }, 15000);

        isIntroActive = true;
        document.body.classList.add('intro-active');
        overlay.classList.remove('intro-hidden');

        // Setup Skip Button & ESC Hotkey
        const skipBtn = document.getElementById('intro-skip-btn');
        if (skipBtn) {
            skipBtn.addEventListener('click', () => skipIntro(true));
        }
        window.addEventListener('keydown', handleKeyDown);

        // Start Visual Engine (Three.js WebGL Fluid Ribbons & 3D Particles, with 2D fallback)
        const canvas = document.getElementById('intro-webgl-canvas');
        if (canvas) {
            if (typeof THREE !== 'undefined') {
                try {
                    visualEngine = initWebGLFluidEngine(canvas);
                } catch (err) {
                    console.warn('[Intro] WebGL init fallback:', err);
                    visualEngine = initCanvas2DFallback(canvas);
                }
            } else {
                visualEngine = initCanvas2DFallback(canvas);
            }
        }

        // Build & Run Master 14.5-Second GSAP Timeline
        if (typeof gsap !== 'undefined') {
            mainTl = build14SecondTimeline();
            mainTl.play();
        } else {
            setTimeout(() => finishIntro(false), 14500);
        }
    }

    // ================= MASTER 14.5-SECOND GSAP TIMELINE =================
    function build14SecondTimeline() {
        const tl = gsap.timeline({
            onComplete: () => finishIntro(false)
        });

        // Reset any initial styles
        gsap.set('.intro-grid', { opacity: 0 });
        gsap.set('.intro-ambient-bloom', { opacity: 0, scale: 0.6 });
        gsap.set('.intro-tag', { opacity: 0, y: 8 });
        gsap.set('.intro-skip-btn', { opacity: 0 });
        gsap.set('.intro-orbit-svg', { opacity: 0, scale: 0.9 });
        gsap.set('.intro-star-wrap', { opacity: 0, scale: 0.3, rotation: -90 });
        gsap.set('.intro-lockup', { opacity: 0, y: 15 });
        gsap.set('.intro-word-hwi', { opacity: 0, y: 30, scale: 0.92 });
        gsap.set('.intro-symbol-cross', { opacity: 0, scale: 0.1, rotation: -90 });
        gsap.set('.intro-word-mcet', { opacity: 0, y: 30, x: 20, scale: 0.92 });
        gsap.set('.intro-light-sweep', { opacity: 0, backgroundPosition: '-150% 0' });
        gsap.set('.intro-sub-block', { opacity: 0, y: 14 });

        // ----------------------------------------------------
        // PHASE 1: DARK ATMOSPHERE (0.0s – 2.0s)
        // Black screen, subtle grid, center glow, corner HUD
        // ----------------------------------------------------
        tl.to('.intro-grid', {
            opacity: 1,
            duration: 1.8,
            ease: 'power2.out'
        }, 0.2);

        tl.to('.intro-ambient-bloom', {
            opacity: 0.85,
            scale: 1,
            duration: 2.0,
            ease: 'power2.out'
        }, 0.4);

        tl.to('.intro-tag', {
            opacity: 1,
            y: 0,
            duration: 1.0,
            stagger: 0.12,
            ease: 'power2.out'
        }, 0.6);

        tl.to('.intro-skip-btn', {
            opacity: 1,
            duration: 0.8,
            ease: 'power2.out'
        }, 0.8);

        // Notify visual engine: Phase 1 (Atmosphere)
        tl.to({}, {
            duration: 2.0,
            onUpdate: function () {
                if (visualEngine && visualEngine.setPhase) {
                    visualEngine.setPhase(1, this.progress());
                }
            }
        }, 0);

        // ----------------------------------------------------
        // PHASE 2: FLUID MECHANICS (2.0s – 6.0s)
        // Red liquid ribbons flow from both sides, organic waves,
        // particles float and merge, thin orbital curves in background
        // ----------------------------------------------------
        tl.to('.intro-orbit-svg', {
            opacity: 0.45,
            scale: 1,
            duration: 2.5,
            ease: 'power2.out'
        }, 2.4);

        tl.to('.intro-ambient-bloom', {
            opacity: 1,
            scale: 1.15,
            duration: 3.5,
            ease: 'sine.inOut'
        }, 2.0);

        // Dynamic fluid ribbon wave expansion driven into WebGL engine
        tl.to({}, {
            duration: 4.0,
            onUpdate: function () {
                if (visualEngine && visualEngine.setPhase) {
                    visualEngine.setPhase(2, this.progress());
                }
            }
        }, 2.0);

        // ----------------------------------------------------
        // PHASE 3: ORBITAL FORMATION & GEOMETRIC STAR (6.0s – 9.0s)
        // Fluid ribbons converge to center, orbital curves accelerate,
        // particles follow orbits, fluid crystallizes into 8-spoke star,
        // controlled red energy pulse fires
        // ----------------------------------------------------
        tl.to('.intro-orbit-svg', {
            opacity: 0.85,
            duration: 1.5,
            ease: 'power2.inOut'
        }, 6.0);

        // Star structure forms in center inspired by homepage 3D asterisk
        tl.to('.intro-star-wrap', {
            opacity: 1,
            scale: 1,
            rotation: 0,
            duration: 2.2,
            ease: 'back.out(1.4)'
        }, 6.2);

        // Inform engine of Phase 3 convergence
        tl.to({}, {
            duration: 3.0,
            onUpdate: function () {
                if (visualEngine && visualEngine.setPhase) {
                    visualEngine.setPhase(3, this.progress());
                }
            }
        }, 6.0);

        // Controlled Red Energy Pulse Shockwave (8.6s – 9.8s)
        tl.fromTo('.intro-energy-ring', {
            scale: 0.2,
            opacity: 0.95
        }, {
            scale: 2.6,
            opacity: 0,
            duration: 1.2,
            ease: 'power2.out'
        }, 8.6);

        // ----------------------------------------------------
        // PHASE 4: BRAND REVEAL (9.0s – 12.0s)
        // Exact Sequence:
        // 1. HWI in bold off-white typography (9.0s)
        // 2. Bright red × forms between words (9.8s)
        // 3. MCET reveals with directional motion (10.5s)
        // Final Title: HWI × MCET + Red light sweep
        // ----------------------------------------------------
        // Star gently flattens/dissolves into the lockup
        tl.to('.intro-star-wrap', {
            scale: 0.7,
            opacity: 0.25,
            duration: 0.8,
            ease: 'power2.in'
        }, 8.8);

        tl.to('.intro-lockup', {
            opacity: 1,
            y: 0,
            duration: 0.3
        }, 9.0);

        // 1. Reveal HWI
        tl.to('.intro-word-hwi', {
            opacity: 1,
            y: 0,
            scale: 1,
            duration: 0.85,
            ease: 'power3.out'
        }, 9.0);

        // 2. Bright Red Cross (×)
        tl.to('.intro-symbol-cross', {
            opacity: 1,
            scale: 1,
            rotation: 0,
            duration: 0.65,
            ease: 'back.out(2)'
        }, 9.8);

        // 3. Reveal MCET
        tl.to('.intro-word-mcet', {
            opacity: 1,
            y: 0,
            x: 0,
            scale: 1,
            duration: 0.85,
            ease: 'power3.out'
        }, 10.5);

        // Cinematic Red Light Sweep across HWI × MCET
        tl.fromTo('.intro-light-sweep', {
            opacity: 0,
            backgroundPosition: '-150% 0'
        }, {
            opacity: 1,
            backgroundPosition: '250% 0',
            duration: 1.3,
            ease: 'power2.inOut'
        }, 11.0);

        // Engine Phase 4: Embers hovering around lockup
        tl.to({}, {
            duration: 3.0,
            onUpdate: function () {
                if (visualEngine && visualEngine.setPhase) {
                    visualEngine.setPhase(4, this.progress());
                }
            }
        }, 9.0);

        // ----------------------------------------------------
        // PHASE 5: BRAND IDENTIFICATION & HOMEPAGE TRANSITION (12.0s – 14.5s)
        // Display: HACKWITHINDIA / MCET CHAPTER
        // Orbital curves slowly move outward, ribbons dissolve into particles,
        // seamless dissolve into existing homepage
        // ----------------------------------------------------
        tl.to('.intro-sub-block', {
            opacity: 1,
            y: 0,
            duration: 0.9,
            ease: 'power2.out'
        }, 12.0);

        // Outward expansion of orbital curves
        tl.to('.intro-orbit-svg', {
            scale: 1.35,
            opacity: 0,
            duration: 1.4,
            ease: 'power2.in'
        }, 13.2);

        // Star fades away completely
        tl.to('.intro-star-wrap', {
            opacity: 0,
            scale: 0.4,
            duration: 0.8
        }, 13.0);

        // Engine Phase 5: Outward particle dispersal & fluid dissolve
        tl.to({}, {
            duration: 1.5,
            onStart: () => {
                if (visualEngine && visualEngine.disperse) {
                    visualEngine.disperse();
                }
            },
            onUpdate: function () {
                if (visualEngine && visualEngine.setPhase) {
                    visualEngine.setPhase(5, this.progress());
                }
            }
        }, 13.2);

        // Dissolve intro stage
        tl.to('.intro-stage', {
            scale: 1.06,
            y: -10,
            opacity: 0,
            filter: 'blur(10px)',
            duration: 1.3,
            ease: 'power2.in'
        }, 13.3);

        // Dissolve base overlay directly into the homepage hero
        tl.to('#cinematic-intro', {
            opacity: 0,
            duration: 1.3,
            ease: 'power2.inOut'
        }, 13.3);

        return tl;
    }

    function finishIntro(fast = false) {
        if (!isIntroActive) return;
        isIntroActive = false;

        if (mainTl) {
            mainTl.kill();
            mainTl = null;
        }

        window.removeEventListener('keydown', handleKeyDown);

        if (visualEngine && visualEngine.dispose) {
            visualEngine.dispose();
            visualEngine = null;
        }

        try {
            sessionStorage.setItem(STORAGE_KEY, 'true');
        } catch (e) {}

        const overlay = document.getElementById('cinematic-intro');
        if (!overlay) {
            document.body.classList.remove('intro-active');
            return;
        }

        document.body.classList.remove('intro-active');

        if (fast) {
            overlay.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        }
        overlay.classList.add('intro-fade-out');

        setTimeout(() => {
            overlay.classList.add('intro-hidden');
        }, fast ? 320 : 1400);
    }

    function skipIntro(fast = true) {
        finishIntro(fast);
    }

    function handleKeyDown(e) {
        if (e.key === 'Escape' || e.keyCode === 27) {
            skipIntro(true);
        }
    }

    // ================= THREE.JS + WEBGL FLUID RIBBONS & 3D PARTICLE ENGINE =================
    function initWebGLFluidEngine(canvas) {
        let width = canvas.clientWidth || window.innerWidth;
        let height = canvas.clientHeight || window.innerHeight;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 100);
        camera.position.z = 6.0;

        const renderer = new THREE.WebGLRenderer({
            canvas: canvas,
            alpha: true,
            antialias: true,
            powerPreference: 'high-performance'
        });
        renderer.setSize(width, height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

        // -----------------------------------------------------------------
        // 1. GLSL Shaders for Organic Flowing Liquid Ribbons (Dual Left & Right)
        // -----------------------------------------------------------------
        const fluidVertexShader = `
            precision highp float;
            uniform float uTime;
            uniform float uPhase;
            uniform float uFlow;
            uniform float uConvergence;
            varying vec2 vUv;
            varying float vElevation;

            void main() {
                vUv = uv;
                vec3 pos = position;

                // Organic fluid wave undulation
                float wave1 = sin(pos.x * 2.2 + uTime * 2.1) * 0.22;
                float wave2 = cos(pos.y * 3.1 + uTime * 1.6) * 0.18;
                float wave3 = sin((pos.x + pos.y) * 1.8 + uTime * 2.8) * 0.14;
                float elevation = (wave1 + wave2 + wave3) * uFlow;

                pos.z += elevation;
                pos.y += sin(pos.x * 2.8 + uTime * 1.8) * 0.16 * uFlow;

                // Convergence toward center during Phase 3
                if (uConvergence > 0.0) {
                    pos.x = mix(pos.x, pos.x * 0.35, uConvergence);
                    pos.y = mix(pos.y, pos.y * 0.35, uConvergence);
                }

                vElevation = elevation;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
            }
        `;

        const fluidFragmentShader = `
            precision highp float;
            uniform float uTime;
            uniform float uOpacity;
            uniform float uDissolve;
            varying vec2 vUv;
            varying float vElevation;

            void main() {
                // Dual edge falloff for smooth ribbon borders
                float edgeFadeX = smoothstep(0.0, 0.18, vUv.x) * (1.0 - smoothstep(0.82, 1.0, vUv.x));
                float edgeFadeY = smoothstep(0.0, 0.22, vUv.y) * (1.0 - smoothstep(0.78, 1.0, vUv.y));
                float ribbonMask = edgeFadeX * edgeFadeY;

                // Fluid color spectrum: Electric Red core, deep crimson velvet edges, hot specular gleam
                vec3 deepVelvet = vec3(0.33, 0.03, 0.05);   // #54080D
                vec3 electricRed = vec3(0.95, 0.16, 0.21);  // #F32936
                vec3 hotSpecular = vec3(1.0, 0.65, 0.70);   // Hot light scattering

                float normalFactor = clamp((vElevation + 0.3) * 1.8, 0.0, 1.0);
                vec3 fluidColor = mix(deepVelvet, electricRed, normalFactor);

                // Add specular light glint
                float glint = pow(clamp(sin(vUv.x * 12.0 + uTime * 3.0 + vElevation * 4.0), 0.0, 1.0), 5.0);
                fluidColor += hotSpecular * glint * 0.35;

                float alpha = ribbonMask * uOpacity * (1.0 - uDissolve);
                if (alpha < 0.005) discard;

                gl_FragColor = vec4(fluidColor, alpha);
            }
        `;

        // Create Left and Right Fluid Ribbon Planes
        const ribbonGeo = new THREE.PlaneGeometry(5.2, 1.8, 96, 48);
        const fluidUniforms = {
            uTime: { value: 0 },
            uPhase: { value: 1.0 },
            uFlow: { value: 0.0 },
            uConvergence: { value: 0.0 },
            uOpacity: { value: 0.0 },
            uDissolve: { value: 0.0 }
        };

        const fluidMaterial = new THREE.ShaderMaterial({
            vertexShader: fluidVertexShader,
            fragmentShader: fluidFragmentShader,
            uniforms: fluidUniforms,
            transparent: true,
            side: THREE.DoubleSide,
            depthWrite: false,
            blending: THREE.AdditiveBlending
        });

        // Left fluid ribbon
        const ribbonLeft = new THREE.Mesh(ribbonGeo, fluidMaterial);
        ribbonLeft.position.set(-2.2, 0.2, 0);
        ribbonLeft.rotation.z = 0.15;
        scene.add(ribbonLeft);

        // Right fluid ribbon
        const ribbonRight = new THREE.Mesh(ribbonGeo, fluidMaterial.clone());
        ribbonRight.position.set(2.2, -0.2, 0);
        ribbonRight.rotation.z = -0.15;
        ribbonRight.rotation.y = Math.PI;
        scene.add(ribbonRight);

        // -----------------------------------------------------------------
        // 2. 3D Particle Swarm & Geometric Fragments (1,200 Particles)
        // -----------------------------------------------------------------
        const particleCount = 1200;
        const particleGeo = new THREE.BufferGeometry();
        const posArray = new Float32Array(particleCount * 3);
        const originArray = new Float32Array(particleCount * 3);
        const colorArray = new Float32Array(particleCount * 3);
        const sizeArray = new Float32Array(particleCount);
        const phaseArray = new Float32Array(particleCount);

        const colorElectric = new THREE.Color('#F32936');
        const colorCrimson = new THREE.Color('#B31A1A');
        const colorWhite = new THREE.Color('#F5F3EF');

        for (let i = 0; i < particleCount; i++) {
            const i3 = i * 3;
            // Distribute across 3D space with slight bias toward the center
            const radius = Math.pow(Math.random(), 1.6) * 5.5;
            const angle = Math.random() * Math.PI * 2;
            const z = (Math.random() - 0.5) * 4.0;

            posArray[i3] = Math.cos(angle) * radius;
            posArray[i3 + 1] = Math.sin(angle) * (radius * 0.65);
            posArray[i3 + 2] = z;

            originArray[i3] = posArray[i3];
            originArray[i3 + 1] = posArray[i3 + 1];
            originArray[i3 + 2] = z;

            // Palette mix: 75% red, 15% dark crimson, 10% off-white sparkles
            const roll = Math.random();
            let c;
            if (roll < 0.75) c = colorElectric;
            else if (roll < 0.90) c = colorCrimson;
            else c = colorWhite;

            colorArray[i3] = c.r;
            colorArray[i3 + 1] = c.g;
            colorArray[i3 + 2] = c.b;

            sizeArray[i] = Math.random() * 3.2 + 1.2;
            phaseArray[i] = Math.random() * Math.PI * 2;
        }

        particleGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
        particleGeo.setAttribute('color', new THREE.BufferAttribute(colorArray, 3));
        particleGeo.setAttribute('size', new THREE.BufferAttribute(sizeArray, 1));

        // Soft circular particle texture generated via 2D Canvas
        const pCanvas = document.createElement('canvas');
        pCanvas.width = 32;
        pCanvas.height = 32;
        const pCtx = pCanvas.getContext('2d');
        const grad = pCtx.createRadialGradient(16, 16, 0, 16, 16, 16);
        grad.addColorStop(0, 'rgba(255, 255, 255, 1)');
        grad.addColorStop(0.35, 'rgba(243, 41, 54, 0.9)');
        grad.addColorStop(0.7, 'rgba(243, 41, 54, 0.25)');
        grad.addColorStop(1, 'rgba(243, 41, 54, 0)');
        pCtx.fillStyle = grad;
        pCtx.fillRect(0, 0, 32, 32);

        const particleTexture = new THREE.CanvasTexture(pCanvas);

        const particleMaterial = new THREE.PointsMaterial({
            size: 0.08,
            vertexColors: true,
            map: particleTexture,
            transparent: true,
            opacity: 0.85,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });

        const particleSystem = new THREE.Points(particleGeo, particleMaterial);
        scene.add(particleSystem);

        // -----------------------------------------------------------------
        // Dynamic Controls and Animation Loop
        // -----------------------------------------------------------------
        let clock = new THREE.Clock();
        let animId = null;
        let currentPhase = 1;
        let phaseProgress = 0;
        let isDispersing = false;

        function animate() {
            animId = requestAnimationFrame(animate);
            const delta = clock.getDelta();
            const elapsed = clock.getElapsedTime();

            // Update Fluid Ribbon Uniforms
            fluidMaterial.uniforms.uTime.value = elapsed;
            ribbonRight.material.uniforms.uTime.value = elapsed;

            if (currentPhase === 1) {
                // Phase 1: Gentle initial atmosphere
                fluidMaterial.uniforms.uFlow.value = phaseProgress * 0.3;
                fluidMaterial.uniforms.uOpacity.value = phaseProgress * 0.3;
                ribbonRight.material.uniforms.uFlow.value = phaseProgress * 0.3;
                ribbonRight.material.uniforms.uOpacity.value = phaseProgress * 0.3;
            } else if (currentPhase === 2) {
                // Phase 2: Dynamic surge of fluid ribbons from sides
                const flow = 0.3 + phaseProgress * 0.7;
                fluidMaterial.uniforms.uFlow.value = flow;
                fluidMaterial.uniforms.uOpacity.value = Math.min(1.0, 0.4 + phaseProgress * 0.6);
                ribbonRight.material.uniforms.uFlow.value = flow;
                ribbonRight.material.uniforms.uOpacity.value = Math.min(1.0, 0.4 + phaseProgress * 0.6);
            } else if (currentPhase === 3) {
                // Phase 3: Ribbons converge toward center
                fluidMaterial.uniforms.uConvergence.value = phaseProgress;
                ribbonRight.material.uniforms.uConvergence.value = phaseProgress;
                fluidMaterial.uniforms.uFlow.value = 1.0 - phaseProgress * 0.3;
                ribbonRight.material.uniforms.uFlow.value = 1.0 - phaseProgress * 0.3;
            } else if (currentPhase >= 4) {
                // Phase 4 & 5: Ribbons dissolve into glowing embers
                const dissolve = (currentPhase === 5) ? Math.min(1.0, phaseProgress * 1.5) : 0.35;
                fluidMaterial.uniforms.uDissolve.value = dissolve;
                ribbonRight.material.uniforms.uDissolve.value = dissolve;
            }

            // Animate 3D Particles based on Phase
            const positions = particleGeo.attributes.position.array;

            for (let i = 0; i < particleCount; i++) {
                const i3 = i * 3;
                const pPhase = phaseArray[i];

                if (isDispersing) {
                    // Outward high-speed dispersal during final transition
                    positions[i3] *= 1.035;
                    positions[i3 + 1] *= 1.035;
                    positions[i3 + 2] += (Math.sin(pPhase) * 0.08);
                } else if (currentPhase <= 2) {
                    // Ambient drift with subtle fluid velocity field
                    positions[i3] += Math.sin(elapsed * 0.8 + pPhase) * 0.003;
                    positions[i3 + 1] += Math.cos(elapsed * 0.7 + pPhase) * 0.003;
                    positions[i3 + 2] += Math.sin(elapsed * 0.5 + pPhase) * 0.002;
                } else if (currentPhase === 3) {
                    // Orbital swirl around the forming geometric star
                    const x = positions[i3];
                    const y = positions[i3 + 1];
                    const dist = Math.sqrt(x * x + y * y) + 0.001;
                    const speed = 0.025 / Math.max(0.5, dist);
                    const newAngle = Math.atan2(y, x) + speed;
                    const pull = (dist - 1.8) * 0.015;

                    positions[i3] = Math.cos(newAngle) * (dist - pull);
                    positions[i3 + 1] = Math.sin(newAngle) * (dist - pull) * 0.85;
                } else if (currentPhase >= 4) {
                    // Peaceful embers hovering around typography
                    positions[i3] += Math.sin(elapsed * 0.6 + pPhase) * 0.002;
                    positions[i3 + 1] += Math.cos(elapsed * 0.5 + pPhase) * 0.002;
                }
            }

            particleGeo.attributes.position.needsUpdate = true;
            particleSystem.rotation.z = elapsed * 0.04;

            renderer.render(scene, camera);
        }

        animate();

        // Responsive Resizing
        function onWindowResize() {
            width = canvas.clientWidth || window.innerWidth;
            height = canvas.clientHeight || window.innerHeight;
            camera.aspect = width / height;
            camera.updateProjectionMatrix();
            renderer.setSize(width, height);
        }
        window.addEventListener('resize', onWindowResize);

        return {
            setPhase: (phaseNum, progress) => {
                currentPhase = phaseNum;
                phaseProgress = Math.max(0, Math.min(1, progress));
            },
            disperse: () => {
                isDispersing = true;
                if (particleMaterial) {
                    gsap.to(particleMaterial, { opacity: 0, duration: 1.4, ease: 'power2.in' });
                }
            },
            dispose: () => {
                if (animId) cancelAnimationFrame(animId);
                window.removeEventListener('resize', onWindowResize);
                ribbonGeo.dispose();
                fluidMaterial.dispose();
                ribbonRight.material.dispose();
                particleGeo.dispose();
                particleMaterial.dispose();
                particleTexture.dispose();
                renderer.dispose();
            }
        };
    }

    // ================= 2D PROCEDURAL CANVAS FALLBACK =================
    function initCanvas2DFallback(canvas) {
        const ctx = canvas.getContext('2d');
        if (!ctx) return null;

        let width = canvas.width = window.innerWidth;
        let height = canvas.height = window.innerHeight;
        let animId = null;
        let currentPhase = 1;
        let phaseProgress = 0;
        let isDispersing = false;

        const particles = [];
        for (let i = 0; i < 180; i++) {
            particles.push({
                x: Math.random() * width,
                y: Math.random() * height,
                vx: (Math.random() - 0.5) * 0.8,
                vy: (Math.random() - 0.5) * 0.8,
                radius: Math.random() * 2.5 + 1.0,
                alpha: Math.random() * 0.7 + 0.3,
                color: Math.random() > 0.15 ? '#F32936' : '#F5F3EF'
            });
        }

        let time = 0;
        function render() {
            animId = requestAnimationFrame(render);
            time += 0.016;

            ctx.clearRect(0, 0, width, height);

            // Flowing fluid sine wave ribbons (Fallback)
            if (currentPhase >= 2) {
                const waveAlpha = Math.min(0.35, currentPhase === 2 ? phaseProgress * 0.35 : 0.25);
                ctx.fillStyle = `rgba(243, 41, 54, ${waveAlpha})`;
                ctx.beginPath();
                ctx.moveTo(0, height * 0.5);
                for (let x = 0; x <= width; x += 20) {
                    const y = height * 0.5 + Math.sin(x * 0.005 + time * 1.5) * 50 + Math.cos(x * 0.003 - time) * 35;
                    ctx.lineTo(x, y);
                }
                ctx.lineTo(width, height);
                ctx.lineTo(0, height);
                ctx.closePath();
                ctx.fill();
            }

            // Draw particles
            particles.forEach(p => {
                if (isDispersing) {
                    p.x += (p.x - width / 2) * 0.04;
                    p.y += (p.y - height / 2) * 0.04;
                    p.alpha *= 0.96;
                } else {
                    p.x += p.vx;
                    p.y += p.vy;
                    if (p.x < 0) p.x = width;
                    if (p.x > width) p.x = 0;
                    if (p.y < 0) p.y = height;
                    if (p.y > height) p.y = 0;
                }

                ctx.save();
                ctx.globalAlpha = p.alpha;
                ctx.fillStyle = p.color;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            });
        }
        render();

        function onResize() {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', onResize);

        return {
            setPhase: (p, prog) => { currentPhase = p; phaseProgress = prog; },
            disperse: () => { isDispersing = true; },
            dispose: () => {
                if (animId) cancelAnimationFrame(animId);
                window.removeEventListener('resize', onResize);
            }
        };
    }

    // Public Replay Method for presentation / testing
    window.replayIntro = function () {
        document.body.classList.add('intro-active');
        const overlay = document.getElementById('cinematic-intro');
        if (overlay) {
            overlay.classList.remove('intro-hidden', 'intro-fade-out');
            overlay.style.display = 'flex';
            overlay.style.opacity = '1';
            overlay.style.transform = 'none';

            const stage = overlay.querySelector('.intro-stage');
            if (stage) {
                stage.style.opacity = '1';
                stage.style.transform = 'none';
                stage.style.filter = 'none';
            }
        }
        initIntro(true);
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initIntro);
    } else {
        initIntro();
    }
})();
