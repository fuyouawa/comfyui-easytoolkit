import { app } from "../../../scripts/app.js";

function downloadBase64(b64, filename, file_format) {
    const byteCharacters = atob(b64);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);

    let blob_type = '';
    if (file_format === 'png') {
        blob_type = 'image/png';
    }
    else if (file_format === 'jpeg') {
        blob_type = 'image/jpeg';
    }
    else if (file_format === 'mp4') {
        blob_type = 'video/mp4';
    }
    else if (file_format === 'webm') {
        blob_type = 'video/webm';
    }
    else {
        alert('不支持的格式：' + file_format);
        return;
    }
    const blob = new Blob([byteArray], { type: blob_type });

    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename + "." + file_format;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
}

app.registerExtension({
    name: "EasyToolkit.Misc.Base64Downloader",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "Base64Downloader") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            if (onNodeCreated) onNodeCreated.apply(this, arguments);

            let uuid_widget = this.widgets?.find(w => w.name === "uuid");
            if (uuid_widget && (!uuid_widget.value || uuid_widget.value === "")) {
                uuid_widget.value = crypto.randomUUID();
            }

            uuid_widget.hidden = true;

            this.addWidget("button", "下载上次数据", null, async () => {
                const response = await fetch("/base64_downloader/download", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ "uuid": uuid_widget.value }),
                });
                const data = await response.json();
                if (data.success) {
                    downloadBase64(data.base64_image, data.filename, data.file_format);
                }
                else {
                    alert(data.error);
                }
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
