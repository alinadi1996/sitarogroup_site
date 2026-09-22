(() => {
    "use strict";

    const tool = document.querySelector("[data-serp-tool]");
    if (!tool) return;

    const fields = Object.fromEntries(
        Array.from(tool.querySelectorAll("[data-serp-input]")).map((field) => [field.dataset.serpInput, field])
    );
    const outputs = Object.fromEntries(
        Array.from(tool.querySelectorAll("[data-serp-output]")).map((output) => [output.dataset.serpOutput, output])
    );
    const counters = Object.fromEntries(
        Array.from(tool.querySelectorAll("[data-serp-counter]")).map((counter) => [counter.dataset.serpCounter, counter])
    );
    const preview = tool.querySelector("[data-serp-preview]");
    const deviceButtons = Array.from(tool.querySelectorAll("[data-serp-device]"));
    const feedback = tool.querySelector("[data-serp-feedback]");
    const defaults = {
        siteName: "نام سایت شما",
        title: "عنوان نمونه برای پیش‌نمایش نتیجه",
        description: "این یک نمونه آموزشی است. برای مشاهده ظاهر تقریبی نتیجه، عنوان و توضیحات متای صفحه را وارد کنید.",
        breadcrumb: "example.com/example",
    };

    const trimText = (value) => value.trim();
    const normaliseUrl = (value) => {
        const trimmed = trimText(value);
        if (!trimmed) return defaults.breadcrumb;
        return trimmed.replace(/^https?:\/\//i, "").replace(/\/$/, "") || defaults.breadcrumb;
    };
    const escapeAttribute = (value) => value.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    const setFeedback = (message, isError = false) => {
        feedback.textContent = message;
        feedback.classList.toggle("is-error", isError);
    };
    const measureTitle = (text) => {
        const canvas = document.createElement("canvas");
        const context = canvas.getContext("2d");
        if (!context) return "";
        context.font = "20px Arial";
        return `، عرض تقریبی ${Math.round(context.measureText(text).width)}px`;
    };
    const updateCounter = (name, maximum, minimum) => {
        const value = trimText(fields[name].value);
        const length = value.length;
        let state = "short";
        let label = "کوتاه";
        if (length >= minimum && length <= maximum) {
            state = "good";
            label = "مناسب";
        } else if (length > maximum) {
            state = "long";
            label = "طولانی";
        }
        const widthHint = name === "title" && value ? measureTitle(value) : "";
        const counter = counters[name];
        counter.dataset.state = state;
        counter.textContent = `${length} کاراکتر · ${label}${widthHint}`;
    };
    const updatePreview = () => {
        const values = {
            siteName: trimText(fields.siteName.value) || defaults.siteName,
            title: trimText(fields.title.value) || defaults.title,
            description: trimText(fields.description.value) || defaults.description,
            breadcrumb: normaliseUrl(fields.url.value),
        };
        Object.entries(values).forEach(([name, value]) => {
            outputs[name].textContent = value;
        });
        updateCounter("title", 60, 25);
        updateCounter("description", 160, 70);
    };
    const setDevice = (device) => {
        const isMobile = device === "mobile";
        preview.classList.toggle("is-mobile", isMobile);
        preview.classList.toggle("is-desktop", !isMobile);
        preview.setAttribute("aria-labelledby", isMobile ? "serp-mobile-tab" : "serp-desktop-tab");
        deviceButtons.forEach((button) => button.setAttribute("aria-selected", String(button.dataset.serpDevice === device)));
    };
    const fallbackCopy = (value) => {
        const textarea = document.createElement("textarea");
        textarea.value = value;
        textarea.setAttribute("readonly", "");
        textarea.style.position = "fixed";
        textarea.style.opacity = "0";
        document.body.append(textarea);
        textarea.select();
        const copied = document.execCommand("copy");
        textarea.remove();
        return copied;
    };
    const copyMeta = async () => {
        const title = trimText(fields.title.value);
        const description = trimText(fields.description.value);
        if (!title && !description) {
            setFeedback("برای کپی، حداقل عنوان یا توضیحات متا را وارد کنید.", true);
            return;
        }
        const tags = [];
        if (title) tags.push(`<title>${escapeAttribute(title)}</title>`);
        if (description) tags.push(`<meta name="description" content="${escapeAttribute(description)}">`);
        const text = tags.join("\n");
        try {
            if (navigator.clipboard?.writeText) {
                await navigator.clipboard.writeText(text);
            } else if (!fallbackCopy(text)) {
                throw new Error("copy-failed");
            }
            setFeedback("متاتگ‌ها با موفقیت کپی شدند.");
        } catch (error) {
            setFeedback("کپی خودکار ممکن نشد. دسترسی Clipboard مرورگر را بررسی کنید.", true);
        }
    };

    Object.values(fields).forEach((field) => field.addEventListener("input", updatePreview));
    deviceButtons.forEach((button) => button.addEventListener("click", () => setDevice(button.dataset.serpDevice)));
    tool.querySelector("[data-serp-copy]").addEventListener("click", copyMeta);
    tool.querySelector("[data-serp-reset]").addEventListener("click", () => {
        Object.values(fields).forEach((field) => { field.value = ""; });
        updatePreview();
        setFeedback("ورودی‌ها پاک شدند و پیش‌نمایش به حالت آموزشی بازگشت.");
        fields.siteName.focus();
    });
    tool.querySelector("[data-serp-form]").addEventListener("submit", (event) => event.preventDefault());
    updatePreview();
})();
