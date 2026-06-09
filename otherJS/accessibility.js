// =====================================================
// 1. CHOOSE ACCESSIBILITY DOM EXECUTION LIFECYCLE
// =====================================================
document.addEventListener("DOMContentLoaded", () => {

    // Define the component markup layout string
    const accessibilityMarkup = `
    <section aria-label="Accessibility Options">
        <button id="accessibility-btn" class="accessibility-btn" aria-label="Open Accessibility Settings" aria-controls="accessibility-panel" aria-expanded="false">
            <i class="fas fa-universal-access" aria-hidden="true"></i>
        </button>
        <div id="accessibility-panel" class="accessibility-panel" role="region" aria-labelledby="accessibility-heading" aria-hidden="true">
            <h3 id="accessibility-heading">Accessibility Settings</h3>
            
            <div class="setting-group">
                <label for="font-size">Text Size</label>
                <select id="font-size" aria-describedby="font-size-desc">
                    <option value="small">Small</option>
                    <option value="medium" selected>Medium</option>
                    <option value="large">Large</option>
                </select>
                <span id="font-size-desc" class="sr-only">Adjusts the site wide text scaling.</span>
            </div>

            <div class="setting-group">
                <input type="checkbox" id="contrast-toggle">
                <label for="contrast-toggle">Enable High Contrast Mode</label>
            </div>
            
            <div class="setting-group">
                <input type="checkbox" id="focus-toggle">
                <label for="focus-toggle">Highlight Keyboard Focus</label>
            </div>
        </div>
    </section>
    `;

    // Inject the markup cleanly into the DOM right before the body closes
    document.body.insertAdjacentHTML('beforeend', accessibilityMarkup);

    // =====================================================
    // 2. DOM ELEMENT TARGET SELECTION
    // =====================================================
    const accessibilityBtn = document.getElementById("accessibility-btn");
    const accessibilityPanel = document.getElementById("accessibility-panel");
    const fontSizeSelect = document.getElementById("font-size");
    const contrastToggle = document.getElementById("contrast-toggle");
    const focusToggle = document.getElementById("focus-toggle");

    // =====================================================
    // 3. CACHED PREFERENCES RECOVERY
    // =====================================================
    const allowedFonts = ["small", "medium", "large"];

    let savedFont = localStorage.getItem("fontSize");

    if (!allowedFonts.includes(savedFont)) {
        savedFont = "medium";
    }
    const savedContrast = localStorage.getItem("contrastMode") === "true";
    const savedFocus = localStorage.getItem("focusMode") === "true";

    // Apply font-size configurations
    document.body.classList.add(`font-${savedFont}`);
    if (fontSizeSelect) fontSizeSelect.value = savedFont;

    // Apply high contrast configurations
    if (contrastToggle) contrastToggle.checked = savedContrast;
    if (savedContrast) {
        document.body.classList.add("high-contrast");
    }

    // Apply focus styles configuration
    if (focusToggle) focusToggle.checked = savedFocus;
    if (savedFocus) {
        document.body.classList.add("force-focus-indicators");
    }

    // =====================================================
    // 4. ACTION LISTENERS & INTERACTION MANAGEMENT
    // =====================================================

    // Floating panel activation hook
    accessibilityBtn?.addEventListener("click", (e) => {
        e.stopPropagation(); // Stops immediate body listener execution override
        const isExpanded = accessibilityBtn.getAttribute("aria-expanded") === "true";
        
        accessibilityPanel?.classList.toggle("show");
        accessibilityBtn.setAttribute("aria-expanded", !isExpanded);
        accessibilityPanel?.setAttribute("aria-hidden", isExpanded);
    });

    // Font Scaling Selector
    fontSizeSelect?.addEventListener("change", () => {
        document.body.classList.remove("font-small", "font-medium", "font-large");
        document.body.classList.add(`font-${fontSizeSelect.value}`);
        localStorage.setItem("fontSize", fontSizeSelect.value);
    });

    // High Contrast Switch
    contrastToggle?.addEventListener("change", () => {
        document.body.classList.toggle("high-contrast", contrastToggle.checked);
        localStorage.setItem("contrastMode", contrastToggle.checked);
    });

    // Keyboard Indicator Focus Switch
    focusToggle?.addEventListener("change", () => {
        document.body.classList.toggle("force-focus-indicators", focusToggle.checked);
        localStorage.setItem("focusMode", focusToggle.checked);
    });

    // Outside document click closer logic
    document.addEventListener("click", (e) => {
        if (accessibilityPanel && !accessibilityPanel.contains(e.target) && !accessibilityBtn?.contains(e.target)) {
            accessibilityPanel.classList.remove("show");
            accessibilityBtn?.setAttribute("aria-expanded", "false");
            accessibilityPanel.setAttribute("aria-hidden", "true");
        }
    });

    // Keyboard physical Escape sequence panel closer
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && accessibilityPanel?.classList.contains("show")) {
            accessibilityPanel.classList.remove("show");
            accessibilityBtn?.setAttribute("aria-expanded", "false");
            accessibilityPanel?.setAttribute("aria-hidden", "true");
            accessibilityBtn?.focus(); 
        }
    });
});