(() => {
    "use strict";

    const tool = document.querySelector("[data-schema-tool]");
    if (!tool) return;

    const typeButtons = Array.from(tool.querySelectorAll("[data-schema-type]"));
    const fieldsRoot = tool.querySelector("[data-schema-fields]");
    const formTitle = tool.querySelector("[data-schema-form-title]");
    const errorsRoot = tool.querySelector("[data-schema-errors]");
    const warningsRoot = tool.querySelector("[data-schema-warnings]");
    const codeRoot = tool.querySelector("[data-schema-code]");
    const outputStatus = tool.querySelector("[data-schema-output-status]");
    const feedback = tool.querySelector("[data-schema-feedback]");
    const form = tool.querySelector("[data-schema-form]");
    const state = { type: "organization", values: {}, socials: [""], crumbs: [{ name: "", url: "" }, { name: "", url: "" }], output: null, interacted: false };

    const typeLabels = { organization: "اطلاعات سازمان", localBusiness: "اطلاعات کسب‌وکار محلی", article: "اطلاعات مقاله", product: "اطلاعات محصول", breadcrumb: "مسیر صفحه" };
    const fieldSets = {
        organization: [
            ["name", "نام سازمان", "text", true, "مثال: نام سازمان شما"], ["url", "URL رسمی", "url", true, "https://example.com"],
            ["logo", "URL لوگو", "url", false, "https://example.com/logo.svg"], ["legalName", "نام قانونی", "text", false, ""],
            ["description", "توضیح کوتاه", "textarea", false, ""], ["telephone", "شماره تلفن", "tel", false, ""], ["email", "ایمیل", "email", false, "name@example.com"],
        ],
        localBusiness: [
            ["name", "نام کسب‌وکار", "text", true, ""], ["url", "URL رسمی", "url", true, "https://example.com"], ["image", "URL تصویر یا لوگو", "url", false, ""],
            ["telephone", "شماره تماس", "tel", false, ""], ["priceRange", "محدوده قیمت", "text", false, "مثال: $$"], ["businessType", "نوع کسب‌وکار", "text", false, "LocalBusiness"],
            ["country", "کشور", "text", true, "مثال: IR"], ["region", "استان", "text", false, ""], ["city", "شهر", "text", true, ""], ["streetAddress", "آدرس", "textarea", true, ""],
            ["postalCode", "کد پستی", "text", false, ""], ["latitude", "عرض جغرافیایی", "number", false, "35.6892"], ["longitude", "طول جغرافیایی", "number", false, "51.3890"],
            ["openingDays", "روزهای کاری", "text", false, "مثال: Saturday,Sunday"], ["opens", "ساعت بازشدن", "time", false, ""], ["closes", "ساعت بسته‌شدن", "time", false, ""],
        ],
        article: [
            ["articleType", "نوع مقاله", "select", true, "", [["Article", "Article"], ["BlogPosting", "BlogPosting"]]], ["headline", "عنوان", "text", true, ""], ["url", "URL صفحه", "url", true, "https://example.com/article"],
            ["description", "توضیح", "textarea", false, ""], ["image", "URL تصویر شاخص", "url", true, "https://example.com/image.jpg"], ["authorName", "نام نویسنده", "text", true, ""],
            ["authorType", "نوع نویسنده", "select", true, "", [["Person", "Person"], ["Organization", "Organization"]]], ["authorUrl", "URL نویسنده", "url", false, ""],
            ["datePublished", "تاریخ انتشار", "date", true, ""], ["dateModified", "تاریخ ویرایش", "date", false, ""], ["publisherName", "نام ناشر", "text", true, ""], ["publisherLogo", "URL لوگوی ناشر", "url", false, ""],
        ],
        product: [
            ["name", "نام محصول", "text", true, ""], ["url", "URL محصول", "url", true, "https://example.com/product"], ["description", "توضیح", "textarea", false, ""],
            ["image", "URL تصویر محصول", "url", true, "https://example.com/product.jpg"], ["brand", "برند", "text", false, ""], ["sku", "SKU", "text", false, ""], ["mpn", "MPN", "text", false, ""], ["gtin", "GTIN", "text", false, ""],
            ["price", "قیمت", "number", true, "0"], ["priceCurrency", "واحد پول", "text", true, "IRR"], ["availability", "موجودی", "select", true, "", [["InStock", "InStock"], ["OutOfStock", "OutOfStock"], ["PreOrder", "PreOrder"], ["BackOrder", "BackOrder"]]],
            ["itemCondition", "وضعیت کالا", "select", true, "", [["NewCondition", "NewCondition"], ["UsedCondition", "UsedCondition"], ["RefurbishedCondition", "RefurbishedCondition"]]], ["priceValidUntil", "تاریخ اعتبار قیمت", "date", false, ""],
        ],
    };

    const clear = (node) => { while (node.firstChild) node.removeChild(node.firstChild); };
    const create = (tag, className, text) => { const el = document.createElement(tag); if (className) el.className = className; if (text !== undefined) el.textContent = text; return el; };
    const inputId = (name) => `schema-${state.type}-${name}`;
    const valueOf = (name) => (state.values[name] || "").trim();
    const urlIsValid = (value) => { try { const url = new URL(value); return ["http:", "https:"].includes(url.protocol); } catch { return false; } };
    const emailIsValid = (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    const isoDate = (value) => /^\d{4}-\d{2}-\d{2}$/.test(value) && !Number.isNaN(Date.parse(value));
    const setFeedback = (message, error = false) => { feedback.textContent = message; feedback.classList.toggle("is-error", error); };
    const removeEmpty = (value) => {
        if (Array.isArray(value)) { const output = value.map(removeEmpty).filter((item) => item && (!Array.isArray(item) || item.length)); return output.length ? output : undefined; }
        if (value && typeof value === "object") { const output = Object.fromEntries(Object.entries(value).map(([key, item]) => [key, removeEmpty(item)]).filter(([, item]) => item !== undefined && item !== "")); return Object.keys(output).length ? output : undefined; }
        return value === "" || value === null || value === undefined ? undefined : value;
    };

    const addField = ([name, label, type, required, placeholder, options]) => {
        const wrap = create("div", "schema-field");
        const labelEl = create("label", "", label);
        labelEl.htmlFor = inputId(name);
        const marker = create("span", required ? "is-required" : "is-optional", required ? "ضروری" : "اختیاری");
        labelEl.append(marker);
        wrap.append(labelEl);
        let control;
        if (type === "textarea") { control = document.createElement("textarea"); control.rows = 4; }
        else if (type === "select") { control = document.createElement("select"); options.forEach(([value, optionLabel]) => { const option = new Option(optionLabel, value); control.add(option); }); }
        else { control = document.createElement("input"); control.type = type; if (type === "number") { control.step = "any"; control.min = "0"; } }
        const defaults = { businessType: "LocalBusiness", priceCurrency: "IRR", availability: "InStock", itemCondition: "NewCondition", articleType: "Article", authorType: "Person" };
        const initialValue = state.values[name] ?? (defaults[name] || "");
        control.id = inputId(name); control.name = name; control.placeholder = placeholder; control.required = required; control.value = initialValue;
        if (!(name in state.values)) state.values[name] = initialValue;
        if (["url", "image", "logo", "authorUrl", "publisherLogo"].includes(name)) { control.dir = "ltr"; control.inputMode = "url"; }
        control.addEventListener("input", () => { state.interacted = true; state.values[name] = control.value; updateOutput(); });
        control.addEventListener("change", () => { state.interacted = true; state.values[name] = control.value; updateOutput(); });
        wrap.append(control);
        const error = create("p", "schema-field-error"); error.dataset.schemaErrorFor = name; error.hidden = true; wrap.append(error);
        fieldsRoot.append(wrap);
    };
    const addCollectionHeading = (title, copy, actionText, action) => {
        const head = create("div", "schema-collection-head"); const group = create("div"); group.append(create("h3", "", title), create("p", "", copy));
        const button = create("button", "schema-inline-button", actionText); button.type = "button"; button.addEventListener("click", action); head.append(group, button); fieldsRoot.append(head);
    };
    const renderSocials = () => {
        addCollectionHeading("شبکه‌های اجتماعی", "URL هر پروفایل را جداگانه وارد کنید.", "افزودن لینک", () => { state.socials.push(""); renderForm(); });
        state.socials.forEach((value, index) => { const row = create("div", "schema-collection-row"); const input = document.createElement("input"); input.type = "url"; input.dir = "ltr"; input.inputMode = "url"; input.placeholder = "https://social.example/profile"; input.value = value; input.setAttribute("aria-label", `لینک شبکه اجتماعی ${index + 1}`); input.addEventListener("input", () => { state.interacted = true; state.socials[index] = input.value; updateOutput(); }); const remove = create("button", "schema-row-remove", "حذف"); remove.type = "button"; remove.disabled = state.socials.length === 1; remove.addEventListener("click", () => { state.interacted = true; state.socials.splice(index, 1); renderForm(); updateOutput(); }); row.append(input, remove); fieldsRoot.append(row); });
    };
    const renderBreadcrumbs = () => {
        addCollectionHeading("ردیف‌های مسیر", "حداقل دو مسیر کامل وارد کنید. جایگاه هر ردیف خودکار تعیین می‌شود.", "افزودن ردیف", () => { state.crumbs.push({ name: "", url: "" }); renderForm(); });
        state.crumbs.forEach((crumb, index) => { const row = create("div", "schema-breadcrumb-row"); const indexEl = create("b", "", String(index + 1).padStart(2, "0")); const name = document.createElement("input"); name.type = "text"; name.placeholder = "نام مسیر"; name.value = crumb.name; name.setAttribute("aria-label", `نام مسیر ${index + 1}`); name.addEventListener("input", () => { state.interacted = true; state.crumbs[index].name = name.value; updateOutput(); }); const url = document.createElement("input"); url.type = "url"; url.dir = "ltr"; url.inputMode = "url"; url.placeholder = "https://example.com"; url.value = crumb.url; url.setAttribute("aria-label", `URL مسیر ${index + 1}`); url.addEventListener("input", () => { state.interacted = true; state.crumbs[index].url = url.value; updateOutput(); }); const controls = create("div", "schema-row-controls"); [["↑", -1, "انتقال به بالا"], ["↓", 1, "انتقال به پایین"]].forEach(([text, delta, label]) => { const button = create("button", "", text); button.type = "button"; button.disabled = index + delta < 0 || index + delta >= state.crumbs.length; button.setAttribute("aria-label", label); button.addEventListener("click", () => { state.interacted = true; const next = index + delta; [state.crumbs[index], state.crumbs[next]] = [state.crumbs[next], state.crumbs[index]]; renderForm(); updateOutput(); }); controls.append(button); }); const remove = create("button", "schema-row-remove", "حذف"); remove.type = "button"; remove.disabled = state.crumbs.length <= 2; remove.addEventListener("click", () => { state.interacted = true; state.crumbs.splice(index, 1); renderForm(); updateOutput(); }); controls.append(remove); row.append(indexEl, name, url, controls); fieldsRoot.append(row); });
    };
    const renderForm = () => { clear(fieldsRoot); if (state.type === "breadcrumb") renderBreadcrumbs(); else { fieldSets[state.type].forEach(addField); if (state.type === "organization") renderSocials(); if (state.type === "product") { const note = create("p", "schema-currency-note", "IRR معادل ریال است. اگر قیمت سایت تومان است، مقدار و واحد پول را با ساختار واقعی سایت هماهنگ کنید."); fieldsRoot.append(note); } } formTitle.textContent = typeLabels[state.type]; };
    const setFieldErrors = (errors) => { tool.querySelectorAll("[data-schema-error-for]").forEach((node) => { node.hidden = true; node.textContent = ""; }); Object.entries(errors).forEach(([name, message]) => { const node = tool.querySelector(`[data-schema-error-for="${name}"]`); if (node) { node.textContent = `خطا: ${message}`; node.hidden = false; } }); };
    const validate = () => {
        const errors = {}; const warnings = []; const required = (name, label) => { if (!valueOf(name)) errors[name] = `${label} را وارد کنید.`; };
        const validUrl = (name, label) => { const value = valueOf(name); if (value && !urlIsValid(value)) errors[name] = `${label} باید با http یا https شروع شود.`; };
        const validDate = (name, label) => { const value = valueOf(name); if (value && !isoDate(value)) errors[name] = `${label} معتبر نیست.`; };
        if (state.type === "organization") { required("name", "نام سازمان"); required("url", "URL رسمی"); ["url", "logo"].forEach((name) => validUrl(name, name === "url" ? "URL رسمی" : "URL لوگو")); if (valueOf("email") && !emailIsValid(valueOf("email"))) errors.email = "ایمیل معتبر نیست."; if (!valueOf("logo")) warnings.push("هشدار: لوگوی سازمان وارد نشده است."); state.socials.filter(Boolean).forEach((url) => { if (!urlIsValid(url)) errors.socials = "هر لینک شبکه اجتماعی باید URL معتبر باشد."; }); }
        if (state.type === "localBusiness") { [ ["name", "نام کسب‌وکار"], ["url", "URL"], ["country", "کشور"], ["city", "شهر"], ["streetAddress", "آدرس"] ].forEach(([name, label]) => required(name, label)); ["url", "image"].forEach((name) => validUrl(name, name === "url" ? "URL" : "URL تصویر")); const lat = valueOf("latitude"), lng = valueOf("longitude"); if ((lat && !lng) || (!lat && lng)) errors.coordinates = "عرض و طول جغرافیایی باید با هم وارد شوند."; if (lat && (Number(lat) < -90 || Number(lat) > 90)) errors.latitude = "عرض جغرافیایی باید بین ۹۰- و ۹۰ باشد."; if (lng && (Number(lng) < -180 || Number(lng) > 180)) errors.longitude = "طول جغرافیایی باید بین ۱۸۰- و ۱۸۰ باشد."; const hours = [valueOf("openingDays"), valueOf("opens"), valueOf("closes")]; if (hours.some(Boolean) && !hours.every(Boolean)) errors.openingHours = "روزها و ساعت باز و بسته‌شدن باید کامل وارد شوند."; if (!hours.some(Boolean)) warnings.push("هشدار: ساعت کاری کسب‌وکار وارد نشده است."); }
        if (state.type === "article") { [ ["headline", "عنوان"], ["url", "URL صفحه"], ["image", "تصویر شاخص"], ["authorName", "نام نویسنده"], ["datePublished", "تاریخ انتشار"], ["publisherName", "نام ناشر"] ].forEach(([name, label]) => required(name, label)); ["url", "image", "authorUrl", "publisherLogo"].forEach((name) => validUrl(name, name)); validDate("datePublished", "تاریخ انتشار"); validDate("dateModified", "تاریخ ویرایش"); if (valueOf("dateModified") && valueOf("datePublished") && valueOf("dateModified") < valueOf("datePublished")) warnings.push("هشدار: تاریخ ویرایش از تاریخ انتشار قدیمی‌تر است."); }
        if (state.type === "product") { [ ["name", "نام محصول"], ["url", "URL محصول"], ["image", "تصویر محصول"], ["price", "قیمت"], ["priceCurrency", "واحد پول"] ].forEach(([name, label]) => required(name, label)); ["url", "image"].forEach((name) => validUrl(name, name)); if (valueOf("price") && (Number.isNaN(Number(valueOf("price"))) || Number(valueOf("price")) < 0)) errors.price = "قیمت باید عددی نامنفی باشد."; if (valueOf("priceCurrency") && !/^[A-Za-z]{3}$/.test(valueOf("priceCurrency"))) errors.priceCurrency = "واحد پول باید سه حرف انگلیسی باشد."; validDate("priceValidUntil", "تاریخ اعتبار قیمت"); if (!valueOf("brand") && !valueOf("sku")) warnings.push("هشدار: محصول فاقد برند یا SKU است."); }
        if (state.type === "breadcrumb") { if (state.crumbs.length < 2) errors.breadcrumb = "حداقل دو ردیف مسیر لازم است."; state.crumbs.forEach((crumb, index) => { if (!crumb.name.trim() || !crumb.url.trim()) errors.breadcrumb = `ردیف ${index + 1} باید نام و URL کامل داشته باشد.`; else if (!urlIsValid(crumb.url.trim())) errors.breadcrumb = `URL ردیف ${index + 1} معتبر نیست.`; }); }
        return { errors, warnings };
    };
    const buildOutput = () => {
        const value = valueOf; let object;
        if (state.type === "organization") object = { "@context": "https://schema.org", "@type": "Organization", name: value("name"), url: value("url"), logo: value("logo"), legalName: value("legalName"), description: value("description"), telephone: value("telephone"), email: value("email"), sameAs: state.socials.map((url) => url.trim()).filter(Boolean) };
        if (state.type === "localBusiness") { const address = { "@type": "PostalAddress", addressCountry: value("country"), addressRegion: value("region"), addressLocality: value("city"), streetAddress: value("streetAddress"), postalCode: value("postalCode") }; const geo = value("latitude") && value("longitude") ? { "@type": "GeoCoordinates", latitude: Number(value("latitude")), longitude: Number(value("longitude")) } : undefined; const openingHoursSpecification = value("openingDays") && value("opens") && value("closes") ? { "@type": "OpeningHoursSpecification", dayOfWeek: value("openingDays").split(",").map((day) => day.trim()).filter(Boolean), opens: value("opens"), closes: value("closes") } : undefined; object = { "@context": "https://schema.org", "@type": value("businessType") || "LocalBusiness", name: value("name"), url: value("url"), image: value("image"), telephone: value("telephone"), priceRange: value("priceRange"), address, geo, openingHoursSpecification }; }
        if (state.type === "article") { const author = { "@type": value("authorType") || "Person", name: value("authorName"), url: value("authorUrl") }; const publisher = { "@type": "Organization", name: value("publisherName"), logo: value("publisherLogo") ? { "@type": "ImageObject", url: value("publisherLogo") } : undefined }; object = { "@context": "https://schema.org", "@type": value("articleType") || "Article", headline: value("headline"), mainEntityOfPage: { "@type": "WebPage", "@id": value("url") }, url: value("url"), description: value("description"), image: value("image"), author, datePublished: value("datePublished"), dateModified: value("dateModified"), publisher }; }
        if (state.type === "product") object = { "@context": "https://schema.org", "@type": "Product", name: value("name"), url: value("url"), description: value("description"), image: value("image"), brand: value("brand") ? { "@type": "Brand", name: value("brand") } : undefined, sku: value("sku"), mpn: value("mpn"), gtin: value("gtin"), offers: { "@type": "Offer", price: Number(value("price")), priceCurrency: value("priceCurrency").toUpperCase(), availability: `https://schema.org/${value("availability")}`, itemCondition: `https://schema.org/${value("itemCondition")}`, priceValidUntil: value("priceValidUntil") } };
        if (state.type === "breadcrumb") object = { "@context": "https://schema.org", "@type": "BreadcrumbList", itemListElement: state.crumbs.map((crumb, index) => ({ "@type": "ListItem", position: index + 1, name: crumb.name.trim(), item: crumb.url.trim() })) };
        return removeEmpty(object);
    };
    const updateOutput = () => { const { errors, warnings } = validate(); const showIssues = state.interacted; setFieldErrors(showIssues ? errors : {}); clear(errorsRoot); clear(warningsRoot); if (showIssues) { Object.values(errors).forEach((message) => errorsRoot.append(create("p", "schema-message-error", message))); warnings.forEach((message) => warningsRoot.append(create("p", "schema-message-warning", message))); } if (Object.keys(errors).length) { state.output = null; outputStatus.textContent = showIssues ? "نیازمند اصلاح" : "در انتظار اطلاعات"; outputStatus.dataset.state = showIssues ? "error" : ""; codeRoot.textContent = "// برای تولید JSON-LD، اطلاعات ضروری را وارد کنید."; return; } try { state.output = buildOutput(); const json = JSON.stringify(state.output, null, 2); JSON.parse(json); codeRoot.textContent = json; outputStatus.textContent = warnings.length ? "آماده با هشدار" : "JSON معتبر"; outputStatus.dataset.state = warnings.length ? "warning" : "valid"; } catch { state.output = null; outputStatus.textContent = "خطای خروجی"; outputStatus.dataset.state = "error"; codeRoot.textContent = "// تولید JSON ممکن نشد."; } };
    const setType = (type) => { state.type = type; state.values = {}; state.socials = [""]; state.crumbs = [{ name: "", url: "" }, { name: "", url: "" }]; state.interacted = false; typeButtons.forEach((button) => button.setAttribute("aria-selected", String(button.dataset.schemaType === type))); renderForm(); updateOutput(); setFeedback(""); };
    const fallbackCopy = (text) => { const textarea = document.createElement("textarea"); textarea.value = text; textarea.setAttribute("readonly", ""); textarea.style.cssText = "position:fixed;opacity:0"; document.body.append(textarea); textarea.select(); const ok = document.execCommand("copy"); textarea.remove(); return ok; };
    const copy = async (mode) => { if (!state.output) { setFeedback("ابتدا خطاهای فرم را برطرف کنید تا کد ساخته شود.", true); return; } const json = JSON.stringify(state.output, null, 2); const text = mode === "html" ? `<script type="application/ld+json">\n${json}\n</script>` : json; try { if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(text); else if (!fallbackCopy(text)) throw new Error("copy"); setFeedback(mode === "html" ? "کد HTML با موفقیت کپی شد." : "JSON با موفقیت کپی شد."); } catch { setFeedback("کپی خودکار ممکن نشد. دسترسی Clipboard مرورگر را بررسی کنید.", true); } };
    const download = () => { if (!state.output) { setFeedback("ابتدا خطاهای فرم را برطرف کنید تا فایل ساخته شود.", true); return; } const blob = new Blob([JSON.stringify(state.output, null, 2)], { type: "application/ld+json" }); const url = URL.createObjectURL(blob); const link = document.createElement("a"); link.href = url; link.download = `${state.type.replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`)}-schema.json`; document.body.append(link); link.click(); link.remove(); URL.revokeObjectURL(url); setFeedback("فایل JSON آماده دانلود شد."); };
    typeButtons.forEach((button, index) => { button.addEventListener("click", () => setType(button.dataset.schemaType)); button.addEventListener("keydown", (event) => { const keys = ["ArrowLeft", "ArrowRight", "Home", "End"]; if (!keys.includes(event.key)) return; event.preventDefault(); const nextIndex = event.key === "Home" ? 0 : event.key === "End" ? typeButtons.length - 1 : (index + (event.key === "ArrowRight" ? 1 : -1) + typeButtons.length) % typeButtons.length; typeButtons[nextIndex].focus(); setType(typeButtons[nextIndex].dataset.schemaType); }); });
    tool.querySelectorAll("[data-schema-copy]").forEach((button) => button.addEventListener("click", () => copy(button.dataset.schemaCopy)));
    tool.querySelector("[data-schema-download]").addEventListener("click", download);
    tool.querySelector("[data-schema-reset]").addEventListener("click", () => { state.values = {}; state.socials = [""]; state.crumbs = [{ name: "", url: "" }, { name: "", url: "" }]; state.interacted = false; renderForm(); updateOutput(); setFeedback("فرم به حالت اولیه بازگشت."); });
    form.addEventListener("submit", (event) => event.preventDefault());
    renderForm(); updateOutput();
})();
