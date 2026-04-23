import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import art3d
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.animation as animation
import matplotlib.colors as mcolors

def create_cube(ax, origin, size, color, alpha=0.8, label=None):
    """创建一个立方体并添加到3D坐标轴"""
    x, y, z = origin
    l, w, h = size
    
    # 定义立方体的8个顶点
    vertices = np.array([
        [x, y, z],
        [x+l, y, z],
        [x+l, y+w, z],
        [x, y+w, z],
        [x, y, z+h],
        [x+l, y, z+h],
        [x+l, y+w, z+h],
        [x, y+w, z+h]
    ])
    
    # 定义立方体的6个面
    faces = [
        [vertices[0], vertices[1], vertices[5], vertices[4]],  # 底面
        [vertices[2], vertices[3], vertices[7], vertices[6]],  # 顶面
        [vertices[0], vertices[4], vertices[7], vertices[3]],  # 前面
        [vertices[1], vertices[5], vertices[6], vertices[2]],  # 后面
        [vertices[0], vertices[3], vertices[2], vertices[1]],  # 左面
        [vertices[4], vertices[5], vertices[6], vertices[7]]   # 右面
    ]
    
    # 创建面集合并添加到坐标轴
    cube = Poly3DCollection(faces, alpha=alpha, linewidths=1, edgecolors='k')
    cube.set_facecolor(color)
    ax.add_collection3d(cube)
    
    # 添加标签
    if label:
        ax.text(x + l/2, y + w/2, z + h/2, label, 
                color='white', ha='center', va='center', fontsize=8, fontweight='bold')

def visualize_3d_packing(bin_size, packed_items, title="3D Bin Packing Solution"):
    """可视化3D装箱结果"""
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # 设置坐标轴标签
    ax.set_xlabel('Length (X)')
    ax.set_ylabel('Width (Y)')
    ax.set_zlabel('Height (Z)')
    
    # 设置坐标轴范围
    ax.set_xlim(0, bin_size[0])
    ax.set_ylim(0, bin_size[0])
    ax.set_zlim(0, bin_size[0])
    
    # 绘制箱子框架
    # 底部
    rect = Rectangle((0, 0), bin_size[1], bin_size[0], fill=False, edgecolor='red', linestyle='--', alpha=0.5)
    ax.add_patch(rect)
    art3d.pathpatch_2d_to_3d(rect, z=0, zdir="z")

    # # 绘制箱子框架 ==2==
    # # 底部
    # rect = Rectangle((0, 0+ bin_size[1] *2), bin_size[0], bin_size[1], fill=False, edgecolor='blue', linestyle='--', alpha=0.5)
    # ax.add_patch(rect)
    # art3d.pathpatch_2d_to_3d(rect, z=0, zdir="z")
    
    # # 顶部
    # rect_top = Rectangle((0, 0 + bin_size[1] *2), bin_size[0], bin_size[1], fill=False, edgecolor='blue', linestyle='--', alpha=0.5)
    # ax.add_patch(rect_top)
    # art3d.pathpatch_2d_to_3d(rect_top, z=bin_size[2], zdir="z")
    
    # 绘制每个物品
    # for item in packed_items:
    #     create_cube(ax, item['position'], item['dimensions'], 
    #                item['color'], label=f"Item {item['id']}")
    for item in packed_items:
        create_cube(ax, item['position'], item['dimensions'], item['color'])
    # 顶部
    rect_top = Rectangle((0, 0), bin_size[1], bin_size[0], fill=False, edgecolor='red', linestyle='--', alpha=0.5)
    ax.add_patch(rect_top)
    art3d.pathpatch_2d_to_3d(rect_top, z=bin_size[2], zdir="z")

    # 添加图例元素
    legend_elements=[]
    # legend_elements = [Patch(facecolor=item['color'], edgecolor='k', 
    #                     label=f"Item {item['id']} ({item['dimensions'][0]}x{item['dimensions'][1]}x{item['dimensions'][2]})")
    #               for item in packed_items]
    
    # 侧面
    for i in range(4):
        x = [0, bin_size[1], bin_size[1], 0, 0]
        y = [0, 0, bin_size[0], bin_size[0], 0]
        z = [0, 0, 0, 0, 0]
        ax.plot(x, y, z, 'red', linestyle='--', alpha=0.5)
        
        z_top = [bin_size[2]] * 5
        ax.plot(x, y, z_top, 'red', linestyle='--', alpha=0.5)

    
    # # 添加标题
    # total_value = sum(item['value'] for item in packed_items)
    # total_weight = sum(item['weight'] for item in packed_items)
    
    # 添加图例
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))
    
    # 设置视角
    ax.view_init(elev=30, azim=-45)
    
    # 添加比例网格
    ax.grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.show()
    
    # return cog

def create_animation(bin_size, position_history, title="Packing Process"):
    """创建整理过程的动画"""
    fig = plt.figure(figsize=(140, 20))
    ax = fig.add_subplot(111, projection='3d')
    
    # 设置坐标轴
    ax.set_xlim(0, bin_size[0])
    ax.set_ylim(0, bin_size[0])
    ax.set_zlim(0, bin_size[0])
    ax.set_xlabel('Length (X)')
    ax.set_ylabel('Width (Y)')
    ax.set_zlabel('Height (Z)')
    
    # 创建箱子框架
    rect = Rectangle((0, 0), bin_size[0], bin_size[1], fill=False, edgecolor='gray', linestyle='--', alpha=0.5)
    ax.add_patch(rect)
    art3d.pathpatch_2d_to_3d(rect, z=0, zdir="z")
    
    rect_top = Rectangle((0, 0), bin_size[0], bin_size[1], fill=False, edgecolor='gray', linestyle='--', alpha=0.5)
    ax.add_patch(rect_top)
    art3d.pathpatch_2d_to_3d(rect_top, z=bin_size[2], zdir="z")
    
    # 创建初始立方体集合
    cubes = []
    colors = plt.cm.tab10(np.linspace(0, 1, len(position_history[0])))
    for i, (pos, dim) in enumerate(position_history[0]):
        cubes.append(create_cube_collection(pos, dim, colors[i]))
        ax.add_collection3d(cubes[-1])
    
    # 添加标题
    plt.title(title, fontsize=14)
    
    # 更新函数
    def update(frame):
        for i, (cube, (pos, dim)) in enumerate(zip(cubes, position_history[frame])):
            x, y, z = pos
            l, w, h = dim
            
            # 更新立方体顶点
            vertices = np.array([
                [x, y, z],
                [x+l, y, z],
                [x+l, y+w, z],
                [x, y+w, z],
                [x, y, z+h],
                [x+l, y, z+h],
                [x+l, y+w, z+h],
                [x, y+w, z+h]
            ])
            
            faces = [
                [vertices[0], vertices[1], vertices[5], vertices[4]],
                [vertices[2], vertices[3], vertices[7], vertices[6]],
                [vertices[0], vertices[4], vertices[7], vertices[3]],
                [vertices[1], vertices[5], vertices[6], vertices[2]],
                [vertices[0], vertices[3], vertices[2], vertices[1]],
                [vertices[4], vertices[5], vertices[6], vertices[7]]
            ]
            
            cube.set_verts(faces)
        
        return cubes
    
    # 创建动画
    ani = animation.FuncAnimation(fig, update, frames=len(position_history), 
                                  interval=500, blit=False)
    
    plt.tight_layout()
    return ani

def create_cube_collection(origin, size, color, alpha=0.8):
    """创建一个立方体集合对象"""
    x, y, z = origin
    l, w, h = size
    
    vertices = np.array([
        [x, y, z],
        [x+l, y, z],
        [x+l, y+w, z],
        [x, y+w, z],
        [x, y, z+h],
        [x+l, y, z+h],
        [x+l, y+w, z+h],
        [x, y+w, z+h]
    ])
    
    faces = [
        [vertices[0], vertices[1], vertices[5], vertices[4]],
        [vertices[2], vertices[3], vertices[7], vertices[6]],
        [vertices[0], vertices[4], vertices[7], vertices[3]],
        [vertices[1], vertices[5], vertices[6], vertices[2]],
        [vertices[0], vertices[3], vertices[2], vertices[1]],
        [vertices[4], vertices[5], vertices[6], vertices[7]]
    ]
    return Poly3DCollection(faces, alpha=alpha, linewidths=1, edgecolors='k', facecolor=color)

def convert_to_packed_items(walls):
    """
    将装箱数据转换为可视化所需的格式
    
    参数:
    bin_size -- 元组 (L, W, H, C) 表示箱子的长、宽、高、承重
    walls -- DataFrame列表，每个DataFrame包含一堵墙的物品信息
    
    返回:
    packed_items -- 转换后的物品字典列表
    """
    packed_items = []
    item_counter = 1  # 物品ID计数器
    color_palette = list(mcolors.TABLEAU_COLORS.values())  # 预定义颜色列表
    
    # 遍历每面墙
    for wall_df in walls:
        # 遍历墙中的每个物品
        for _, row in wall_df.iterrows():
            # 提取物品原始属性
            orig_id = hash(row['id'])
            length = row['长']
            width = row['宽']
            height = row['高']
            z_pos = row['上下']    # z坐标 (垂直方向)
            y_pos = row['前后']    # y坐标 (深度方向)
            x_pos = row['左右']    # x坐标 (水平方向)
            
            # 创建转换后的物品字典
            item = {
                'id': orig_id,  # 递进编号
                'position': (y_pos, x_pos, z_pos),  # (前后, 左右, 上下)
                'dimensions': (width, length, height),  # (宽, 长, 高)
                'color': color_palette[ orig_id % len(color_palette)],
            }
            
            packed_items.append(item)
            item_counter += 1
    
    return packed_items