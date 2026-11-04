/**
 * Hack with India — MCET Chapter
 * Dark Cyberpunk Editorial Application Logic
 * Integrates: Real DB Sessions, Team Registration, Allotment Pass,
 * Winning Parameters, Mid-Hack Games, Genuine Attendee Feedback, and Organiser Desk.
 */

// Global State
let cachedStats = {};
let typingStartTime = null;
let typingSnippetText = "";

document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadSessions();
    if (document.getElementById('leaderboard-body')) loadLeaderboard();
    if (document.getElementById('feedbacks-stream')) loadFeedbacks();
    if (document.getElementById('summary-avg-rating')) loadFeedbackSummary();
    if (document.getElementById('blog-container')) loadBlog();
    if (document.getElementById('games-container')) loadGames();
    if (document.getElementById('admin-teams-table')) loadAdminTeams();
    if (document.getElementById('sim-inno')) initSimulator();

    // Auto-refresh stats periodically if counter elements exist
    if (document.getElementById('admin-presenties-counter')) {
        setInterval(loadStats, 30000);
    }
});

// Mobile Navigation Toggle
function toggleMobileMenu() {
    const nav = document.getElementById('mobile-nav');
    if (nav) {
        nav.classList.toggle('hidden');
    }
}

// Clean Toast Notification with Red Cyberpunk Theme
function showToast(title, message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    const borderColors = {
        success: 'border-[#FF2A2A] bg-[#111114] text-white shadow-2xl',
        error: 'border-red-600 bg-[#160b0b] text-white shadow-2xl',
        info: 'border-zinc-700 bg-[#111114] text-white shadow-2xl'
    };

    const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
    const iconColor = type === 'success' ? 'text-[#FF2A2A] bg-red-950/40 border border-red-500/30' : type === 'error' ? 'text-red-500 bg-red-950/60 border border-red-500/40' : 'text-zinc-400 bg-zinc-900 border border-zinc-700';

    toast.className = `p-4 rounded-[3px] border-l-4 border transition-all duration-300 transform translate-y-2 opacity-0 flex items-start gap-3 ${borderColors[type] || borderColors.info}`;
    toast.innerHTML = `
        <div class="w-6 h-6 rounded flex items-center justify-center font-bold text-xs flex-shrink-0 ${iconColor}">
            ${icon}
        </div>
        <div>
            <h4 class="font-headline font-bold text-xs uppercase tracking-wider text-white">${title}</h4>
            <p class="text-xs text-zinc-400 mt-0.5 leading-relaxed font-normal">${message}</p>
        </div>
    `;

    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.remove('translate-y-2', 'opacity-0');
    }, 10);

    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-2');
        setTimeout(() => toast.remove(), 300);
    }, 4500);
}

// Confetti Trigger
function triggerConfetti() {
    if (typeof confetti === 'function') {
        confetti({
            particleCount: 50,
            spread: 60,
            origin: { y: 0.6 },
            colors: ['#FF2A2A', '#FFFFFF', '#111114']
        });
    }
}

// Load Global Database Statistics
async function loadStats() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        cachedStats = data;

        const adminCounter = document.getElementById('admin-presenties-counter');
        if (adminCounter) adminCounter.innerText = `${data.present_count} Present / ${data.total_registered} Registered`;

    } catch (err) {
        console.error("Error loading stats:", err);
    }
}

// Quick Fill Demo Data (Removed to prevent fabricated data entry)
function quickFillDemo() {
    showToast("Notice", "Demo data injection has been removed. Please enter genuine team details.", "info");
}

// Launch Spot Registration Desk
function launchSpotRegistrationWizard() {
    const regSection = document.getElementById('register');
    if (regSection) regSection.scrollIntoView({ behavior: 'smooth' });

    const form = document.getElementById('human-registration-form');
    if (form) form.reset();

    const isSpotInput = document.getElementById('reg-is-spot');
    if (isSpotInput) isSpotInput.value = "true";

    showToast("Spot Registration Mode", "Walk-in mode active. Fill in authentic team details for on-desk allotment.", "info");
}

// Handle Team Registration Submission
async function handleRegistrationSubmit(event) {
    event.preventDefault();

    const submitBtn = document.getElementById('reg-submit-btn');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = 'Registering team...';
    }

    const isSpot = document.getElementById('reg-is-spot').value === "true";
    const team_name = document.getElementById('reg-team-name').value.trim();
    const lead_name = document.getElementById('reg-lead-name').value.trim();
    const lead_email = document.getElementById('reg-lead-email').value.trim();
    const lead_phone = document.getElementById('reg-lead-phone').value.trim();
    const college = document.getElementById('reg-college').value.trim() || "MCET Campus";
    const track = document.getElementById('reg-track').value;
    const mode = document.getElementById('reg-mode').value;
    const membersRaw = document.getElementById('reg-members').value.trim();

    const members = membersRaw ? membersRaw.split('\n').map(m => m.trim()).filter(Boolean) : [lead_name];

    const payload = {
        team_name,
        lead_name,
        lead_email,
        lead_phone,
        college,
        track,
        members,
        mode,
        is_spot_registration: isSpot
    };

    try {
        const endpoint = isSpot ? '/api/spot-register' : '/api/register';
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok) {
            showToast("Registration Error", data.detail || "Could not complete registration", "error");
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Submit registration ↗';
            }
            return;
        }

        triggerConfetti();
        showToast("Registration Confirmed!", `Team ID: ${data.registration_id} allotted!`, "success");

        // Display allotment pass & scroll smoothly to Allotment section
        document.getElementById('allotment-search-input').value = data.registration_id;
        displayAllotmentCard(data.registration_id);

        const allotmentSection = document.getElementById('allotment');
        if (allotmentSection) {
            allotmentSection.scrollIntoView({ behavior: 'smooth' });
        }

        // Reset
        document.getElementById('human-registration-form').reset();
        document.getElementById('reg-is-spot').value = "false";
        loadStats();
        loadLeaderboard();
        loadAdminTeams();

    } catch (err) {
        console.error("Error submitting registration:", err);
        showToast("Network Error", "Could not reach server", "error");
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Submit registration ↗';
        }
    }
}

// Allotment Search
async function lookupAllotment() {
    const input = document.getElementById('allotment-search-input');
    const regId = input.value.trim();
    if (!regId) {
        showToast("Input Required", "Please enter your Registration ID or Team Name", "error");
        return;
    }
    displayAllotmentCard(regId);
}

// Display Clean Allotment Pass & Guide
async function displayAllotmentCard(regId) {
    const cardContainer = document.getElementById('allotment-result-card');
    cardContainer.innerHTML = `
        <div class="cyber-card p-8 text-center">
            <div class="animate-spin inline-block w-5 h-5 border-2 border-[#FF2A2A] border-t-transparent rounded-full mb-2"></div>
            <p class="text-xs font-mono text-zinc-400">Retrieving campus pass details...</p>
        </div>
    `;

    try {
        const res = await fetch(`/api/allotment/${encodeURIComponent(regId)}`);
        const data = await res.json();

        if (!res.ok) {
            cardContainer.innerHTML = `
                <div class="cyber-card p-6 text-center border-red-900/50 bg-[#160b0b]">
                    <p class="text-xs font-mono font-bold text-[#FF2A2A] uppercase mb-1">Pass Not Found</p>
                    <p class="text-xs text-zinc-400 mb-3">${data.detail || 'No registration matching ' + regId}</p>
                    <a href="#register" class="btn-red text-xs py-1.5 px-4 inline-block">Register your team</a>
                </div>
            `;
            return;
        }

        cardContainer.innerHTML = `
            <div class="cyber-card overflow-hidden border border-white/20">
                <!-- Top Ribbon -->
                <div class="bg-black/90 p-5 border-b border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                        <div class="flex items-center gap-2 mb-1">
                            <span class="px-2 py-0.5 rounded font-mono text-xs font-bold bg-[#FF2A2A] text-white">
                                ${data.registration_id}
                            </span>
                            <span class="text-xs font-mono text-zinc-400">
                                ${data.mode} Mode
                            </span>
                            ${data.is_spot_registration ? '<span class="text-[9px] font-mono px-1.5 py-0.5 bg-zinc-800 text-zinc-300">Spot Walk-in</span>' : ''}
                        </div>
                        <h3 class="font-headline font-bold text-xl sm:text-2xl uppercase text-white tracking-tight">${data.team_name}</h3>
                        <p class="text-xs text-zinc-400 mt-0.5">Leader: <strong class="text-zinc-200">${data.lead_name}</strong> • ${data.lead_phone} • ${data.college}</p>
                    </div>

                    <div class="flex items-center gap-2">
                        <button onclick="window.print()" class="btn-outline-dark text-xs py-1.5 px-3">
                            🖨️ Print Pass
                        </button>
                    </div>
                </div>

                <!-- Desk & Mentor Details -->
                <div class="p-5 bg-black/40 border-b border-white/10 grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div class="p-3.5 rounded bg-[#101014] border border-white/5 space-y-1">
                        <div class="text-[10px] font-mono text-zinc-500 uppercase">Allocated Desk</div>
                        <div class="text-xs font-bold text-white">${data.lab_allotment}</div>
                        <div class="text-[10px] text-zinc-500">MCET Innovation Lab</div>
                    </div>

                    <div class="p-3.5 rounded bg-[#101014] border border-white/5 space-y-1">
                        <div class="text-[10px] font-mono text-zinc-500 uppercase">Assigned Mentor</div>
                        <div class="text-xs font-bold text-white">${data.mentor_name}</div>
                        <div class="text-[10px] text-zinc-500">${data.mentor_contact}</div>
                    </div>

                    <div class="p-3.5 rounded bg-[#101014] border border-white/5 space-y-1">
                        <div class="text-[10px] font-mono text-zinc-500 uppercase">Wi-Fi Access</div>
                        <div class="text-xs font-bold text-[#FF2A2A]">SSID: HWI_MCET_5G</div>
                        <div class="text-[10px] text-zinc-400 font-mono">Key: hackwithindia2026</div>
                    </div>
                </div>

                <!-- Team Members List -->
                <div class="p-5 border-b border-white/10">
                    <div class="text-[10px] font-mono font-bold text-zinc-400 uppercase tracking-wider mb-2">Team Roster</div>
                    <div class="flex flex-wrap gap-2">
                        ${data.members.map(m => `
                            <span class="px-2.5 py-1 rounded bg-white/5 border border-white/10 text-xs font-mono text-zinc-300">
                                👤 ${(typeof m === 'object' && m !== null) ? `${m.name}${m.email ? ' (' + m.email + ')' : ''}` : m}
                            </span>
                        `).join('')}
                    </div>
                </div>

                <!-- Onboarding Guide -->
                <div class="p-5 space-y-3">
                    <div class="flex items-center justify-between">
                        <h4 class="font-headline font-bold text-xs uppercase tracking-wider text-white">What To Do Next</h4>
                        <span class="text-[10px] font-mono text-zinc-500">Onboarding Checklist</span>
                    </div>

                    <div class="space-y-2">
                        ${data.guide.map((step, idx) => `
                            <div class="flex items-start gap-2.5 p-2 rounded bg-black/40 border border-white/5">
                                <input type="checkbox" id="guide-${idx}" class="mt-0.5 rounded accent-[#FF2A2A] cursor-pointer" />
                                <label for="guide-${idx}" class="text-xs text-zinc-300 cursor-pointer font-normal leading-relaxed">
                                    ${step}
                                </label>
                            </div>
                        `).join('')}
                    </div>
                </div>

            </div>
        `;

    } catch (err) {
        console.error("Error looking up allotment:", err);
    }
}

// Load Sessions from Database (with honest empty state)
async function loadSessions(category = 'All', mode = 'All') {
    const listEl = document.getElementById('sessions-timeline');
    if (!listEl) return;

    try {
        let url = `/api/sessions?`;
        if (category !== 'All') url += `category=${encodeURIComponent(category)}&`;
        if (mode !== 'All') url += `mode=${encodeURIComponent(mode)}&`;

        const res = await fetch(url);
        const sessions = await res.json();

        if (!sessions || sessions.length === 0) {
            listEl.innerHTML = `
                <a href="/events" class="cyber-card block p-6 sm:p-8 border-l-4 border-l-[#FF2A2A] border border-white/10 hover:border-[#FF2A2A]/60 bg-[#0C0C0F] hover:bg-[#111116] transition-all duration-300 group relative overflow-hidden shadow-xl">
                    <div class="absolute -top-16 -right-16 w-52 h-52 rounded-full bg-[#FF2A2A]/10 blur-3xl pointer-events-none group-hover:bg-[#FF2A2A]/20 transition-all duration-500"></div>
                    <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
                        <div class="space-y-2 max-w-2xl">
                            <div class="flex items-center gap-2 text-[11px] font-mono text-[#FF2A2A] tracking-[0.2em] uppercase">
                                <span class="w-2 h-2 rounded-full bg-[#FF2A2A] animate-pulse"></span>
                                <span>// 02. CHAPTER CALENDAR & SESSIONS</span>
                            </div>
                            <h3 class="font-headline font-extrabold text-2xl sm:text-3xl uppercase text-white tracking-tight group-hover:text-zinc-100 transition-colors">
                                Explore More Events & Workshops
                            </h3>
                            <p class="text-xs sm:text-sm text-zinc-400 font-normal leading-relaxed">
                                Browse our complete roster of upcoming inter-college hackathons, speaker keynotes, hands-on masterclasses, and builder sprints.
                            </p>
                        </div>
                        <div class="flex-shrink-0 flex items-center">
                            <span class="btn-red text-xs sm:text-sm py-3 px-6 sm:px-8 font-bold uppercase tracking-wider inline-flex items-center gap-2.5 shadow-lg group-hover:shadow-red-950/60 transition-all">
                                <span>Explore Events</span>
                                <span class="text-base transform group-hover:translate-x-1 transition-transform">→</span>
                            </span>
                        </div>
                    </div>
                </a>
            `;
            return;
        }

        listEl.innerHTML = sessions.map(s => {
            const isLive = (s.status === 'Live Now');
            const statusBadge = isLive 
                ? `<span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-red-950/80 text-[#FF2A2A] border border-red-500/30">● LIVE NOW</span>`
                : s.status === 'Completed'
                ? `<span class="px-2 py-0.5 rounded text-[10px] font-mono text-zinc-500 bg-white/5">COMPLETED</span>`
                : `<span class="px-2 py-0.5 rounded text-[10px] font-mono text-zinc-400 bg-white/5">UPCOMING</span>`;

            const customBadge = s.badge_text ? `
                <span class="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-[#FF2A2A]/15 text-[#FF2A2A] border border-[#FF2A2A]/40 uppercase tracking-wider">
                    ★ ${s.badge_text}
                </span>
            ` : '';

            const imageHtml = (s.image_url && s.image_url.trim()) ? `
                <div class="w-full sm:w-48 md:w-56 h-36 flex-shrink-0 overflow-hidden rounded border border-white/10 bg-black/50 relative">
                    <img src="${s.image_url}" alt="${s.title}" class="w-full h-full object-cover transition-transform duration-500 hover:scale-105" onerror="this.parentElement.style.display='none'">
                </div>
            ` : '';

            const regLink = (s.registration_url && s.registration_url.trim())
                ? s.registration_url
                : `/register?event_id=${s.id}&event_title=${encodeURIComponent(s.title)}`;
            const regLabel = (s.link_label && s.link_label.trim()) ? s.link_label : 'Register Now';
            const isExternalReg = regLink.startsWith('http://') || regLink.startsWith('https://');

            const secondaryLinkHtml = (s.secondary_link_url && s.secondary_link_url.trim()) ? `
                <a href="${s.secondary_link_url}" ${s.secondary_link_url.startsWith('http') ? 'target="_blank" rel="noopener"' : ''} class="text-xs text-zinc-400 hover:text-white underline font-mono">
                    ${s.secondary_link_label || 'Learn More'} ↗
                </a>
            ` : '';

            return `
                <div class="cyber-card p-5 space-y-4 border-l-2 ${isLive ? 'border-l-[#FF2A2A]' : 'border-l-zinc-700'}">
                    <div class="flex flex-col sm:flex-row gap-5 items-start">
                        ${imageHtml}
                        <div class="flex-1 space-y-3 min-w-0 w-full">
                            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                                <div class="flex flex-wrap items-center gap-2 text-xs font-mono">
                                    <span class="text-zinc-200">🕒 ${s.time_slot}</span>
                                    <span class="text-zinc-500">•</span>
                                    <span class="text-zinc-400">${s.mode}</span>
                                    <span class="text-zinc-500">•</span>
                                    <span class="text-[#FF2A2A]">${s.category}</span>
                                </div>
                                <div class="flex items-center gap-2">
                                    ${customBadge}
                                    ${statusBadge}
                                </div>
                            </div>

                            <h3 class="font-headline font-bold text-base uppercase text-white tracking-tight">${s.title}</h3>
                            <p class="text-xs text-zinc-400 font-normal leading-relaxed">${s.description || ''}</p>

                            <div class="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-white/5 text-xs text-zinc-500">
                                <div>
                                    <span>Speaker: <strong class="text-zinc-300 font-medium">${s.speaker}</strong> (${s.speaker_title})</span>
                                    <span class="ml-3">📍 ${s.venue}</span>
                                </div>
                                <div class="flex items-center gap-3">
                                    ${secondaryLinkHtml}
                                    ${s.stream_url ? `
                                        <a href="${s.stream_url}" target="_blank" rel="noopener" class="text-zinc-400 hover:text-white underline font-mono text-xs">
                                            Watch Stream
                                        </a>
                                    ` : ''}
                                    <a href="${regLink}" ${isExternalReg ? 'target="_blank" rel="noopener"' : ''} class="btn-red text-xs py-1.5 px-4 font-semibold inline-block">
                                        ${regLabel}
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

    } catch (err) {
        console.error("Error loading sessions:", err);
    }
}

// Interactive Simulator
function initSimulator() {
    const sliders = ['sim-inno', 'sim-tech', 'sim-impact', 'sim-ui', 'sim-pitch'];
    sliders.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('input', updateSimulatorCalculation);
        }
    });
    updateSimulatorCalculation();
}

function updateSimulatorCalculation() {
    const inno = parseFloat(document.getElementById('sim-inno')?.value || 22);
    const tech = parseFloat(document.getElementById('sim-tech')?.value || 23);
    const impact = parseFloat(document.getElementById('sim-impact')?.value || 18);
    const ui = parseFloat(document.getElementById('sim-ui')?.value || 14);
    const pitch = parseFloat(document.getElementById('sim-pitch')?.value || 13);

    document.getElementById('sim-val-inno').innerText = `${inno}/25`;
    document.getElementById('sim-val-tech').innerText = `${tech}/25`;
    document.getElementById('sim-val-impact').innerText = `${impact}/20`;
    document.getElementById('sim-val-ui').innerText = `${ui}/15`;
    document.getElementById('sim-val-pitch').innerText = `${pitch}/15`;

    const total = (inno + tech + impact + ui + pitch).toFixed(1);
    const totalEl = document.getElementById('sim-total-score');
    if (totalEl) totalEl.innerText = total;

    const rankBadge = document.getElementById('sim-projected-rank');
    if (rankBadge) {
        if (total >= 92) {
            rankBadge.innerText = "Projected: Top 3 Finalist (High Distinction)";
            rankBadge.className = "p-2 rounded bg-red-950/40 text-[#FF2A2A] border border-red-500/30 font-mono text-xs w-full text-center";
        } else if (total >= 85) {
            rankBadge.innerText = "Projected: Top 10 Honors Standing";
            rankBadge.className = "p-2 rounded bg-white/5 text-zinc-300 border border-white/10 font-mono text-xs w-full text-center";
        } else {
            rankBadge.innerText = "Projected: General Qualifier";
            rankBadge.className = "p-2 rounded bg-black/40 text-zinc-500 border border-white/5 font-mono text-xs w-full text-center";
        }
    }
}

// Load Leaderboard from Database
async function loadLeaderboard() {
    const tbody = document.getElementById('leaderboard-body');
    if (!tbody) return;

    try {
        const res = await fetch('/api/leaderboard');
        const data = await res.json();

        if (!data || data.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="py-6 text-center text-zinc-500 font-mono text-xs">
                        No team scores recorded yet. Scores will update live as jury evaluations begin.
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = data.map(team => {
            let rankBadge = `<span class="font-mono text-zinc-500">#${team.rank}</span>`;
            if (team.rank === 1) rankBadge = `<span class="font-bold text-[#FF2A2A] font-mono">01. 🥇</span>`;
            if (team.rank === 2) rankBadge = `<span class="font-bold text-zinc-300 font-mono">02. 🥈</span>`;
            if (team.rank === 3) rankBadge = `<span class="font-bold text-amber-500 font-mono">03. 🥉</span>`;

            return `
                <tr class="hover:bg-white/[0.02] transition-colors">
                    <td class="py-3 px-4 whitespace-nowrap">${rankBadge}</td>
                    <td class="py-3 px-4">
                        <div class="font-bold text-white">${team.team_name}</div>
                        <div class="text-[11px] font-mono text-zinc-500">${team.registration_id} • ${team.college}</div>
                    </td>
                    <td class="py-3 px-4">
                        <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-white/5 text-zinc-300">
                            ${team.track}
                        </span>
                    </td>
                    <td class="py-3 px-4 font-headline font-bold text-right text-[#FF2A2A] text-sm">
                        ${team.total_score}
                    </td>
                </tr>
            `;
        }).join('');

    } catch (err) {
        console.error("Error loading leaderboard:", err);
    }
}

// Load Games Challenges
async function loadGames() {
    const container = document.getElementById('games-container');
    if (!container) return;

    try {
        const res = await fetch('/api/games');
        const games = await res.json();

        if (!games || games.length === 0) {
            container.innerHTML = `
                <div class="col-span-1 sm:col-span-2 cyber-card p-8 text-center text-zinc-500 space-y-2">
                    <div class="text-base font-headline uppercase text-zinc-400 font-bold">No Active Challenges</div>
                    <p class="text-xs text-zinc-500 font-normal">Mini-hack challenges and speed debug quests will be unlocked during live hackathon sessions.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = games.map(g => {
            if (g.type === 'speed_debug') {
                return `
                    <div class="cyber-card p-5 space-y-2.5">
                        <div class="flex items-center justify-between">
                            <span class="text-[10px] font-mono font-bold text-[#FF2A2A] bg-red-950/40 border border-red-500/20 px-2 py-0.5 rounded">
                                BUG HUNT
                            </span>
                            <span class="text-xs font-mono font-bold text-zinc-400">+${g.points} PTS</span>
                        </div>
                        <h4 class="font-headline font-bold text-sm uppercase text-white">${g.title}</h4>
                        <p class="text-xs text-zinc-400 font-normal">${g.question}</p>
                        ${g.snippet ? `<pre class="p-3 bg-black/60 border border-white/5 text-zinc-300 font-mono text-xs rounded overflow-x-auto">${g.snippet}</pre>` : ''}
                        <div class="space-y-1.5 pt-1">
                            ${g.options.map((opt, i) => `
                                <button onclick="submitGameAnswer(${g.id}, '${encodeURIComponent(opt)}')" class="w-full text-left p-2.5 rounded border border-white/10 hover:border-[#FF2A2A] hover:bg-white/[0.02] text-xs text-zinc-300 transition-colors">
                                    <span class="text-[#FF2A2A] font-mono mr-1.5">${String.fromCharCode(65 + i)}.</span> ${opt}
                                </button>
                            `).join('')}
                        </div>
                        <div id="game-feedback-${g.id}" class="text-xs font-mono"></div>
                    </div>
                `;
            } else if (g.type === 'cyber_trivia') {
                return `
                    <div class="cyber-card p-5 space-y-2.5">
                        <div class="flex items-center justify-between">
                            <span class="text-[10px] font-mono font-bold text-zinc-300 bg-white/5 border border-white/10 px-2 py-0.5 rounded">
                                SYSTEM TRIVIA
                            </span>
                            <span class="text-xs font-mono font-bold text-zinc-400">+${g.points} PTS</span>
                        </div>
                        <h4 class="font-headline font-bold text-sm uppercase text-white">${g.title}</h4>
                        <p class="text-xs text-zinc-400 font-normal">${g.question}</p>
                        <div class="space-y-1.5 pt-1">
                            ${g.options.map((opt, i) => `
                                <button onclick="submitGameAnswer(${g.id}, '${encodeURIComponent(opt)}')" class="w-full text-left p-2.5 rounded border border-white/10 hover:border-[#FF2A2A] hover:bg-white/[0.02] text-xs text-zinc-300 transition-colors">
                                    <span class="text-[#FF2A2A] font-mono mr-1.5">${String.fromCharCode(65 + i)}.</span> ${opt}
                                </button>
                            `).join('')}
                        </div>
                        <div id="game-feedback-${g.id}" class="text-xs font-mono"></div>
                    </div>
                `;
            } else if (g.type === 'typing_dash') {
                typingSnippetText = g.snippet;
                return `
                    <div class="cyber-card p-5 space-y-2.5 sm:col-span-2">
                        <div class="flex items-center justify-between">
                            <span class="text-[10px] font-mono font-bold text-[#FF2A2A] bg-red-950/40 border border-red-500/20 px-2 py-0.5 rounded">
                                SPEED TYPING DASH
                            </span>
                            <span class="text-xs font-mono font-bold text-zinc-400">+${g.points} PTS</span>
                        </div>
                        <h4 class="font-headline font-bold text-sm uppercase text-white">${g.title}</h4>
                        <p class="text-xs text-zinc-400 font-normal">${g.question}</p>
                        <pre class="p-3 bg-black/60 border border-white/5 text-zinc-300 font-mono text-xs rounded select-none overflow-x-auto">${g.snippet}</pre>
                        <textarea id="typing-input" oninput="handleTypingInput(${g.id})" rows="3" placeholder="Click here and type the exact code snippet above..." class="cyber-input w-full font-mono text-xs"></textarea>
                        <div class="flex items-center justify-between text-xs text-zinc-500 font-mono">
                            <div>Speed: <span id="typing-wpm" class="text-white font-bold">0</span> WPM</div>
                            <div id="game-feedback-${g.id}" class="text-xs"></div>
                        </div>
                    </div>
                `;
            }
        }).join('');

    } catch (err) {
        console.error("Error loading games:", err);
    }
}

// Submit Game Answer
async function submitGameAnswer(gameId, encodedAnswer) {
    const answer = decodeURIComponent(encodedAnswer);
    const feedbackEl = document.getElementById(`game-feedback-${gameId}`);
    const teamIdInput = document.getElementById('game-team-reg-id');
    const teamId = teamIdInput ? teamIdInput.value.trim() : "";

    const formData = new FormData();
    formData.append('game_id', gameId);
    formData.append('answer', answer);
    if (teamId) formData.append('team_reg_id', teamId);

    try {
        const res = await fetch('/api/games/submit', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();

        if (data.correct) {
            triggerConfetti();
            feedbackEl.className = "text-xs font-mono text-[#FF2A2A] mt-2 p-2 rounded bg-red-950/40 border border-red-500/30";
            feedbackEl.innerHTML = `✓ Correct! +${data.points_earned} Points awarded! ${data.bonus_applied ? 'Bonus synced to Team on Leaderboard!' : ''} <p class="mt-0.5 text-[11px] font-normal text-zinc-400">${data.explanation}</p>`;
            showToast("Challenge Solved!", `+${data.points_earned} Points!`, "success");
            loadLeaderboard();
        } else {
            feedbackEl.className = "text-xs font-mono text-zinc-400 mt-2 p-2 rounded bg-black/40 border border-white/10";
            feedbackEl.innerHTML = `✕ Incorrect attempt. Review the syntax and try again.`;
        }
    } catch (err) {
        console.error("Error submitting answer:", err);
    }
}

// Typing input handler
function handleTypingInput(gameId) {
    const input = document.getElementById('typing-input');
    const wpmEl = document.getElementById('typing-wpm');
    const feedbackEl = document.getElementById(`game-feedback-${gameId}`);

    if (!typingStartTime) {
        typingStartTime = new Date();
    }

    const currentVal = input.value;
    const elapsedMinutes = (new Date() - typingStartTime) / 60000;
    const words = currentVal.trim().split(/\s+/).length;
    const wpm = elapsedMinutes > 0 ? Math.round(words / elapsedMinutes) : 0;
    wpmEl.innerText = Math.min(180, wpm);

    const cleanTarget = typingSnippetText.replace(/\r\n/g, '\n').trim();
    const cleanInput = currentVal.replace(/\r\n/g, '\n').trim();

    if (cleanInput === cleanTarget) {
        triggerConfetti();
        input.disabled = true;
        feedbackEl.className = "text-[#FF2A2A] font-mono font-bold";
        feedbackEl.innerText = `Completed at ${wpm} WPM! +60 Points!`;
        showToast("Typing Dash Cleared!", `Speed: ${wpm} WPM`, "success");
        submitGameAnswer(gameId, encodeURIComponent(cleanTarget));
    }
}

// Load Feedback Summary (True DB Calculations)
async function loadFeedbackSummary() {
    try {
        const res = await fetch('/api/feedbacks/summary');
        const summary = await res.json();

        const avgRatingEl = document.getElementById('summary-avg-rating');
        const execSummaryEl = document.getElementById('summary-exec-digest');

        if (avgRatingEl) {
            avgRatingEl.innerText = summary.total_reviews > 0 ? `${summary.average_rating} / 5.0` : "No ratings yet";
        }
        if (execSummaryEl) {
            execSummaryEl.innerText = summary.executive_summary;
        }
    } catch (err) {
        console.error("Error loading feedback summary:", err);
    }
}

// Load Real Feedbacks Stream
async function loadFeedbacks() {
    const listEl = document.getElementById('feedbacks-stream');
    if (!listEl) return;

    try {
        const res = await fetch('/api/feedbacks');
        const items = await res.json();

        if (!items || items.length === 0) {
            listEl.innerHTML = `
                <div class="p-6 rounded bg-black/40 text-center text-zinc-500 font-mono text-xs">
                    No reviews logged yet. Be the first to share your thoughts on the chapter.
                </div>
            `;
            return;
        }

        listEl.innerHTML = items.map(f => `
            <div class="p-3.5 rounded bg-black/40 border border-white/5 space-y-1">
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-2">
                        <span class="font-bold text-white text-xs">${f.author_name}</span>
                        <span class="px-1.5 py-0.2 rounded text-[10px] font-mono bg-white/5 text-zinc-400">${f.role}</span>
                    </div>
                    <div class="text-[#FF2A2A] text-xs">
                        ${'★'.repeat(f.rating)}${'☆'.repeat(5 - f.rating)}
                    </div>
                </div>
                <p class="text-xs text-zinc-300 italic font-normal">"${f.comment}"</p>
                <div class="text-[10px] font-mono text-zinc-500">Tag: ${f.category}</div>
            </div>
        `).join('');

    } catch (err) {
        console.error("Error loading feedbacks:", err);
    }
}

// Submit Feedback
async function handleFeedbackSubmit(event) {
    event.preventDefault();

    const author_name = document.getElementById('fb-author').value.trim();
    const role = document.getElementById('fb-role').value;
    const rating = parseInt(document.getElementById('fb-rating').value);
    const category = document.getElementById('fb-category').value;
    const comment = document.getElementById('fb-comment').value.trim();

    try {
        const res = await fetch('/api/feedbacks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ author_name, role, rating, category, comment })
        });

        if (res.ok) {
            showToast("Feedback Recorded", "Thank you for helping us improve Hack with India!", "success");
            document.getElementById('feedback-form').reset();
            loadFeedbacks();
            loadFeedbackSummary();
        }
    } catch (err) {
        console.error("Error submitting feedback:", err);
    }
}

// Load Genuine Blog Dispatches
async function loadBlog() {
    const listEl = document.getElementById('blog-container');
    if (!listEl) return;

    try {
        const res = await fetch('/api/blog');
        const blogs = await res.json();

        if (!blogs || blogs.length === 0) {
            listEl.innerHTML = `
                <div class="col-span-3 cyber-card p-8 text-center text-zinc-500 font-mono text-xs">
                    No announcements published yet. Official notices will appear here.
                </div>
            `;
            return;
        }

        listEl.innerHTML = blogs.map(b => `
            <div class="cyber-card p-5 flex flex-col justify-between space-y-3">
                <div class="space-y-2">
                    <div class="flex items-center justify-between text-[10px] font-mono text-zinc-500">
                        <span class="text-[#FF2A2A]">${b.category}</span>
                        <span>${b.pinned ? '📌 PINNED' : ''}</span>
                    </div>
                    <h3 class="font-headline font-bold text-base uppercase text-white leading-snug">${b.title}</h3>
                    <p class="text-xs text-zinc-400 font-normal leading-relaxed">${b.summary}</p>
                </div>
                <div class="pt-2 border-t border-white/5 text-[10px] font-mono text-zinc-500 flex items-center justify-between">
                    <span>By: ${b.author}</span>
                    <button onclick="showToast('${b.title.replace(/'/g, "\\'")}', '${b.content.replace(/'/g, "\\'")}', 'info')" class="text-zinc-300 hover:text-white underline">
                        Read Notice →
                    </button>
                </div>
            </div>
        `).join('');

    } catch (err) {
        console.error("Error loading blog:", err);
    }
}

// Publish Announcement from Admin
async function handlePublishBlog(event) {
    event.preventDefault();

    const title = document.getElementById('admin-blog-title').value.trim();
    const summary = document.getElementById('admin-blog-summary').value.trim();
    const content = document.getElementById('admin-blog-content').value.trim();

    try {
        const res = await fetch('/api/blog', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title,
                category: "Announcement",
                summary,
                content,
                pinned: true
            })
        });

        if (res.ok) {
            showToast("Notice Broadcasted", "Announcement published to chapter feed!", "success");
            document.getElementById('admin-blog-form').reset();
            loadBlog();
        }
    } catch (err) {
        console.error("Error publishing blog:", err);
    }
}

// Admin Panel: Load Teams
async function loadAdminTeams() {
    const tbody = document.getElementById('admin-teams-table');
    if (!tbody) return;

    try {
        const res = await fetch('/api/teams');
        const teams = await res.json();

        if (!teams || teams.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="p-6 text-center text-zinc-500 font-mono text-xs">
                        No team registrations recorded in the database yet.
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = teams.map(t => `
            <tr class="hover:bg-white/[0.02]">
                <td class="p-3 font-mono font-bold text-xs text-[#FF2A2A]">${t.registration_id}</td>
                <td class="p-3 text-xs font-bold text-white">
                    ${t.team_name}
                    ${t.is_spot_registration ? '<span class="ml-1 text-[9px] font-mono px-1.5 py-0.5 bg-red-950 text-[#FF2A2A]">Spot</span>' : ''}
                </td>
                <td class="p-3 text-xs text-zinc-300">${t.lead_name}</td>
                <td class="p-3 text-xs text-zinc-400 font-mono">${t.lab_allotment}</td>
                <td class="p-3 text-xs font-mono font-bold text-white">${t.total_score}</td>
                <td class="p-3 text-xs">
                    <button onclick="toggleAttendance(${t.id}, ${!t.is_present})" class="px-2 py-1 rounded text-xs font-mono font-semibold ${t.is_present ? 'bg-red-950/80 text-[#FF2A2A] border border-red-500/30' : 'bg-white/5 text-zinc-500 border border-white/10'}">
                        ${t.is_present ? '✓ Present' : '✕ Absent'}
                    </button>
                </td>
                <td class="p-3 text-xs">
                    <button onclick="openScoreModal(${t.id}, '${t.team_name.replace(/'/g, "\\'")}', ${JSON.stringify(t.scores).replace(/"/g, '&quot;')})" class="btn-outline-dark text-[10px] py-1 px-2.5">
                        Grade
                    </button>
                </td>
            </tr>
        `).join('');

    } catch (err) {
        console.error("Error loading admin teams:", err);
    }
}

// Toggle Attendance (Number of presenties)
async function toggleAttendance(teamId, newStatus) {
    try {
        const res = await fetch(`/api/teams/${teamId}/attendance`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ is_present: newStatus })
        });

        if (res.ok) {
            showToast("Attendance Updated", `Team marked ${newStatus ? 'Present' : 'Absent'}`, "success");
            loadAdminTeams();
            loadStats();
        }
    } catch (err) {
        console.error("Error toggling attendance:", err);
    }
}

// Score Modal
function openScoreModal(teamId, teamName, scores) {
    document.getElementById('score-modal-team-id').value = teamId;
    document.getElementById('score-modal-team-name').innerText = teamName;
    
    document.getElementById('score-inno').value = scores.innovation || 0;
    document.getElementById('score-tech').value = scores.technical || 0;
    document.getElementById('score-impact').value = scores.impact || 0;
    document.getElementById('score-ui').value = scores.ui_ux || 0;
    document.getElementById('score-pitch').value = scores.pitch || 0;

    document.getElementById('score-modal').classList.remove('hidden');
}

function closeScoreModal() {
    document.getElementById('score-modal').classList.add('hidden');
}

// Save Team Scores
async function handleScoreSubmit(event) {
    event.preventDefault();

    const teamId = document.getElementById('score-modal-team-id').value;
    const score_innovation = parseFloat(document.getElementById('score-inno').value);
    const score_technical = parseFloat(document.getElementById('score-tech').value);
    const score_impact = parseFloat(document.getElementById('score-impact').value);
    const score_ui_ux = parseFloat(document.getElementById('score-ui').value);
    const score_pitch = parseFloat(document.getElementById('score-pitch').value);

    try {
        const res = await fetch(`/api/teams/${teamId}/score`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                score_innovation,
                score_technical,
                score_impact,
                score_ui_ux,
                score_pitch
            })
        });

        if (res.ok) {
            closeScoreModal();
            triggerConfetti();
            showToast("Scores Saved", "Winning parameters updated on leaderboard", "success");
            loadAdminTeams();
            loadLeaderboard();
            loadStats();
        }
    } catch (err) {
        console.error("Error saving scores:", err);
    }
}
