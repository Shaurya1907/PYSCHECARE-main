document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('medication-form');
    const nameInput = document.getElementById('medication-name');
    const dosageAmountInput = document.getElementById('dosage-amount');
    const dosageUnitSelect = document.getElementById('dosage-unit');
    const frequencySelect = document.getElementById('frequency');
    const startDateInput = document.getElementById('start-date');
    const notesInput = document.getElementById('notes');
    const submitBtn = document.querySelector('.submit-btn');
    const statusMessage = document.getElementById('form-status');
    const toast = document.getElementById('toast');

    const errors = {
        name: document.getElementById('name-error'),
        dosage: document.getElementById('dosage-error'),
        frequency: document.getElementById('frequency-error'),
        date: document.getElementById('date-error'),
        notes: document.getElementById('notes-error'),
    };

    const allowedUnits = ['mg', 'mcg', 'ml', 'tablet', 'capsule', 'drop', 'puff'];
    const allowedFrequencies = ['Once daily', 'Twice daily', 'Three times daily', 'Every 8 hours', 'As needed'];

    const validationState = {
        name: false,
        dosage: false,
        unit: false,
        frequency: false,
        date: false,
        notes: true,
    };

    function setFieldState(input, valid, message, fieldKey) {
        const group = input.closest('.form-group');
        if (!group) return;

        if (valid) {
            group.classList.remove('field-invalid');
            group.classList.add('field-valid');
            errors[fieldKey].textContent = '';
        } else {
            group.classList.add('field-invalid');
            group.classList.remove('field-valid');
            errors[fieldKey].textContent = message;
        }

        validationState[fieldKey] = valid;
        updateSubmitButton();
    }

    function updateSubmitButton() {
        submitBtn.disabled = !Object.values(validationState).every(Boolean);
    }

    function validateName() {
        const value = nameInput.value.trim();
        const valid = value.length >= 2 && value.length <= 100;
        setFieldState(nameInput, valid, valid ? '' : 'Medication name is required and must be 2–100 characters.', 'name');
        return valid;
    }

    function validateDosage() {
        const value = dosageAmountInput.value.trim();
        const amount = parseFloat(value);
        const valid = value !== '' && !Number.isNaN(amount) && amount >= 0.1 && amount <= 1000;
        const message = valid ? '' : 'Dosage must be a number between 0.1 and 1000';
        setFieldState(dosageAmountInput, valid, message, 'dosage');
        return valid;
    }

    function validateUnit() {
        const value = dosageUnitSelect.value;
        const valid = allowedUnits.includes(value);
        const message = valid ? '' : 'Please select a valid unit (mg, ml, etc.)';
        setFieldState(dosageUnitSelect, valid, message, 'dosage');
        validationState.unit = valid;
        updateSubmitButton();
        return valid;
    }

    function validateFrequency() {
        const value = frequencySelect.value;
        const valid = allowedFrequencies.includes(value);
        const message = valid ? '' : 'Please select a valid frequency.';
        setFieldState(frequencySelect, valid, message, 'frequency');
        return valid;
    }

    function validateDate() {
        const value = startDateInput.value;
        const selectedDate = new Date(value + 'T00:00:00');
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const valid = value !== '' && !Number.isNaN(selectedDate.getTime()) && selectedDate <= today;
        const message = valid ? '' : 'Start date cannot be in the future';
        setFieldState(startDateInput, valid, message, 'date');
        return valid;
    }

    function validateNotes() {
        const value = notesInput.value.trim();
        const valid = value.length <= 500;
        const message = valid ? '' : 'Notes must be 500 characters or less.';
        setFieldState(notesInput, valid, message, 'notes');
        return valid;
    }

    function showStatus(message, type) {
        if (!statusMessage) return;
        statusMessage.textContent = message;
        statusMessage.style.color = type === 'success' ? '#2e7d32' : '#d32f2f';
    }

    function showToast(message, type = 'success') {
        toast.textContent = message;
        toast.className = `toast visible ${type}`;
        window.clearTimeout(toast.dismissTimeout);
        toast.dismissTimeout = window.setTimeout(() => {
            toast.classList.remove('visible');
        }, 4500);
    }

    function clearStatus() {
        statusMessage.textContent = '';
    }

    function validateAll() {
        validateName();
        const dosageValid = validateDosage();
        const unitValid = validateUnit();
        const frequencyValid = validateFrequency();
        const dateValid = validateDate();
        const notesValid = validateNotes();
        return dosageValid && unitValid && frequencyValid && dateValid && notesValid && validateName();
    }

    nameInput.addEventListener('input', validateName);
    dosageAmountInput.addEventListener('input', validateDosage);
    dosageUnitSelect.addEventListener('change', validateUnit);
    frequencySelect.addEventListener('change', validateFrequency);
    startDateInput.addEventListener('change', validateDate);
    notesInput.addEventListener('input', validateNotes);

    form.addEventListener('submit', async function (event) {
        event.preventDefault();
        clearStatus();

        if (!validateAll()) {
            showStatus('Please fix the highlighted fields before saving.', 'error');
            return;
        }

        submitBtn.disabled = true;
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Saving...';

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
            });

            const data = await response.json();
            if (response.ok && data.success) {
                showStatus(data.message || 'Medication added successfully! ✅', 'success');
                showToast(data.message || 'Medication saved! 🎉', 'success');
                form.reset();
                Object.keys(validationState).forEach(key => {
                    validationState[key] = key === 'notes';
                });
                document.querySelectorAll('.field-valid').forEach(field => field.classList.remove('field-valid'));
                document.querySelectorAll('.field-invalid').forEach(field => field.classList.remove('field-invalid'));
                updateSubmitButton();
            } else {
                const serverMessage = data.message || 'Unable to save medication. Please try again.';
                showStatus(serverMessage, 'error');
                showToast(serverMessage, 'error');
            }
        } catch (error) {
            showStatus('Network error — please check your connection and try again', 'error');
            showToast('Network error — please check your connection and try again', 'error');
        } finally {
            submitBtn.disabled = !Object.values(validationState).every(Boolean);
            submitBtn.textContent = originalText;
        }
    });
});
