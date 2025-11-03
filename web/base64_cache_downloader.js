import { app } from "../../../scripts/app.js";

function downloadBase64(b64, filename, format) {
    let file_ext = format.split("/").pop();
    let blob = null;
    if (format == "text/plain") {
        file_ext = "txt";
        blob = new Blob([b64], { type: format });
    }
    else {
        const byteCharacters = atob(b64);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);

        blob = new Blob([byteArray], { type: format });
    }

    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename + "." + file_ext;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
}

app.registerExtension({
    name: "EasyToolkit.Misc.Base64CacheDownloader",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "Base64CacheDownloader") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            if (onNodeCreated) onNodeCreated.apply(this, arguments);

            let uuid_widget = this.widgets?.find(w => w.name === "uuid");
            if (uuid_widget && (!uuid_widget.value || uuid_widget.value === "")) {
                uuid_widget.value = crypto.randomUUID();
            }

            uuid_widget.hidden = true;

            this.addWidget("button", "下载数据", null, async () => {
                uuid_widget = this.widgets?.find(w => w.name === "uuid");
                let filename_widget = this.widgets?.find(w => w.name === "filename");
                let format_widget = this.widgets?.find(w => w.name === "format");
                if (!uuid_widget || !filename_widget || !format_widget) {
                    alert("Cannot find uuid or filename or format widget.");
                    return;
                }

                const response = await fetch("/base64_cache_downloader/download", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        "uuid": uuid_widget.value,
                        "filename": filename_widget.computedDisabled ? null : filename_widget.value, 
                        "format": format_widget.computedDisabled ? null : format_widget.value
                    }),
                });
                const data = await response.json();
                if (data.success) {
                    try {
                        downloadBase64(data.base64_image, data.filename, data.format);
                    }
                    catch (e) {
                        alert(e);
                    }
                }
                else {
                    alert(data.error);
                }
            });

            this.addWidget("button", "删除缓存", null, async () => {
                const response = await fetch("/base64_cache_downloader/clear", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ "uuid": uuid_widget.value }),
                });
                const data = await response.json();
                if (!data.success) {
                    alert(data.error);
                }
            });

            this.addWidget("button", "重新生成UUID", null, async () => {
                uuid_widget.value = crypto.randomUUID();
            });

            // 自定义绘制
            const onDrawForeground = this.onDrawForeground;
            this.onDrawForeground = function (ctx) {
                if (onDrawForeground) onDrawForeground.apply(this, arguments);

                const w = this.widgets?.find(w => w.name === "uuid");
                if (w) {
                    ctx.save();
                    ctx.fillStyle = "orange";
                    ctx.font = "10px Arial";

                    const text = `UUID: ${w.value}`;
                    const textWidth = ctx.measureText(text).width;

                    // 如果有w.width，用它；否则用默认宽度
                    const nodeWidth = this.width || 100; // 这里100是示例宽度
                    const x = (w.x || 0) + (nodeWidth - textWidth) / 2;
                    const y = (w.y || 0) + 14;

                    ctx.fillText(text, x, y);
                    ctx.restore();
                }
            };
        };
    },
});
