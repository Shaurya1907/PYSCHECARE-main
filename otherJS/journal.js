// otherJS/journal.js
// Handles daily mood journal: entry saving, streak display, trend chart

'use strict';

// ── DOM references ──────────────────────────────────────────────────
const moodSlider      = document.getElementById('mood-slider');
const moodDisplay     = document.getElementById('mood-score-display');
const journalText     = document.getElementById('journal-text');
const charCount       = document.getElementById('char-count');
const saveBtn         = document.getElementById('save-entry-btn');
const messageEl       = document.getElementById('journal-message');
const streakCountEl   = document.getElementById('streak-count');
const avgMoodEl       = document.getElementById('avg-mood-display');
const historyListEl   = document.getElementById('history-list');

let selectedMoodLabel = 'Neutral';
let moodChart         = null;

// ── Mood slider ─────────────────────────────────────────────────────
moodSlider.addEventListener('input', function () {
    moodDisplay.textContent = this.value;
});

// ── Mood tag selection ───────────────────────────────────────────────
document.querySelectorAll('.mood-tag').forEach(tag => {
    tag.addEventListener('click', function () {
        document.querySelectorAll('.mood-tag').forEach(t => t.classList.remove('selected'));
        this.classList.add('selected');
        selectedMoodLabel = this.dataset.mood;
    });
});

// ── Character counter ────────────────────────────────────────────────
journalText.addEventListener('input', function () {
    charCount.textContent = this.value.length;
});

// ── Show message helper ──────────────────────────────────────────────
function showMessage(type, text) {
    messageEl.className    = `journal-message ${type}`;
    messageEl.textContent  = text;
    messageEl.style.display = 'block';
    setTimeout(() => { messageEl.style.display = 'none'; }, 6000);
}

// ── Save entry ───────────────────────────────────────────────────────
saveBtn.addEventListener('click', async function () {
    saveBtn.disabled    = true;
    saveBtn.textContent = '⏳ Saving...';

    try {
        const res = await fetch('/api/journal/entry', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                mood_score:   parseInt(moodSlider.value),
                mood_label:   selectedMoodLabel,
                journal_text: journalText.value.trim(),
            }),
        });

        const data = await res.json();

        if (res.ok) {
            showMessage('success', data.message);
            journalText.value     = '';
            charCount.textContent = '0';
            await loadHistory(7);   // Refresh chart and history
        } else {
            showMessage('error', `❌ ${data.error}`);
        }
    } catch {
        showMessage('error', '❌ Could not reach the server. Please try again.');
    } finally {
        saveBtn.disabled    = false;
        saveBtn.textContent = '💾 Save Today\'s Entry';
    }
});

// ── Load history + streak + chart ────────────────────────────────────
async function loadHistory(days = 7) {
    try {
        const res  = await fetch(`/api/journal/history?days=${days}`);
        const data = await res.json();

        // Update streak
        if (streakCountEl) streakCountEl.textContent = data.streak ?? 0;

        // Update average mood
        if (avgMoodEl) {
            avgMoodEl.textContent = data.avg_mood > 0
                ? `${data.avg_mood} / 10`
                : '—';
        }

        // Render chart
        renderMoodChart(data.entries);

        // Render history list
        renderHistoryList(data.entries);

    } catch (err) {
        console.error('Failed to load journal history:', err);
        if (historyListEl) {
            historyListEl.innerHTML = '<p class="error-text">Failed to load entries. Please refresh.</p>';
        }
    }
}

// ── Chart rendering ──────────────────────────────────────────────────
function renderMoodChart(entries) {
    const canvas = document.getElementById('moodTrendChart');
    if (!canvas) return;

    const ctx    = canvas.getContext('2d');
    const labels = entries.map(e =>
        new Date(e.entry_date + 'T00:00:00').toLocaleDateString('en-IN', {
            weekday: 'short', month: 'short', day: 'numeric'
        })
    );
    const scores = entries.map(e => e.mood_score);

    // Determine point colors: red for low, yellow for mid, green for high
    const pointColors = scores.map(s =>
        s <= 3 ? '#ef4444' : s <= 6 ? '#f59e0b' : '#10b981'
    );

    if (moodChart) {
        moodChart.destroy();
    }

    moodChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label:           'Mood Score',
                data:            scores,
                borderColor:     '#6C63FF',
                backgroundColor: 'rgba(108, 99, 255, 0.08)',
                pointBackgroundColor: pointColors,
                pointRadius:     6,
                pointHoverRadius:8,
                fill:            true,
                tension:         0.4,
            }],
        },
        options: {
            responsive:          true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    min:   1,
                    max:   10,
                    ticks: { stepSize: 1 },
                    title: { display: true, text: 'Mood Score' },
                },
                x: {
                    title: { display: true, text: 'Date' },
                },
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => `Mood: ${ctx.parsed.y}/10 — ${entries[ctx.dataIndex]?.mood_label || ''}`,
                    },
                },
            },
        },
    });
}

// ── History list rendering ───────────────────────────────────────────
function renderHistoryList(entries) {
    if (!historyListEl) return;

    if (!entries || entries.length === 0) {
        historyListEl.innerHTML =
            '<p class="no-entries">No journal entries yet. Start writing today! 🌱</p>';
        return;
    }

    // Show newest entries first
    const sorted = [...entries].sort((a, b) =>
        new Date(b.entry_date) - new Date(a.entry_date)
    );

    historyListEl.innerHTML = sorted.map(e => {
        const scoreColor = e.mood_score <= 3 ? 'low'
                         : e.mood_score <= 6 ? 'mid' : 'high';
        return `
            <div class="history-entry">
                <div class="entry-header">
                    <span class="entry-date">
                        ${new Date(e.entry_date + 'T00:00:00').toLocaleDateString('en-IN', {
                            weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
                        })}
                    </span>
                    <span class="entry-score score-${scoreColor}">
                        ${e.mood_score}/10 — ${e.mood_label}
                    </span>
                </div>
                ${e.journal_text
                    ? `<p class="entry-text">${e.journal_text}</p>`
                    : '<p class="entry-text no-text">No written entry for this day.</p>'
                }
            </div>
        `;
    }).join('');
}

// ── Init on page load ────────────────────────────────────────────────
loadHistory(7);