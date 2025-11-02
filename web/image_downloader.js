import { app } from "../../../scripts/app.js";

function downloadBase64Image(b64, filename) {
    const byteCharacters = atob(b64);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: 'image/png' });

    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename + ".png";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
}

app.registerExtension({
    name: "EasyToolkit.Image.ImageDownloader",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "ImageDownloader") return;

        // 注册节点创建时的 UI
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            if (onNodeCreated) onNodeCreated.apply(this, arguments);

            // 添加一个按钮
            this.addWidget("button", "下载上次图片", null, async () => {
                const response = await fetch("/image_downloader/download", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({})
                });
                const data = await response.json();
                if (data.success) {
                    const b64 = data.base64_image;
                    downloadBase64Image(b64, data.filename);
                }
                else {
                    alert(data.error);
                }
            });
        };
    },
});
