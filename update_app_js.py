path = r"C:\Users\saad uddin\.gemini\antigravity\scratch\hack-with-india-mcet\static\js\app.js"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

target = """        listEl.innerHTML = sessions.map(s => {
            const isLive = (s.status === 'Live Now');
            const statusBadge = isLive 
                ? `<span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-red-950/80 text-[#FF2A2A] border border-red-500/30">● LIVE NOW</span>`
                : s.status === 'Completed'
                ? `<span class="px-2 py-0.5 rounded text-[10px] font-mono text-zinc-500 bg-white/5">COMPLETED</span>`
                : `<span class="px-2 py-0.5 rounded text-[10px] font-mono text-zinc-400 bg-white/5">UPCOMING</span>`;

            return `
                <div class="cyber-card p-5 space-y-3 border-l-2 ${isLive ? 'border-l-[#FF2A2A]' : 'border-l-zinc-700'}">
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <div class="flex items-center gap-2 text-xs font-mono">
                            <span class="text-zinc-200">🕒 ${s.time_slot}</span>
                            <span class="text-zinc-500">•</span>
                            <span class="text-zinc-400">${s.mode}</span>
                            <span class="text-zinc-500">•</span>
                            <span class="text-[#FF2A2A]">${s.category}</span>
                        </div>
                        <div>${statusBadge}</div>
                    </div>

                    <h3 class="font-headline font-bold text-base uppercase text-white tracking-tight">${s.title}</h3>
                    <p class="text-xs text-zinc-400 font-normal leading-relaxed">${s.description}</p>

                    <div class="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-white/5 text-xs text-zinc-500">
                        <div>
                            <span>Speaker: <strong class="text-zinc-300 font-medium">${s.speaker}</strong> (${s.speaker_title})</span>
                            <span class="ml-3">📍 ${s.venue}</span>
                        </div>
                        <div class="flex items-center gap-3">
                            ${s.stream_url ? `
                                <a href="${s.stream_url}" target="_blank" class="text-zinc-400 hover:text-white underline font-mono text-xs">
                                    Watch Stream
                                </a>
                            ` : ''}
                            <a href="/register?event_id=${s.id}&event_title=${encodeURIComponent(s.title)}" class="btn-red text-xs py-1.5 px-4 font-semibold inline-block">
                                Register Now
                            </a>
                        </div>
                    </div>
                </div>
            `;
        }).join('');"""

replacement = """        listEl.innerHTML = sessions.map(s => {
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
        }).join('');"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS")
else:
    print("TARGET NOT FOUND")
