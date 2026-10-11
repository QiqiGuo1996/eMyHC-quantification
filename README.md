# muscle_image

中文 | [English](#english)

骨骼肌切片图像分析工具。目前包含 **FiberQuant v1.10.0**，一个在浏览器里运行的肌纤维损伤与再生定量工具。

## FiberQuant 能做什么

- 根据 WGA 染色分割肌纤维
- 根据 DAPI 识别中央核纤维（CNF），以此界定损伤区
- 测量阳性标记（如 eMyHC）在损伤区内所占的面积比例
- 支持手动校正纤维分类、手绘补充遗漏的纤维和损伤区
- 结果导出为 CSV（参数和所有手动校正都会记录在内）和 PNG 叠加图

整个工具就是一个 HTML 文件，无需安装，图像只在本机处理，不会上传。

## 快速开始

1. 下载 [`eMyHC_Quanti_v1.10.html`](eMyHC_Quanti_v1.10.html)，用 Chrome、Edge、Firefox 或 Safari 打开。
2. 点"用示例图试一试"熟悉流程，或载入自己的图像（PNG、JPG 或 TIFF）。
3. 指定 WGA、DAPI 和标记通道，填写原图像素尺寸（µm/像素）。
4. 点"运行分析"，检查结果，必要时手动校正，然后导出 CSV。

首次读取 TIFF 需要联网（TIFF 解码组件从 CDN 加载），PNG 和 JPG 可完全离线使用。

## 仓库结构

| 路径 | 说明 |
| --- | --- |
| [`eMyHC_Quanti_v1.10.html`](eMyHC_Quanti_v1.10.html) | 工具本体，可直接打开使用 |
| [`fiber-quant-v1.10.0/fiber-quant-v1.10.0/`](fiber-quant-v1.10.0/fiber-quant-v1.10.0/) | 完整发布包：同一个工具（`fiber-quant.html`）及其文档 |

两个 HTML 文件内容完全相同。分析流程、参数说明、输出格式和局限性的完整说明见发布包内的文档：

- [README.zh-CN.md](fiber-quant-v1.10.0/fiber-quant-v1.10.0/README.zh-CN.md)（中文）
- [README.md](fiber-quant-v1.10.0/fiber-quant-v1.10.0/README.md)（English）
- [CHANGELOG.md](fiber-quant-v1.10.0/fiber-quant-v1.10.0/CHANGELOG.md)（版本记录）

## 引用与许可

引用信息见 [CITATION.cff](fiber-quant-v1.10.0/fiber-quant-v1.10.0/CITATION.cff)。本工具以 [MIT 许可证](fiber-quant-v1.10.0/fiber-quant-v1.10.0/LICENSE) 发布，所用第三方库见 [THIRD_PARTY_NOTICES.md](fiber-quant-v1.10.0/fiber-quant-v1.10.0/THIRD_PARTY_NOTICES.md)。

---

## English

Image analysis tools for skeletal muscle sections. The repository currently contains **FiberQuant v1.10.0**, a browser-based tool for quantifying muscle injury and regeneration.

FiberQuant segments muscle fibers from WGA staining, identifies centrally nucleated fibers (CNFs) to define the injured region, and measures the area fraction of a marker (e.g. eMyHC) within that region. It is a single self-contained HTML file: no installation is needed, and images are processed locally without being uploaded.

**Quick start:** download [`eMyHC_Quanti_v1.10.html`](eMyHC_Quanti_v1.10.html), open it in a current browser, load an image, assign the channels, enter the pixel size, and click **Run analysis**.

The release package in [`fiber-quant-v1.10.0/fiber-quant-v1.10.0/`](fiber-quant-v1.10.0/fiber-quant-v1.10.0/) contains the same tool (`fiber-quant.html`) with full documentation. See its [README](fiber-quant-v1.10.0/fiber-quant-v1.10.0/README.md) for the analysis workflow, parameters, output and limitations.

Released under the [MIT License](fiber-quant-v1.10.0/fiber-quant-v1.10.0/LICENSE).
