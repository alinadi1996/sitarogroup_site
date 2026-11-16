(() => {
    "use strict";
    const form = document.querySelector("[data-image-converter]");
    if (!form) return;

    const fileInput = form.querySelector("#image-input");
    const dropZone = form.querySelector(".image-drop-zone");
    const preview = form.querySelector("[data-file-preview]");
    const icon = form.querySelector("[data-file-icon]");
    const fileName = form.querySelector("[data-file-name]");
    const fileDetail = form.querySelector("[data-file-detail]");
    const fileAction = form.querySelector("[data-file-action]");
    const quality = form.querySelector("#image-quality");
    const qualityValue = form.querySelector("#image-quality-value");
    const qualityHint = form.querySelector("#image-quality-hint");
    const svgNote = form.querySelector("[data-svg-note]");
    const error = form.querySelector("[data-converter-error]");
    const panel = form.querySelector("[data-progress-panel]");
    const progress = form.querySelector("progress");
    const status = form.querySelector("[data-progress-label]");
    const submit = form.querySelector("[type=submit]");
    const submitLabel = form.querySelector("[data-submit-label]");
    const download = form.querySelector("[data-download-link]");
    const formats = [...form.querySelectorAll("[name=output_format]")];
    const number = new Intl.NumberFormat("fa-IR");
    const sizeNumber = new Intl.NumberFormat("fa-IR", { maximumFractionDigits: 2 });
    let previewURL = null;
    let downloadURL = null;
    let busy = false;
    let dragDepth = 0;

    const selectedFormat = () => formats.find((radio) => radio.checked).value;
    const showError = (message) => {
        error.textContent = message;
        error.hidden = !message;
    };
    const clearDownload = () => {
        download.hidden = true;
        download.removeAttribute("href");
        if (downloadURL) URL.revokeObjectURL(downloadURL);
        downloadURL = null;
    };
    const showProgress = (message, value) => {
        panel.hidden = false;
        status.textContent = message;
        if (value === undefined) progress.removeAttribute("value");
        else progress.value = value;
    };
    const updateQuality = () => {
        const format = selectedFormat();
        quality.disabled = busy || format === "png";
        qualityValue.textContent = format === "png" ? "بدون افت" : `${number.format(quality.value)}٪`;
        quality.setAttribute("aria-valuetext", `${number.format(quality.value)} درصد`);
        qualityHint.textContent = format === "png"
            ? "PNG همیشه بدون افت کیفیت ذخیره می‌شود؛ تنظیم درصد کیفیت برای این فرمت کاربرد ندارد."
            : format === "svg"
                ? "درصد بالاتر، جزئیات و دقت رنگ بیشتری را در مسیرهای برداری حفظ می‌کند و ممکن است حجم خروجی را افزایش دهد."
                : "درصد بالاتر جزئیات بیشتری حفظ می‌کند؛ درصد کمتر معمولاً فایل سبک‌تری می‌سازد.";
        svgNote.hidden = format !== "svg";
    };
    const resetResult = () => {
        panel.hidden = true;
        progress.value = 0;
        showError("");
        clearDownload();
    };
    const resetPreview = () => {
        preview.hidden = true;
        preview.removeAttribute("src");
        if (previewURL) URL.revokeObjectURL(previewURL);
        previewURL = null;
        icon.hidden = false;
    };
    const updateFile = () => {
        resetResult();
        resetPreview();
        const file = fileInput.files[0];
        dropZone.classList.toggle("has-file", Boolean(file));
        fileName.textContent = file ? file.name : "تصویر یا ZIP تصاویر را اینجا رها کنید";
        fileAction.textContent = file ? "تغییر فایل" : "انتخاب فایل";
        icon.textContent = "↑";
        fileDetail.textContent = "PNG، JPG، JPEG، WebP، GIF، TIFF، BMP، AVIF یا ZIP";
        if (!file) return;
        if (!/\.(png|jpe?g|webp|gif|tiff?|bmp|avif|zip)$/i.test(file.name)) {
            fileInput.value = "";
            updateFile();
            showError("یک تصویر با فرمت پشتیبانی‌شده یا فایل ZIP انتخاب کنید.");
            return;
        }
        if (file.size > 25 * 1024 * 1024) {
            fileInput.value = "";
            updateFile();
            showError("حجم فایل نباید از ۲۵ مگابایت بیشتر باشد.");
            return;
        }
        const isZip = /\.zip$/i.test(file.name);
        icon.textContent = isZip ? "ZIP" : "IMG";
        const size = file.size < 1024 * 1024
            ? `${sizeNumber.format(file.size / 1024)} کیلوبایت`
            : `${sizeNumber.format(file.size / (1024 * 1024))} مگابایت`;
        fileDetail.textContent = `${size} · ${isZip ? "آرشیو تصاویر" : "تصویر آماده تبدیل"}`;
        if (!isZip) {
            previewURL = URL.createObjectURL(file);
            preview.src = previewURL;
        }
    };
    preview.addEventListener("load", () => { preview.hidden = false; icon.hidden = true; });
    preview.addEventListener("error", resetPreview);
    fileInput.addEventListener("change", updateFile);
    quality.addEventListener("input", updateQuality);
    quality.addEventListener("change", resetResult);
    formats.forEach((radio) => radio.addEventListener("change", () => { updateQuality(); resetResult(); }));

    ["dragenter", "dragover", "dragleave", "drop"].forEach((type) => {
        dropZone.addEventListener(type, (event) => {
            event.preventDefault();
            if (busy) return;
            if (type === "dragenter") dragDepth += 1;
            if (type === "dragleave") dragDepth = Math.max(0, dragDepth - 1);
            if (type === "dragover") event.dataTransfer.dropEffect = "copy";
            if (type === "drop") {
                dragDepth = 0;
                if (event.dataTransfer.files.length !== 1) {
                    fileInput.value = "";
                    updateFile();
                    showError("یک تصویر یا یک فایل ZIP انتخاب کنید.");
                } else {
                    fileInput.files = event.dataTransfer.files;
                    updateFile();
                }
            }
            dropZone.classList.toggle("is-dragging", dragDepth > 0);
        });
    });

    const setBusy = (value) => {
        busy = value;
        form.setAttribute("aria-busy", String(value));
        fileInput.disabled = value;
        formats.forEach((radio) => { radio.disabled = value; });
        submit.disabled = value;
        submitLabel.textContent = value ? "در حال تبدیل…" : "تبدیل و دانلود";
        dropZone.classList.toggle("is-busy", value);
        updateQuality();
    };
    const responseFilename = (request, fallback) => {
        const header = request.getResponseHeader("Content-Disposition") || "";
        const encoded = header.match(/filename\*=UTF-8''([^;]+)/i);
        if (encoded) {
            try { return decodeURIComponent(encoded[1]); } catch { return fallback; }
        }
        return header.match(/filename="([^"]+)"/i)?.[1] || fallback;
    };
    form.addEventListener("submit", (event) => {
        event.preventDefault();
        if (busy || !form.reportValidity()) return;
        resetResult();
        const file = fileInput.files[0];
        const format = selectedFormat();
        const payload = new FormData(form);
        payload.set("quality", quality.value);
        const extension = format === "jpeg" ? "jpg" : format;
        const fallbackName = /\.zip$/i.test(file.name)
            ? `sitaro-images-${format}.zip`
            : `${file.name.replace(/\.[^.]+$/, "")}.${extension}`;
        const request = new XMLHttpRequest();
        request.open("POST", form.action);
        request.setRequestHeader("X-Requested-With", "XMLHttpRequest");
        request.responseType = "blob";
        request.timeout = 120000;
        request.upload.addEventListener("progress", (upload) => {
            if (!upload.lengthComputable) return;
            const percent = Math.round(upload.loaded / upload.total * 100);
            showProgress(`در حال بارگذاری · ${number.format(percent)}٪`, percent);
        });
        request.upload.addEventListener("load", () => { showProgress("بارگذاری کامل شد؛ در حال تبدیل تصویر…"); });
        request.addEventListener("progress", (transfer) => {
            if (request.status !== 200) return;
            if (transfer.lengthComputable) {
                const percent = Math.round(transfer.loaded / transfer.total * 100);
                showProgress(`در حال دریافت خروجی · ${number.format(percent)}٪`, percent);
            } else showProgress("تبدیل انجام شد؛ در حال دریافت خروجی…");
        });
        const fail = (message) => {
            showError(message);
            showProgress("تبدیل انجام نشد. می‌توانید دوباره تلاش کنید.", 0);
        };
        request.addEventListener("load", async () => {
            try {
                if (request.status !== 200) {
                    let message = request.status === 413 ? "حجم فایل از حد مجاز سرور بیشتر است." : "تبدیل انجام نشد. فایل را بررسی کنید و دوباره تلاش کنید.";
                    try { message = JSON.parse(await request.response.text()).error || message; } catch { /* Keep the safe fallback for HTML error pages. */ }
                    fail(message);
                    return;
                }
                const expectedType = /\.zip$/i.test(file.name) ? "application/zip" : { webp: "image/webp", png: "image/png", jpeg: "image/jpeg", svg: "image/svg+xml" }[format];
                if (!request.response.size || request.response.type.split(";")[0] !== expectedType) {
                    fail("پاسخ سرور یک فایل خروجی معتبر نیست. دوباره تلاش کنید.");
                    return;
                }
                downloadURL = URL.createObjectURL(request.response);
                download.href = downloadURL;
                download.download = responseFilename(request, fallbackName);
                download.hidden = false;
                showProgress("تبدیل کامل شد · ۱۰۰٪ · فایل آماده دانلود است.", 100);
                download.click();
            } finally { setBusy(false); }
        });
        request.addEventListener("error", () => { fail("ارتباط با سرور برقرار نشد. اتصال اینترنت را بررسی کنید."); setBusy(false); });
        request.addEventListener("timeout", () => { fail("زمان تبدیل بیش از حد طول کشید. تصویر کوچک‌تر یا ZIP با تصاویر کمتر را امتحان کنید."); setBusy(false); });
        request.addEventListener("abort", () => { fail("تبدیل متوقف شد."); setBusy(false); });
        setBusy(true);
        showProgress("در حال بارگذاری…", 0);
        try { request.send(payload); }
        catch { fail("ارسال فایل ممکن نشد. دوباره تلاش کنید."); setBusy(false); }
    });
    window.addEventListener("pagehide", () => { resetPreview(); clearDownload(); });
    window.addEventListener("pageshow", (event) => { if (event.persisted) updateFile(); });
    updateQuality();
})();
