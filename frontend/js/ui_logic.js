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


    // --- 4. Logika Upload Gambar ---
    const menuOpenImage = document.getElementById('menu-open-image');
    const fileUploadInput = document.getElementById('file-upload');
    
    // Elemen Kanvas Kiri (Original)
    const imgOriginal = document.getElementById('img-original');
    const placeholderOriginal = document.getElementById('placeholder-original');
    
    // Elemen Kanvas Kanan (Edited / Preview)
    const imgEdited = document.getElementById('img-edited');
    const placeholderEdited = document.getElementById('placeholder-edited');

    // Kalau menu "open image" diklik, trigger input file
    if (menuOpenImage && fileUploadInput) {
        menuOpenImage.addEventListener('click', () => {
            fileUploadInput.click();
        });
    }

    // Kalau user udah milih gambar
    if (fileUploadInput) {
        fileUploadInput.addEventListener('change', function(event) {
            const file = event.target.files[0]; 
            
            if (file) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    // 1. Set source gambar ke kedua kanvas
                    imgOriginal.src = e.target.result;
                    imgEdited.src = e.target.result; // Tampilkan juga di kanan sebagai preview awal
                    
                    // 2. Munculkan tag <img> di kedua kanvas
                    imgOriginal.classList.remove('hidden');
                    imgEdited.classList.remove('hidden');

                    // 3. Sembunyikan teks placeholder di kedua kanvas
                    placeholderOriginal.classList.add('hidden');
                    placeholderEdited.classList.add('hidden');
                }
                
                reader.readAsDataURL(file);
            }
        });
    }


    // --- 5. Logika Export / Download Gambar ---
    const btnExport = document.getElementById('btn-export');
    const menuSaveImage = document.getElementById('menu-save-image');

    // Fungsi utama untuk download
    const downloadImage = () => {
        // Cek apakah sudah ada gambar yang di-upload atau diedit
        if (!imgEdited.src || imgEdited.classList.contains('hidden')) {
            alert('Belum ada gambar yang bisa diekspor!');
            return;
        }

        // Ambil source gambar
        const imageURL = imgEdited.src;
        
        // Bikin elemen link (anchor) bayangan di memori
        const link = document.createElement('a');
        link.href = imageURL;
        
        // Tentukan nama file downloadnya
        link.download = 'poshop-edited-image.png'; 
        
        // Masukkan link ke dokumen sebentar, klik, lalu hapus lagi
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    // Pasang event listener ke tombol Export
    if (btnExport) {
        btnExport.addEventListener('click', downloadImage);
    }

    // Pasang event listener ke menu Save Image As
    if (menuSaveImage) {
        menuSaveImage.addEventListener('click', downloadImage);
    }


    // --- 6. Simulasi Efek Loading (Untuk Preview UI) ---
    const loadingOverlay = document.getElementById('loading-overlay');

    // Fungsi untuk memunculkan loading
    const showLoading = () => {
        if (loadingOverlay) {
            loadingOverlay.classList.remove('hidden');
            loadingOverlay.classList.add('flex'); // Pakai flex biar iconnya di tengah
        }
    };

    // Fungsi untuk menyembunyikan loading
    const hideLoading = () => {
        if (loadingOverlay) {
            loadingOverlay.classList.add('hidden');
            loadingOverlay.classList.remove('flex');
        }
    };

    // Pasang simulasi loading di semua input slider 
    // Kita pakai event 'change' bukan 'input'. 
    // 'input' jalan pas slider digeser. 'change' jalan pas mouse lu LEPAS dari slider.
    sliders.forEach(slider => {
        slider.addEventListener('change', () => {
            // Cek dulu, jangan sampe loading jalan padahal belum upload gambar
            if (imgEdited.src && !imgEdited.classList.contains('hidden')) {
                showLoading(); // Munculin loading

                // Pura-puranya nunggu Backend Python mikir selama 1.5 detik
                setTimeout(() => {
                    hideLoading(); // Matiin loading
                    console.log('Gambar selesai diproses backend (Simulasi)');
                }, 1500);
            } else {
                alert('Tolong upload gambar dulu sebelum mainan slider ya!');
                // Kembalikan nilai slider ke 0 karena belum ada gambar
                slider.value = 0;
                const display = slider.parentElement.querySelector('span:last-child');
                if(display) display.textContent = 0;
            }
        });
    });

}); 