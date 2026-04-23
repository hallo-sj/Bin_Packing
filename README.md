[capture_20260423104222810.bmp](https://github.com/user-attachments/files/26994616/capture_20260423104222810.bmp)# Bin_Packing
# 3D Bin Packing Problem - Heuristic Algorithm Optimization

## 项目简介
本项目针对三维装箱问题（3D-BPP），设计并实现了一种基于地面层+多层堆叠的启发式算法。
在地面层采用动态规划优选组合物品，最大化底面积利用率。
在上层采用锚点支撑判断，保证堆叠稳定性（支撑面积 > 80%）。
支持物品六种旋转姿态的自适应选择。

## 核心文件说明
`main.py`：算法主入口，支持从 Excel/CSV 导入数据，输出可视化结果与 CSV 报表。<br>
`packing_visualization_2.py`：基于 Matplotlib 的 3D 可视化模块。<br>
`LP112Goods.xlsx`：测试用例数据集。<br>

## 运行环境
Python 3.8+
Pandas, Matplotlib, openpyxl (用于读取 .xlsx)

## 运行结果示例
![可视化结果](images/capture_20260423104222810.bmp)   

## 优化效果
相比经典 First Fit Decreasing 算法，在 LP113 测试集上对40寸集装箱进行装箱空间利用率提升至63.17%(装载率100%)。
