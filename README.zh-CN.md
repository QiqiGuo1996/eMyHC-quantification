# eMyHC_Quanti：肌肉损伤与再生定量工具

[English](README.md) | 中文

eMyHC_Quanti 在 WGA 染色的肌肉横切片上分割肌纤维，以中央核纤维（CNF）界定损伤区，测量再生标记（胚胎型肌球蛋白重链 eMyHC 或其他红色标记）在损伤区内所占的面积比例，并给出纤维横截面积（CSA）。

分析在浏览器中由一个 HTML 文件完成，图像只在本机处理，不会上传。也可选择在自己电脑的显卡上用 [Cellpose](https://github.com/MouseLand/cellpose) 分割纤维。

本仓库对应论文：[作者]. [题目]. *[期刊]* ([年份]). https://doi.org/[论文DOI]

## 文件说明

| 文件 | 说明 |
| --- | --- |
| `eMyHC_Quanti.html` | 分析工具（用浏览器打开） |
| `cellpose_server.py` | 可选：在本机运行 Cellpose，并打开带"用Cellpose分割"按钮的工具 |
| `cellpose_batch.py` | 可选：用 Cellpose 批量分割整个文件夹，生成可导入的标签图 |
| `CHANGELOG.md`、`CITATION.cff`、`LICENSE`、`THIRD_PARTY_NOTICES.md` | 版本记录、引用信息、许可证、第三方组件许可 |

## 快速开始

1. 用 Chrome、Edge、Firefox 或 Safari（2023 年及以后的版本）打开 `eMyHC_Quanti.html`。
2. 载入图像，或点"用示例图试一试"。
3. 核对通道（WGA、DAPI、标记）和像素尺寸。Keyence BZ-X 的 TIFF 会自动读取像素尺寸。
4. 点"运行分析"，检查叠加图，必要时校正，导出 CSV。

首次打开 TIFF 需要联网，因为 TIFF 解码组件从公共 CDN 加载。

## 输入

- WGA（纤维轮廓）、DAPI（细胞核）和标记（如 eMyHC）染色的横切冰冻切片。
- RGB 合成图（PNG、JPG、TIFF），或每页一个通道的多通道 TIFF（8 位、16 位或 32 位浮点）。
- 浏览器无法读取 BigTIFF，请先在 Fiji 中缩小另存。

### 像素尺寸与 Keyence 拼接图

所有面积都取决于像素尺寸。Keyence BZ-X 软件保存拼接图时，如果拼接图超过约 1250 万像素，会按拼接视野数不同程度地缩小图像，因此即使拍摄设置相同，不同图像的像素尺寸也可能不同（20× 物镜、2×2 binning 时未缩小为 0.7549 µm/像素，缩小后更大）。本工具会从每个文件的 Keyence 元数据中读取真实像素尺寸；经其他软件另存的文件通常丢失这些信息，需手动填写。

如需一批图在相同分辨率下分析，可将"处理时缩小倍数"设为"统一分辨率"：每张图按自己的像素尺寸缩放到统一处理分辨率。

## 分析流程

**1. 纤维分割（内置）。** WGA 通道扣除背景并平滑后，以"被亮环包围的暗区"作为每根纤维的中心（WGA 强度的 h-minima），再在 WGA 强度图上做标记分水岭，从中心扩展出每根纤维。随后每根纤维只保留自己的内部和靠近自己一侧的一半 WGA 膜，使边界落在膜中线上，膜外的间隙不计入。以 0.7 倍 Otsu 阈值得到的膜掩膜用于计算膜内侧面积和到膜的距离。最后按膜内侧面积、内切半径、凸度（面积 ÷ 凸包面积）和形状指数（面积 ÷ 最大内切圆面积）剔除间隙和间质。

**1′. 用 Cellpose 分割（可选）。** 可用 Cellpose 的标签图代替内置分割：通过 `cellpose_server.py` 在网页中一键分割，或导入 `cellpose_batch.py` 生成的 `*_cp_masks.tif`。每个 Cellpose 对象同样只保留其内部和靠近自身一侧的一半膜，接触图像边缘或面积不在范围内的对象被排除。

**2. 中央核。** 细胞核通道扣除背景、平滑后按 Otsu 阈值分割。距膜超过"中心区内缩距离"的部分为纤维中心区（小纤维以内切半径的 40% 为上限）。中心区内细胞核面积达到下限的纤维判为中央核纤维。

**3. 标记阳性纤维。** 标记通道扣除背景、平滑后按阈值分割。标记覆盖面积达到设定比例的纤维判为阳性（可选择把纤维轮廓向外扩一段距离后计算）。

**4. 损伤区。** 默认为所有中央核纤维的并集。可选择加入没有中央核的标记阳性纤维，以及无纤维损伤区（手动圈画、自动识别的 DAPI 密集区，或选中的未识别区域）。

**5. 主要结果。**

```
标记阳性比例 (%) = 损伤区内标记阳性面积 ÷ 损伤区面积 × 100
```

默认设置下，分子和分母都只包括中央核纤维：非中央核纤维和间质中的标记信号不计入。标记阳性面积可按阳性像素计算（默认），或按阳性纤维的整根面积计算。

**6. 纤维面积。** 每根纤维的 CSA（至膜中线），以及全部纤维、损伤纤维、非损伤纤维和标记阳性损伤纤维的均值 ± SD 与中位数。

## 参数

下表为默认值；同一实验的所有图像请使用相同参数。所有参数、实际阈值和分割来源都会写入导出的 CSV。

| 类别 | 参数 | 默认值 | 说明 |
| --- | --- | --- | --- |
| 比例尺 | 像素尺寸 | 读取 Keyence 元数据 | 文件中没有时需手动填写 |
| 比例尺 | 处理时缩小倍数 | 自动 | "统一分辨率"将所有图缩放到同一分辨率 |
| 纤维分割 | WGA 阈值 | 自动（0.7 × Otsu） | |
| 纤维分割 | 纤维面积范围 | 100–15,000 µm² | 下限按膜内侧面积计算；纤维很小时调低 |
| 纤维分割 | 排除接触图像边缘的纤维 | 开 | |
| 纤维与间质分离 | 最小凸度 | 0.9 | |
| 纤维与间质分离 | 最大形状指数 | 4 | |
| 纤维与间质分离 | 纤维内最大细胞核占比 | 0（关闭） | |
| 中央核判定 | 细胞核阈值 | 自动（Otsu） | |
| 中央核判定 | 中心区内缩距离 | 4 µm | |
| 中央核判定 | 中心区最小核面积 | 6 µm² | |
| 阳性标记 | 标记阈值 | 自动（Otsu） | 建议设为固定值，见"局限性" |
| 阳性标记 | 判为阳性纤维的面积占比 | 20% | |
| 阳性标记 | 阳性面积计算方式 | 按像素 | 可改为阳性纤维整根 |
| 阳性标记 | 阳性判定外扩距离 | 0 µm | |
| 阳性标记 | 阳性纤维计入损伤区 | 关 | |
| 无纤维损伤区 | 自动识别 DAPI 密集区 | 关 | |

## 手动校正

单击纤维查看数据。快捷键：**C** 切换中央核，**R** 切换标记阳性，**X** 排除或恢复。"圈画纤维""圈画红色阳性""框选损伤区"可补充自动分析遗漏的内容。单击灰色的未识别区域可查看剔除原因，并设为"损伤区""非损伤区""按类别"，或转为纤维（快捷键 I、N、F）。所有校正都记录在 CSV 中。

## Cellpose（可选）

需要 Python；有 NVIDIA 显卡时速度快得多。

```
conda create -n cellpose python=3.10 -y
conda activate cellpose
pip install "cellpose[gui]" tifffile imagecodecs
python -c "import torch; print(torch.cuda.is_available())"     # 应显示 True
```

**一键方式：** 将 `cellpose_server.py` 与 `eMyHC_Quanti.html` 放在同一文件夹，运行 `python cellpose_server.py`。工具会在 http://127.0.0.1:8765 打开（支持 Windows、macOS、Linux 桌面和 WSL）；载入图像后点"用Cellpose分割（本机GPU）"。微调过的模型用 `--model <路径>` 指定；Cellpose 3 的模型可用 `--diam_um` 设置纤维直径。

**批量方式：** `python cellpose_batch.py <文件夹>` 会为每个 `*_Merge.tif` 生成 `<图像名>_cp_masks.tif`；在工具中载入原图后"导入Cellpose分割"。

## 输出

界面汇总显示损伤区标记阳性比例、纤维数与中央核纤维数、损伤区面积、标记阳性面积与纤维数，以及纤维面积统计。CSV 包含汇总、纤维面积统计、全部参数（含工具版本、分析时间、图像名和分割来源）以及每根纤维一行的数据。叠加图可导出为 PNG。

## 验证

建议在随机抽取的切片上与人工定量比较（例如两名不知分组的评估者计数中央核纤维和标记阳性纤维并勾画纤维），以组内相关系数和 Bland–Altman 图报告一致性。本研究的验证结果见论文 [补充图 x]。

## 局限性

- 标记阈值对阳性比例影响很大。请为整个实验设定固定阈值，以只加二抗的对照基本为阴性为准。
- 分割依赖 WGA 膜染色。请检查叠加图中粘连、切开或遗漏的纤维，手动校正或改用 Cellpose。
- 默认设置下，切片恰好未切到中央核的标记阳性纤维不计入损伤区，因此阳性比例偏保守。
- 浏览器中每次分析一张图；大量图像可先用 `cellpose_batch.py` 准备分割结果。

## 引用

请同时引用上述论文和存档的软件版本：

> [作者]. eMyHC_Quanti: quantification of muscle injury and regeneration (v2.3.0). *Zenodo* https://doi.org/[DOI] ([年份]).

使用 Cellpose 分割时也请引用 Cellpose。引用信息见 `CITATION.cff`。

## AI 工具使用说明

源代码在大语言模型（Claude，Anthropic）辅助下生成。作者确定了分析流程，审核了代码，并以人工定量验证了输出结果，对代码承担全部责任。

## 许可证

MIT 许可证（见 `LICENSE`）。第三方组件见 `THIRD_PARTY_NOTICES.md`。

## 联系方式

[姓名]，[单位]，[邮箱]。问题请通过 GitHub issue 反馈。

## 参考文献

1. Otsu, N. A threshold selection method from gray-level histograms. *IEEE Trans. Syst. Man Cybern.* **9**, 62–66 (1979).
2. Borgefors, G. Distance transformations in digital images. *Comput. Vis. Graph. Image Process.* **34**, 344–371 (1986).
3. Vincent, L. & Soille, P. Watersheds in digital spaces: an efficient algorithm based on immersion simulations. *IEEE Trans. Pattern Anal. Mach. Intell.* **13**, 583–598 (1991).
4. Stringer, C., Wang, T., Michaelos, M. & Pachitariu, M. Cellpose: a generalist algorithm for cellular segmentation. *Nat. Methods* **18**, 100–106 (2021).
