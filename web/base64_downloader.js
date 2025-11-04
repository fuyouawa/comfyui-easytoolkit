import { app } from "../../../scripts/app.js";

function downloadBase64(b64, basename, format) {
    let suffix = format.split("/").pop();
    let blob = null;
    if (format == "text/plain") {
        suffix = "txt";
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
    link.download = basename + "." + suffix;
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

            uuid_widget.disabled = true;

            this.addWidget("button", "下载数据", null, async () => {
                uuid_widget = this.widgets?.find(w => w.name === "uuid");
                let basename_widget = this.widgets?.find(w => w.name === "basename");
                let format_widget = this.widgets?.find(w => w.name === "format");
                if (!uuid_widget || !basename_widget || !format_widget) {
                    alert("Cannot find uuid or basename or format widget.");
                    return;
                }

                const response = await fetch("/base64_cache_downloader/download", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        "uuid": uuid_widget.value,
                        "basename": basename_widget.computedDisabled ? null : basename_widget.value, 
                        "format": format_widget.computedDisabled ? null : format_widget.value
                    }),
                });
                const data = await response.json();
                if (data.success) {
                    try {
                        downloadBase64(data.base64_image, data.basename, data.format);
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
                uuid_widget = this.widgets?.find(w => w.name === "uuid");
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
                uuid_widget = this.widgets?.find(w => w.name === "uuid");
                uuid_widget.value = crypto.randomUUID();
            });
        };
    },
});
