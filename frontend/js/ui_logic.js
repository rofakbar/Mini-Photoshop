/**
 * UI Logic for Mini Photoshop
 * Mengatur interaksi antarmuka seperti Accordion dan Slider
 */

document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. Logika Accordion (Buka-Tutup Panel Sidebar) ---
    const accordionBtns = document.querySelectorAll('.accordion-btn');

    accordionBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Mencari elemen konten setelah tombol (accordion-content)
            const content = this.nextElementSibling;
            // Mencari icon panah di dalam tombol
            const icon = this.querySelector('.accordion-icon');

            // Toggle class 'hidden' (Tailwind class untuk display: none)
            content.classList.toggle('hidden');

            // Update UI tombol saat terbuka/tertutup
            if (content.classList.contains('hidden')) {
                icon.textContent = '▶';
                this.classList.remove('bg-gray-700/30', 'text-gray-200', 'font-semibold');
                this.classList.add('text-gray-400');
            } else {
                icon.textContent = '▼';
                this.classList.add('bg-gray-700/30', 'text-gray-200', 'font-semibold');
                this.classList.remove('text-gray-400');
            }
        });
    });

    // --- 2. Logika Update Nilai Slider (Brightness/Contrast) ---
    const sliders = document.querySelectorAll('input[type="range"]');
    
    sliders.forEach(slider => {
        slider.addEventListener('input', function() {
            // Mencari elemen span yang menampilkan angka (di atas slider)
            const valueDisplay = this.parentElement.querySelector('span:last-child');
            if (valueDisplay) {
                valueDisplay.textContent = this.value;
            }
        });
    });

    // --- 3. Logika Reset Global ---
    const resetBtn = document.querySelector('nav button:first-of-type'); // Tombol RESET di navbar
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            if(confirm('Apakah Anda yakin ingin meriset semua perubahan?')) {
                // Reset semua slider ke 0
                sliders.forEach(slider => {
                    slider.value = 0;
                    const display = slider.parentElement.querySelector('span:last-child');
                    if(display) display.textContent = 0;
                });
                console.log('UI Reset to default state');
            }
        });
    }

});