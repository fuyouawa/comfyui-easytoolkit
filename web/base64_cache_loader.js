import { app } from "../../../scripts/app.js";

app.registerExtension({
    name: "EasyToolkit.Misc.Base64CacheLoader",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "Base64CacheLoader") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            if (onNodeCreated) onNodeCreated.apply(this, arguments);

            let uuid_widget = this.widgets?.find(w => w.name === "uuid");
            if (uuid_widget && (!uuid_widget.value || uuid_widget.value === "")) {
                uuid_widget.value = crypto.randomUUID();
            }

            uuid_widget.disabled = true;

            this.addWidget("button", "选择文件上传", null, async () => {
                const input = document.createElement("input");
                input.type = "file";
                input.accept = "*/*";
                input.style.display = "none";

                input.onchange = async (event) => {
                    const file = event.target.files[0];
                    if (!file) return;

                    uuid_widget = this.widgets?.find(w => w.name === "uuid");
                    let filename_widget = this.widgets?.find(w => w.name === "filename");
                    if (!uuid_widget || !filename_widget) {
                        alert("Cannot find uuid or file widget.");
                        return;
                    }
                    filename_widget.value = file.name;

                    const reader = new FileReader();
                    reader.onload = async () => {
                        // Split the data URL into format and base64 data
                        const dataUrl = reader.result;
                        const matches = dataUrl.match(/^data:(.+\/.+);base64,(.+)$/);
                        const fileFormat = matches ? matches[1] : "application/octet-stream";
                        const base64Data = matches ? matches[2] : dataUrl.replace(/^data:.*?;base64,/, "");

                        const response = await fetch("/base64_cache_loader/update", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({
                                "uuid": uuid_widget.value,
                                "filename": file.name,
                                "format": fileFormat,
                                "base64": base64Data,
                            }),
                        });
                        const result = await response.json();
                        if (!result.success) {
                            alert(result.error);
                            return;
                        }
                    };
                    reader.readAsDataURL(file);
                };

                this.addWidget("button", "重新生成UUID", null, async () => {
                    uuid_widget = this.widgets?.find(w => w.name === "uuid");
                    uuid_widget.value = crypto.randomUUID();
                });

                input.click(); // 打开文件选择对话框
            });
        };
    },
});
