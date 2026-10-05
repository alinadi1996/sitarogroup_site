(() => {
    "use strict";

    const labels = [
        ["bold", "درشت", "B"],
        ["italic", "کج", "I"],
        ["formatBlock:h2", "عنوان", "H2"],
        ["formatBlock:h3", "زیرعنوان", "H3"],
        ["insertUnorderedList", "فهرست", "☷"],
        ["insertOrderedList", "فهرست شماره‌دار", "1."],
        ["formatBlock:blockquote", "نقل‌قول", "❞"],
        ["createLink", "افزودن پیوند", "پیوند"],
        ["unlink", "حذف پیوند", "↶"],
    ];

    function initialize(source) {
        if (source.dataset.editorReady) return;
        source.dataset.editorReady = "true";

        const shell = document.createElement("div");
        shell.className = "sitaro-editor";
        const toolbar = document.createElement("div");
        toolbar.className = "sitaro-editor-toolbar";
        toolbar.setAttribute("role", "toolbar");
        toolbar.setAttribute("aria-label", "ابزارهای ویرایش نوشته");
        const editor = document.createElement("div");
        editor.className = "sitaro-editor-canvas";
        editor.contentEditable = "true";
        editor.dir = "rtl";
        editor.setAttribute("role", "textbox");
        editor.setAttribute("aria-multiline", "true");
        editor.setAttribute("aria-label", "متن نوشته");
        editor.innerHTML = source.value;

        const sync = () => { source.value = editor.innerHTML; };
        editor.addEventListener("input", sync);
        editor.addEventListener("blur", sync);
        editor.addEventListener("paste", (event) => {
            event.preventDefault();
            document.execCommand("insertText", false, event.clipboardData.getData("text/plain"));
            sync();
        });

        labels.forEach(([command, title, text]) => {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "sitaro-editor-tool";
            button.textContent = text;
            button.title = title;
            button.setAttribute("aria-label", title);
            button.addEventListener("mousedown", (event) => event.preventDefault());
            button.addEventListener("click", () => {
                editor.focus();
                if (command === "createLink") {
                    const url = window.prompt("آدرس پیوند (https:// یا mailto:)");
                    if (!url || !/^(https?:\/\/|mailto:)/i.test(url.trim())) return;
                    document.execCommand("createLink", false, url.trim());
                } else {
                    const [action, value] = command.split(":");
                    document.execCommand(action, false, value || null);
                }
                sync();
            });
            toolbar.append(button);
        });

        const sourceToggle = document.createElement("button");
        sourceToggle.type = "button";
        sourceToggle.className = "sitaro-editor-source-toggle";
        sourceToggle.textContent = "HTML";
        sourceToggle.setAttribute("aria-label", "نمایش کد HTML");
        sourceToggle.setAttribute("aria-pressed", "false");
        sourceToggle.addEventListener("click", () => {
            const showSource = sourceToggle.getAttribute("aria-pressed") !== "true";
            if (showSource) sync();
            else editor.innerHTML = source.value;
            sourceToggle.setAttribute("aria-pressed", String(showSource));
            source.hidden = !showSource;
            editor.hidden = showSource;
            toolbar.querySelectorAll(".sitaro-editor-tool").forEach((button) => { button.disabled = showSource; });
            (showSource ? source : editor).focus();
        });
        toolbar.append(sourceToggle);

        const hint = document.createElement("p");
        hint.className = "sitaro-editor-hint";
        hint.textContent = "متن را انتخاب کنید و قالب دلخواه را اعمال کنید. برای مشاهده کد HTML، دکمه HTML را بزنید.";

        source.before(shell);
        shell.append(toolbar, editor, source, hint);
        source.readOnly = true;
        source.hidden = true;
        source.form?.addEventListener("submit", () => {
            if (!source.hidden) return;
            sync();
        });
    }

    function start() {
        document.querySelectorAll("textarea.sitaro-rich-text-source").forEach(initialize);
    }

    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
    else start();
})();
