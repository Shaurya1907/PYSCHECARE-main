// otherJS/appointment.js
// Appointment booking and management functionality

document.addEventListener('DOMContentLoaded', async function () {

    // ── Set min date to today ──────────────────────────────────────
    const dateInput = document.getElementById('appt-date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.setAttribute('min', today);
    }

    // ── Populate therapist dropdown on page load ──────────────────
    async function loadTherapists() {
        const selectEl = document.getElementById('therapist');
        if (!selectEl) return;

        try {
            const res = await fetch('/api/appointment/therapists');
            const data = await res.json();

            selectEl.innerHTML = '<option value="">-- Select a Therapist --</option>';
            data.therapists.forEach(t => {
                const opt = document.createElement('option');
                opt.value = t.id;
                opt.textContent = `${t.name} — ${t.specialty}`;
                selectEl.appendChild(opt);
            });
        } catch (err) {
            console.error('Failed to load therapists:', err);
            selectEl.innerHTML = '<option value="">Error loading therapists. Please refresh.</option>';
        }
    }

    // ── Load upcoming appointments ────────────────────────────────
    async function loadMyAppointments() {
        const listEl = document.getElementById('appointments-list');
        if (!listEl) return;

        try {
            const res = await fetch('/api/appointment/my');
            const data = await res.json();

            if (data.appointments.length === 0) {
                listEl.innerHTML = '<p class="no-appointments">No upcoming appointments.</p>';
                return;
            }

            listEl.innerHTML = data.appointments.map(appt => `
                <div class="appointment-card status-${appt.status}">
                    <div class="appt-header">
                        <strong>${appt.therapist_name || 'Your Therapist'}</strong>
                        <span class="appt-status badge-${appt.status}">${appt.status.toUpperCase()}</span>
                    </div>
                    <p>📅 ${new Date(appt.appointment_datetime).toLocaleString('en-IN')}</p>
                    <p>📱 Session Type: ${appt.session_type}</p>
                    ${appt.notes ? `<p>📝 Notes: ${appt.notes}</p>` : ''}
                    ${appt.status === 'pending' || appt.status === 'confirmed' ? `
                        <button class="cancel-btn" data-id="${appt.id}">❌ Cancel Appointment</button>
                    ` : ''}
                </div>
            `).join('');

            // Attach cancel handlers
            document.querySelectorAll('.cancel-btn').forEach(btn => {
                btn.addEventListener('click', () => cancelAppointment(btn.dataset.id));
            });

        } catch (err) {
            console.error('Failed to load appointments:', err);
            listEl.innerHTML = '<p class="error">Could not load appointments. Please refresh.</p>';
        }
    }

    // ── Cancel appointment ────────────────────────────────────────
    async function cancelAppointment(apptId) {
        const confirmed = confirm('Are you sure you want to cancel this appointment?');
        if (!confirmed) return;

        const reason = prompt('Reason for cancellation (optional):') || '';

        try {
            const res = await fetch(`/api/appointment/${apptId}/cancel`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reason }),
            });
            const data = await res.json();

            if (res.ok) {
                showMessage('success', `✅ ${data.message}`);
                await loadMyAppointments();   // Refresh the list
            } else {
                showMessage('error', `❌ ${data.error}`);
            }
        } catch (err) {
            showMessage('error', '❌ Could not connect to server. Please try again.');
        }
    }

    // ── Book appointment form handler ─────────────────────────────
    const bookingForm = document.getElementById('book-appointment-form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            const submitBtn = bookingForm.querySelector('[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.textContent = '⏳ Booking...';

            const payload = {
                therapist_id: document.getElementById('therapist')?.value,
                appointment_date: document.getElementById('appt-date')?.value,
                appointment_time: document.getElementById('appt-time')?.value,
                session_type: document.getElementById('session-type')?.value,
                notes: document.getElementById('notes')?.value || '',
            };

            // Client-side validation before sending
            if (!payload.therapist_id) {
                showMessage('error', 'Please select a therapist.');
                submitBtn.disabled = false;
                submitBtn.textContent = '📅 Book Appointment';
                return;
            }

            if (!payload.appointment_date || !payload.appointment_time) {
                showMessage('error', 'Please select both date and time.');
                submitBtn.disabled = false;
                submitBtn.textContent = '📅 Book Appointment';
                return;
            }

            try {
                const res = await fetch('/api/appointment/book', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });

                const data = await res.json();

                if (res.ok) {
                    const appt = data.appointment;
                    showMessage(
                        'success',
                        `✅ ${data.message}\n` +
                        `Therapist: ${appt.therapist_id}\n` +
                        `Date & Time: ${appt.appointment_datetime}\n` +
                        `Session Type: ${appt.session_type}`
                    );
                    bookingForm.reset();
                    // Set min date again after reset
                    if (dateInput) {
                        dateInput.setAttribute('min', new Date().toISOString().split('T')[0]);
                    }
                    await loadMyAppointments();  // Refresh upcoming list
                } else {
                    showMessage('error', `❌ ${data.error}`);
                }

            } catch (err) {
                showMessage('error', '❌ Could not connect to the server. Please try again.');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = '📅 Book Appointment';
            }
        });
    }

    // ── Helper: show success/error message ────────────────────────
    function showMessage(type, text) {
        let msgEl = document.getElementById('booking-message');
        if (!msgEl) {
            msgEl = document.createElement('div');
            msgEl.id = 'booking-message';
            const form = document.getElementById('book-appointment-form');
            form?.parentNode?.insertBefore(msgEl, form);
        }
        msgEl.className = `booking-message ${type}`;
        msgEl.textContent = text;
        msgEl.scrollIntoView({ behavior: 'smooth' });
        setTimeout(() => { 
            if (msgEl) msgEl.textContent = ''; 
        }, 8000);
    }

    // ── Init ──────────────────────────────────────────────────────
    await loadTherapists();
    await loadMyAppointments();
});