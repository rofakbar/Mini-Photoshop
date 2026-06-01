/**
 * UI Logic for Mini Photoshop
 * Mengatur interaksi antarmuka + komunikasi ke backend Flask
 */

const API = 'http://localhost:5000';

// ─── Helper: kirim request ke backend ───────────────────────────────────────

async function callBackend(endpoint, body = null, file = null) {
    showLoading();
    try {
        let response;
        if (file) {
            const formData = new FormData();
            formData.append('image', file);
            response = await fetch(`${API}${endpoint}`, { method: 'POST', body: formData });
        } else {
            response = await fetch(`${API}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body || {})
            });
        }
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            const data = await response.json();
            if (data.error) throw new Error(data.error);
            return data;
        } else {
            const blob = await response.blob();
            const objectUrl = URL.createObjectURL(blob);
            return {
                image: objectUrl,
                original_size_kb: response.headers.get("X-Original-Size-KB"),
                compressed_size_kb: response.headers.get("X-Compressed-Size-KB")
            };
        }
    } catch (err) {
        alert('Error: ' + err.message);
        return null;
    } finally {
        hideLoading();
    }
}

function showResult(base64Image) {
    if (!base64Image) return;
    imgEdited.src = base64Image;
    imgEdited.classList.remove('hidden');
    placeholderEdited.classList.add('hidden');
    updateHistograms();
}

// ─── Elemen DOM ─────────────────────────────────────────────────────────────

const imgOriginal         = document.getElementById('img-original');
const placeholderOriginal = document.getElementById('placeholder-original');
const imgEdited           = document.getElementById('img-edited');
const placeholderEdited   = document.getElementById('placeholder-edited');
const loadingOverlay      = document.getElementById('loading-overlay');

const showLoading = () => {
    if (loadingOverlay) { loadingOverlay.classList.remove('hidden'); loadingOverlay.classList.add('flex'); }
};
const hideLoading = () => {
    if (loadingOverlay) { loadingOverlay.classList.add('hidden'); loadingOverlay.classList.remove('flex'); }
};

// ─── Histogram ──────────────────────────────────────────────────────────────

const histOriginal        = document.getElementById('hist-original');
const histEdited          = document.getElementById('hist-edited');
const placeholderHistOrig = document.getElementById('placeholder-hist-orig');
const placeholderHistEdit = document.getElementById('placeholder-hist-edit');

async function updateHistograms() {
    try {
        const [origResp, editResp] = await Promise.all([
            fetch(`${API}/histogram/original`),
            fetch(`${API}/histogram/current`)
        ]);
        const origData = await origResp.json();
        const editData = await editResp.json();

        if (origData.image && histOriginal) {
            histOriginal.src = origData.image;
            histOriginal.classList.remove('hidden');
            if (placeholderHistOrig) placeholderHistOrig.classList.add('hidden');
        }
        if (editData.image && histEdited) {
            histEdited.src = editData.image;
            histEdited.classList.remove('hidden');
            if (placeholderHistEdit) placeholderHistEdit.classList.add('hidden');
        }
    } catch (e) {
        console.log('Histogram update failed:', e);
    }
}

// ─── Inisialisasi ────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {

    // 1. Accordion (Buka-Tutup Panel Sidebar)
    document.querySelectorAll('.accordion-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const content = this.nextElementSibling;
            const icon = this.querySelector('.accordion-icon');
            content.classList.toggle('hidden');
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

    // 2. Slider display value (update angka saat digeser)
    const sliders = document.querySelectorAll('input[type="range"]');
    sliders.forEach(slider => {
        slider.addEventListener('input', function () {
            if (this.id && this.id.startsWith('slider-')) {
                const display = document.getElementById(this.id.replace('slider-', 'val-'));
                if (display) display.textContent = this.value;
            }
        });
    });

    // 3. Upload Gambar
    const menuOpenImage   = document.getElementById('menu-open-image');
    const fileUploadInput = document.getElementById('file-upload');

    if (menuOpenImage && fileUploadInput) {
        menuOpenImage.addEventListener('click', () => fileUploadInput.click());
    }

    if (fileUploadInput) {
        fileUploadInput.addEventListener('change', async function (e) {
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (ev) => {
                imgOriginal.src = ev.target.result;
                imgOriginal.classList.remove('hidden');
                placeholderOriginal.classList.add('hidden');
            };
            reader.readAsDataURL(file);
            const data = await callBackend('/upload', null, file);
            if (data) showResult(data.image);
        });
    }

    // 4. Reset — panggil backend + kembalikan semua slider ke nilai default
    const resetBtn = document.querySelector('nav button:first-of-type');
    if (resetBtn) {
        resetBtn.addEventListener('click', async () => {
            if (!confirm('Apakah Anda yakin ingin meriset semua perubahan?')) return;

            // Reset semua slider ke 0 dan update tampilan angkanya
            sliders.forEach(slider => {
                slider.value = 0;
                const display = slider.parentElement.querySelector('span:last-child');
                if (display) display.textContent = 0;
            });

            // Kirim reset ke backend
            const data = await callBackend('/reset', {});
            if (data) showResult(data.image);

            console.log('UI Reset to default state');
        });
    }

    // 5. Export / Download Gambar
    const downloadImage = () => {
        if (!imgEdited.src || imgEdited.classList.contains('hidden')) {
            alert('Belum ada gambar yang bisa diekspor!'); return;
        }
        const link = document.createElement('a');
        link.href = imgEdited.src;
        link.download = 'poshop-edited-image.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };
    document.getElementById('btn-export')?.addEventListener('click', downloadImage);
    document.getElementById('menu-save-image')?.addEventListener('click', downloadImage);

    // Helper: cek apakah sudah ada gambar
    const hasImage = () => {
        if (imgEdited.classList.contains('hidden')) { alert('Tolong upload gambar dulu sebelum mainan slider ya!'); return false; }
        return true;
    };

    // --- 6. Image Enhancement ---
    document.getElementById('btn-apply-enhance')?.addEventListener('click', async () => {
        if (!hasImage()) return;
        const bright = document.getElementById('slider-bright')?.value || 0;
        const contrast = document.getElementById('slider-contrast')?.value || 0;
        const blurK = document.getElementById('slider-blur')?.value || 1;
        
        let needsUpdate = false;
        if (bright != 0 || contrast != 0) {
            const data1 = await callBackend('/enhance/brightness-contrast', { brightness: parseInt(bright), contrast: parseInt(contrast) });
            if (data1) { showResult(data1.image); needsUpdate = true; }
        }
        
        if (blurK > 1) {
            const data2 = await callBackend('/enhance/blur', { kernel_size: parseInt(blurK) });
            if (data2) showResult(data2.image);
        }
    });

    document.querySelector('[data-action="hist-eq"]')?.addEventListener('click', async () => {
        if (!hasImage()) return;
        const data = await callBackend('/enhance/histogram-eq', {});
        if (data) showResult(data.image);
    });

    document.querySelector('[data-action="sharpen"]')?.addEventListener('click', async () => {
        if (!hasImage()) return;
        const data = await callBackend('/enhance/sharpen', {});
        if (data) showResult(data.image);
    });

    // --- 7. Geometric Transform ---
    document.getElementById('btn-apply-rotate')?.addEventListener('click', async () => {
        if (!hasImage()) return;
        const angle = document.getElementById('slider-rotate')?.value || 0;
        const data = await callBackend('/transform/rotate', { angle: parseFloat(angle) });
        if (data) showResult(data.image);
    });

    document.querySelector('[data-action="flip-h"]')?.addEventListener('click', async () => {
        if (!hasImage()) return;
        const data = await callBackend('/transform/flip', { direction: 'horizontal' });
        if (data) showResult(data.image);
    });

    document.querySelector('[data-action="flip-v"]')?.addEventListener('click', async () => {
        if (!hasImage()) return;
        const data = await callBackend('/transform/flip', { direction: 'vertical' });
        if (data) showResult(data.image);
    });

    document.getElementById('btn-apply-crop')?.addEventListener('click', async () => {
        if (!hasImage()) return;
        const x = document.getElementById('crop-x')?.value || 0;
        const y = document.getElementById('crop-y')?.value || 0;
        const w = document.getElementById('crop-w')?.value || 100;
        const h = document.getElementById('crop-h')?.value || 100;
        const data = await callBackend('/transform/crop', { x: parseInt(x), y: parseInt(y), width: parseInt(w), height: parseInt(h) });
        if (data) showResult(data.image);
    });

    document.getElementById('btn-apply-resize')?.addEventListener('click', async () => {
        if (!hasImage()) return;
        const w = document.getElementById('resize-w')?.value || 100;
        const h = document.getElementById('resize-h')?.value || 100;
        const data = await callBackend('/transform/resize', { width: parseInt(w), height: parseInt(h), interpolation: 'bilinear' });
        if (data) showResult(data.image);
    });

    document.getElementById('btn-apply-translate')?.addEventListener('click', async () => {
        if (!hasImage()) return;
        const tx = document.getElementById('trans-x')?.value || 0;
        const ty = document.getElementById('trans-y')?.value || 0;
        const data = await callBackend('/transform/translate', { tx: parseInt(tx), ty: parseInt(ty) });
        if (data) showResult(data.image);
    });

    // --- 8. Image Restoration ---
    document.getElementById('btn-apply-gauss')?.addEventListener('click', async () => {
        if (!hasImage()) return;
        const k = document.getElementById('slider-gauss')?.value || 1;
        const data = await callBackend('/filter/gaussian', { kernel_size: parseInt(k), sigma: 0 });
        if (data) showResult(data.image);
    });

    document.getElementById('btn-apply-median')?.addEventListener('click', async () => {
        if (!hasImage()) return;
        const k = document.getElementById('slider-median')?.value || 1;
        const data = await callBackend('/filter/median', { kernel_size: parseInt(k) });
        if (data) showResult(data.image);
    });

    document.getElementById('btn-apply-denoise')?.addEventListener('click', async () => {
        if (!hasImage()) return;
        const data = await callBackend('/filter/denoise', { kernel_size: 3 }); 
        if (data) showResult(data.image);
    });

    // --- 9. Binary & Edge ---
    document.getElementById('btn-apply-thresh')?.addEventListener('click', async () => {
        if (!hasImage()) return;
        const val = document.getElementById('slider-thresh')?.value || 127;
        const data = await callBackend('/binary/threshold', { value: parseInt(val) });
        if (data) showResult(data.image);
    });

    document.getElementById('btn-apply-edge')?.addEventListener('click', async () => {
        if (!hasImage()) return;
        const method = document.getElementById('edge-method')?.value || 'canny';
        const data = await callBackend('/edge/detect', { method: method });
        if (data) showResult(data.image);
    });

    document.getElementById('btn-apply-morph')?.addEventListener('click', async () => {
        if (!hasImage()) return;
        const operation = document.getElementById('morph-method')?.value || 'erosion';
        const data = await callBackend('/morphology', { operation: operation, kernel_size: 5 });
        if (data) showResult(data.image);
    });

    // --- 10. Color Processing ---
    document.querySelector('[data-action="grayscale"]')?.addEventListener('click', async () => {
        if (!hasImage()) return;
        const data = await callBackend('/color/grayscale', {});
        if (data) showResult(data.image);
    });

    ['r', 'g', 'b'].forEach(ch => {
        document.querySelector(`[data-action="channel-${ch}"]`)?.addEventListener('click', async () => {
            if (!hasImage()) return;
            const data = await callBackend('/color/split-channel', { channel: ch });
            if (data) showResult(data.image);
        });
    });

    document.getElementById('btn-apply-hsv')?.addEventListener('click', async () => {
        if (!hasImage()) return;
        const hue = document.getElementById('slider-hue')?.value || 0;
        const sat = document.getElementById('slider-sat')?.value || 100;
        const data = await callBackend('/color/adjust-hue-saturation', { hue: parseInt(hue), saturation: parseInt(sat) });
        if (data) showResult(data.image);
    });

    // --- 11. Image Segmentation ---
    document.getElementById('btn-apply-seg')?.addEventListener('click', async () => {
        if (!hasImage()) return;
        const method = document.getElementById('seg-method')?.value || 'threshold';
        const data = await callBackend('/segment', { method: method });
        if (data) showResult(data.image);
    });

    // --- 12. Image Compression ---
    document.getElementById('btn-apply-compress')?.addEventListener('click', async () => {
        if (!hasImage()) return;
        const quality = document.getElementById('slider-compress')?.value || 50;
        const data = await callBackend('/compress', { quality: parseInt(quality) });
        if (data) {
            showResult(data.image);
            const infoBox = document.getElementById('compress-info');
            const spanOrig = document.getElementById('comp-orig');
            const spanNew = document.getElementById('comp-new');
            if (infoBox && spanOrig && spanNew) {
                spanOrig.textContent = data.original_size_kb;
                spanNew.textContent = data.compressed_size_kb;
                infoBox.classList.remove('hidden');
            }
        }
    });

});