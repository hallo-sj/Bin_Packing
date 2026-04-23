import pandas as pd
import csv
from packing_visualization_2 import convert_to_packed_items, visualize_3d_packing

class  Item:
    def __init__(self,id,length,width,height):
        self.id=id
        self.length=length  #Y
        self.width=width    #X
        self.height=height  #Z
        self.pos=(0,0,0)
    
    @property
    def area(self):
        '''
        计算物品底面积
        '''
        return self.length*self.width
    
    def get_rotation(self):
        '''
        返回所有姿态可能（共六种）
        且按高度降低，底面积增大排序
        '''
        l,w,h=self.length,self.width,self.height
        possible_rotation=[
            (l,w,h),(l,h,w),
            (w,l,h),(w,h,l),
            (h,l,w),(h,w,l)
        ]
        all_rotation=list(set(possible_rotation))
        #x[0] length,x[1] width,x[2] height
        all_rotation.sort(key=lambda x: (x[2],-(x[0]*x[1])))
        return all_rotation
    
    def set_rotation(self,length,width,height):
        '''
        修改物品的长宽高
        '''
        self.length=length
        self.width=width
        self.height=height

        
        

class Bin:
    def __init__(self,length,width,height):
        self.length=length
        self.width=width
        self.height=height
        self.items=[]   #记录已放置物品

    def add_item(self,item,pos):
        '''
        物品入箱，并记录位置
        '''
        item.pos=pos
        self.items.append(item)

    def is_valid_position(self,item,pos):
        '''
        检查位置是否合法不超边界，不与已放置物品重叠
        '''
        x,y,z=pos
        if(x<0 or y<0 or z<0 or 
           x+item.width>self.width or y+item.length>self.length or z+item.height>self.height):
            return False
        for existing in self.items:
            ex_x, ex_y, ex_z = existing.pos
            if (x < ex_x + existing.width and x + item.width > ex_x and
                y < ex_y + existing.length and y + item.length > ex_y and
                z < ex_z + existing.height and z + item.height > ex_z):
                return False
        return True


def calculate_utilization(bin):
    '''
    计算实际空间利用率
    '''
    total_volume=bin.length*bin.width*bin.height
    used_volume=sum(item.length*item.width*item.height for item in bin.items)
    utilization=(used_volume/total_volume)*100

    print(f"空间利用率:{utilization:.2f}%")

    return utilization


def row_dp(remaining_length,shelf_width,bin_height,items):
    '''
    一排内的物品动态规划
    '''
    capacity=remaining_length
    dp=[0]*(capacity+1) #容量为i ,价值为dp[i]
    item_choice={w:[] for w in range(capacity+1)} #容量为i, 最优组合为item_choice[i]

    for item in items:
        new_dp=list(dp)
        new_choice={w:list(item_choice[w]) for w in range(capacity+1)}
        rotation=item.get_rotation()
        for l,w,h in rotation: 
            if w<=shelf_width and h<bin_height and l<=capacity:
                v=l*w   #底面积作为价值

                #逆序遍历容量，基于上一组dp状态更新new_dp
                for j in range(capacity,l-1,-1):
                    if dp[j-l]+v>new_dp[j]:

                        new_dp[j]=dp[j-l]+v
                        new_choice[j]=item_choice[j-l]+[(item,l,w,h)]

        dp=new_dp
        item_choice=new_choice
    best_j=max(range(capacity+1),key=lambda j:dp[j]) #得到价值最大的容量

    return item_choice[best_j]


"""地面层铺满策略：动态规划按排填充"""
def pack_ground_floor(bin,items):
    '''
    挑选第一个物品放置，底面积最大，若无法放置，则尝试旋转
    '''
    items_remaining=sorted(items, key=lambda x: x.area, reverse=True)
    placed=[]
    shelves=[]  #记录每一排的信息：{'x':起始x, 'y':当前y，长度, 'width':该排宽度}
    max_x=0 #当前已占用的最大x边界

    if items_remaining:
        first_item=None
        for i,item in enumerate(items_remaining):
            if item.height<=bin.height and item.length<=bin.length and item.width<=bin.width:
                first_item=item
                items_remaining.pop(i)
                break
        if first_item is None:
            for item in items_remaining:
                for l,w,h in item.get_rotation():
                    if h<=bin.height and l<=bin.length and w<=bin.width:
                        item.set_rotation(l,w,h)
                        first_item=item
                        items_remaining.pop(item)
                        break
    if first_item is None:
        print("所有物品高度均超出箱子，无法放置")
        return []
    
    pos = (0, 0, 0)
    if not bin.is_valid_position(first_item, pos):
        print("第一个物品无法放置")
        return []
    bin.add_item(first_item, pos)
    placed.append(first_item)
    shelves.append({'x': 0, 'y': first_item.length, 'width': first_item.width})
    max_x = first_item.width

    '''
    继续放置
    '''
    while items_remaining:
        if not shelves:
            break
        current_shelf = shelves[-1]
        cur_x = current_shelf['x']
        cur_y = current_shelf['y']
        shelf_width = current_shelf['width']
        avail_length = bin.length - cur_y

        #在当前排寻找可放物品
        candidates = []
        for item in items_remaining:
            if (item.width <= shelf_width and
                item.length <= avail_length and
                item.height <= bin.height):
                candidates.append(item)

        
        if candidates:
            # 1. 使用 DP 选出最优的一组物品
            best_group = row_dp(avail_length,shelf_width,bin.height,candidates)
            if not best_group:
                # 没有物品能放入当前排，尝试开新排
                pass
            else:
                # 2. 依次将这组物品放入当前排
                for chosen in best_group:
                    item,l,w,h=chosen
                    item.set_rotation(l,w,h)
                    pos = (cur_x, cur_y, 0)
                    if bin.is_valid_position(item, pos):
                        bin.add_item(item, pos)
                        placed.append(item)
                        items_remaining.remove(item)
                        cur_y += item.length  # 更新当前排的 Y 坐标
                        max_x = max(max_x, cur_x + item.width)
                        #print(f"地面层: 物品 {chosen.id} 放在当前排 (x={cur_x}, y={pos[1]})")
                current_shelf['y'] = cur_y  # 更新当前排的 Y 坐标
                continue
            
            


        #无法在当前排放置，尝试开新排
        new_x = max_x
        #从剩余物品中选底面积最大的，且能放入新排
        items_remaining.sort(key=lambda x: x.area, reverse=True)
        found = False
        for item in items_remaining[:]:
            if (item.width <= bin.width - new_x and
                item.length <= bin.length and
                item.height <= bin.height):
                pos = (new_x, 0, 0)
                if bin.is_valid_position(item, pos):
                    bin.add_item(item, pos)
                    placed.append(item)
                    if item in items_remaining:
                        items_remaining.remove(item)
                    shelves.append({'x': new_x, 'y': item.length, 'width': item.width})
                    max_x = max(max_x, new_x + item.width)
                    #print(f"地面层: 物品 {item.id} 开新排 (x={new_x}, y=0)")
                    found = True
                    break
        if not found:
            break   #无法开新排，地面层结束

    return items_remaining   #返回未放置的物品


def has_support(bin,item,pos):
    '''
    支撑面积计算
    '''
    x,y,z=pos
    if z==0:
        return True
    
    supported_area=0
    item_area=item.width*item.length

    for ex in bin.items:
        es_top_z=ex.pos[2]+ex.height
        if es_top_z==z:
            dx=max(0,min(x+item.width,ex.pos[0]+ex.width)-max(x,ex.pos[0])) #右边界较小，左边界较大
            dy=max(0,min(y+item.length,ex.pos[1]+ex.length)-max(y,ex.pos[1]))
            if dx>0 and dy>0:
                supported_area+=dx*dy
    #如果支撑面积占物品底面积的比例超过60%，则认为有足够的支撑
    
    return (supported_area / item_area)>=0.8



def pack_multi_levels(bin,remaning_items):
    #多层堆叠
    remaning_items.sort(key=lambda x: x.area, reverse=True)
    placed_any=True
    while remaning_items and placed_any:
        placed_any=False
        items_to_remove=[]

        anchor_points=set()
        for ex in bin.items:
            anchor_points.add((ex.pos[0],ex.pos[1],ex.pos[2]+ex.height))
            anchor_points.add((ex.pos[0]+ex.width,ex.pos[1],ex.pos[2]))
            anchor_points.add((ex.pos[0],ex.pos[1]+ex.length,ex.pos[2]))

        valid_anchors=sorted([p for p in anchor_points if p[2]<bin.height], key=lambda p: (p[2],p[1],p[0]))

        for item in remaning_items:
            placed_this_item=False

            #获取物品旋转可能的姿态
            rotations=item.get_rotation()
            #保存该物品的尺寸，以便尝试放置失败后恢复
            original_dims=(item.length,item.width,item.height)



            for pos in valid_anchors:
                if placed_this_item:
                    break
                #遍历每种旋转姿态
                for l, w, h in rotations:
                    # 更新物品姿态并立即检测该姿态能否放置
                    item.set_rotation(l, w, h)
                    if bin.is_valid_position(item, pos) and has_support(bin, item, pos):
                        bin.add_item(item, pos)
                        items_to_remove.append(item)
                        placed_any = True
                        placed_this_item = True

                        x, y, z = pos
                        # 更新新的锚点
                        new_anchors = [
                            (x, y, z + item.height),
                            (x + item.width, y, z),
                            (x, y + item.length, z)
                        ]
                        valid_anchors.extend(new_anchors)
                        valid_anchors = sorted(valid_anchors, key=lambda p: (p[2], p[1], p[0]))
                        break

                # 如果该物品在所有旋转姿态都无法放置，恢复原始尺寸
                if not placed_this_item:
                    item.set_rotation(*original_dims)
                else:
                    break

        for item in items_to_remove:
            if item in remaning_items:
                remaning_items.remove(item)

def pack_items(bin,items):
    '''
    装箱主函数
    '''

    remaining=pack_ground_floor(bin,items)
    pack_multi_levels(bin,remaining)
    return bin.items

if __name__=="__main__":


    file_path = "./data/LP113Goods.csv.xlsx"


    df=pd.read_excel(file_path)


    name_col = '名称'
    len_col  = '长'        # 长度 Y轴
    wid_col  = '宽'        # 宽度 X轴
    hei_col  = '高'        # 高度 Z轴
    qty_col  = '数量'

    items_from_excel=[]
    for idx,row in df.iterrows():
        name=row[name_col]
        length=int(row[len_col])
        width=int(row[wid_col])
        height=int(row[hei_col])
        qty=int(row[qty_col])

        for i in range(qty):
            item_name = f"{name}_{i+1}" if qty > 1 else name
            items_from_excel.append(Item(item_name, length, width, height))
    
    print(f"共生成{len(items_from_excel)}个物品")

    #BIN_LENGTH,BIN_WIDTH,BIN_HEIGHT= 5890, 2350, 2390 #20寸柜子
    BIN_LENGTH, BIN_WIDTH, BIN_HEIGHT = 13560, 2352, 2678   # 40寸柜子：13560, 2352, 2678
    bin = Bin(BIN_LENGTH, BIN_WIDTH, BIN_HEIGHT)

    pack_items(bin, items_from_excel)

    total_items=0

    for item in bin.items:
        total_items=total_items+1
        #print(f"物品 {item.id}: 位置 {item.pos}, 尺寸 (长={item.length}, 宽={item.width}, 高={item.height})")

    print(f"共放置 {total_items} 个物品")

    calculate_utilization(bin)

    output_csv = "packing_result.csv"
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', '长', '宽', '高', '左右', '前后', '上下'])
        for idx, item in enumerate(bin.items, start=1):
            writer.writerow([
                f"{item.id}_{idx}" if hasattr(item, 'id') else f"Item_{idx}",
                item.length,
                item.width,
                item.height,
                item.pos[1],   # 左右 = x
                item.pos[0],   # 前后 = y
                item.pos[2]    # 上下 = z
            ])

    print(f"装箱结果已保存到 {output_csv}")



    # 读取 CSV
    df = pd.read_csv("packing_result.csv")
    # convert_to_packed_items 需要一个 DataFrame 的列表
    walls = [df]
    # 箱子尺寸：长(Y)、宽(X)、高(Z)
    bin_size = (BIN_LENGTH, BIN_WIDTH, BIN_HEIGHT)

    packed_items = convert_to_packed_items(walls)
    visualize_3d_packing(bin_size, packed_items, title="3D Packing Result")














    