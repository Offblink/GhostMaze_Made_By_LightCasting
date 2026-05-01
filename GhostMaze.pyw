import pygame
import numpy as np
import random
import math
import sys
import locale
from pygame import gfxdraw
import os
import heapq  # 用于A*算法的优先队列

# 设置中文编码
try:
    locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'chinese')
    except:
        pass

# 初始化pygame
pygame.init()

# 尝试设置窗口图标
try:
    icon = pygame.image.load('icon.ico')
    pygame.display.set_icon(icon)
except:
    # 如果都没有，创建动态图标
    def icon_not_found():  
        return

# ============================================================================
# 音效系统初始化
# ============================================================================
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# ============================================================================
# 窗口设置 - 修改为1068×801比例
# ============================================================================
BASE_WINDOW_WIDTH = 1068
BASE_WINDOW_HEIGHT = 801
WIDTH, HEIGHT = BASE_WINDOW_WIDTH, BASE_WINDOW_HEIGHT  # 添加这行
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GhostMaze")

# ============================================================================
# 关卡系统配置
# ============================================================================

# 关卡数量
TOTAL_LEVELS = 3

# 每关的迷宫尺寸配置
LEVEL_MAZE_SIZES = [
    (15, 15),   # 第一关：15×15
    (19, 19),   # 第二关：19×19
    (25, 25)    # 第三关：25×25
]

# 每关的幽灵追踪半径配置
LEVEL_GHOST_CHASE_RADIUS = [10.0, 12.0, 16.0]  # 逐关增加

# 每关的钥匙数量配置
LEVEL_KEY_COUNTS = [1, 2, 4]  # 第一关1把，第二关2把，第三关4把

# 每关的地图数量配置（新增：每关1个）
LEVEL_MAP_COUNTS = [1, 1, 1]  # 每关均有且仅有1个地图道具

# 每关的幽灵贴图文件配置（需要外部图片文件）
LEVEL_GHOST_IMAGES = [
    "png\ghost1_80x80.png",  # 第一关幽灵贴图
    "png\ghost2_80x80.png",  # 第二关幽灵贴图（更恐怖）
    "png\ghost3_80x80.png"   # 第三关幽灵贴图（最恐怖）
]

# ============================================================================
# 颜色定义 - 按关卡划分
# ============================================================================

# 第一关颜色（相对明亮）
COLORS_LEVEL1 = {
    'bg': (20, 20, 30),
    'wall': (100, 100, 150),      # 浅灰紫
    'corner': (0, 0, 0),
    'path': (30, 30, 40),
    'player': (0, 150, 255),
    'ghost': (148, 0, 211, 160),
    'exit': (0, 255, 100),        # 出口颜色保持不变
    'exit_wall': (50, 200, 100),
    'trigger_zone': (255, 200, 0, 100),
    'sky_top': (135, 206, 235),       # 天蓝色顶部（修改）
    'sky_bottom': (240, 248, 255),    # 淡蓝色底部（修改）
    'floor': (34, 139, 34),       # 森林绿
    'ray': (255, 200, 100, 100),
    'text': (220, 220, 240),
    'ui_bg': (30, 35, 50, 200),
    'ui_border': (60, 70, 100),
    'key': (255, 215, 0),         # 金色钥匙
    'key_ui': (255, 223, 0),
    'heart': (255, 105, 97),      # 珊瑚红爱心
    'heart_ui': (255, 60, 60),
    'lives_ui': (255, 80, 80),
    'fade_overlay': (0, 0, 0, 0),
    'map': (50, 200, 255),        # 新增：地图道具颜色（亮蓝色）
    'map_ui': (100, 220, 255),    # 新增：地图UI颜色
}

# 第二关颜色（中等压抑）
COLORS_LEVEL2 = {
    'bg': (15, 15, 25),
    'wall': (80, 80, 130),        # 中灰紫
    'corner': (0, 0, 0),
    'path': (25, 25, 35),
    'player': (0, 130, 230),
    'ghost': (128, 0, 191, 180),  # 稍微加深
    'exit': (0, 255, 100),        # 出口颜色保持不变
    'exit_wall': (50, 200, 100),
    'trigger_zone': (255, 180, 0, 100),
    'sky_top': (100, 150, 200),       # 灰蓝色顶部（修改）
    'sky_bottom': (180, 200, 220),    # 浅灰蓝色底部（修改）
    'floor': (20, 100, 20),       # 暗绿色
    'ray': (255, 180, 80, 100),
    'text': (200, 200, 220),
    'ui_bg': (25, 30, 45, 200),
    'ui_border': (50, 60, 90),
    'key': (255, 175, 0),         # 橙色钥匙
    'key_ui': (255, 183, 0),
    'heart': (255, 105, 97),      # 爱心颜色保持不变
    'heart_ui': (255, 60, 60),
    'lives_ui': (255, 80, 80),
    'fade_overlay': (0, 0, 0, 0),
    'map': (40, 180, 235),        # 新增：地图道具颜色
    'map_ui': (80, 200, 245),     # 新增：地图UI颜色
}

# 第三关颜色（高度压抑）
COLORS_LEVEL3 = {
    'bg': (10, 10, 20),
    'wall': (60, 60, 100),        # 深灰紫
    'corner': (0, 0, 0),
    'path': (20, 20, 30),
    'player': (0, 110, 210),
    'ghost': (108, 0, 161, 200),  # 进一步加深
    'exit': (0, 255, 100),        # 出口颜色保持不变
    'exit_wall': (50, 200, 100),
    'trigger_zone': (255, 160, 0, 100),
    'sky_top': (50, 70, 100),        # 深灰蓝顶部（修改）
    'sky_bottom': (100, 120, 150),   # 中灰蓝底部（修改）
    'floor': (10, 50, 10),        # 深绿色
    'ray': (255, 160, 60, 100),
    'text': (180, 180, 200),
    'ui_bg': (20, 25, 40, 200),
    'ui_border': (40, 50, 80),
    'key': (255, 100, 0),         # 暗橙色钥匙
    'key_ui': (255, 108, 0),
    'heart': (255, 105, 97),      # 爱心颜色保持不变
    'heart_ui': (255, 60, 60),
    'lives_ui': (255, 80, 80),
    'fade_overlay': (0, 0, 0, 0),
    'map': (30, 160, 215),        # 新增：地图道具颜色
    'map_ui': (60, 180, 235),     # 新增：地图UI颜色
}


# 关卡颜色列表，便于按索引访问
LEVEL_COLORS = [COLORS_LEVEL1, COLORS_LEVEL2, COLORS_LEVEL3]

# 当前使用的颜色（默认第一关）
COLORS = COLORS_LEVEL1

# 加载中文字体
try:
    font_small = pygame.font.SysFont('simhei', 16)
    font_normal = pygame.font.SysFont('simhei', 20)
    font_large = pygame.font.SysFont('simhei', 24)
    font_bold = pygame.font.SysFont('simhei', 28, bold=True)
except:
    font_small = pygame.font.Font(None, 16)
    font_normal = pygame.font.Font(None, 20)
    font_large = pygame.font.Font(None, 24)
    font_bold = pygame.font.Font(None, 28)  # 回退到默认字体的粗体版本

# ============================================================================
# 音效管理器类
# ============================================================================
class AudioManager:
    """音效和背景音乐管理器（简化版：仅保留探索背景音乐）"""
    
    def __init__(self):
        self.volume = 1.0  # 主音量
        
        # 背景音乐音轨（仅保留探索音乐）
        self.wander_music = None
        self.wander_channel = None
        
        # 音效
        self.sounds = {}
        
        # 状态
        self.paused = False
        self.music_loaded = False
        
        # 音量比例因子
        self.music_volume_factor = 1.0  # 背景音乐音量因子
        self.sound_volume_factor = 0.9  # 音效音量因子
        
        # 加载音效
        self._load_sounds()
        
        # 加载背景音乐
        self._load_background_music()
        
        # 脚步声控制
        self.step_timer = 0
        self.step_interval = 1000  # 脚步声间隔（毫秒）
        self.is_playing_step = False
        
    def _load_sounds(self):
        """加载所有音效文件"""
        sound_files = {
            'step': 'mp3\step.mp3',
            'key': 'mp3\key.mp3',
            'map': 'mp3\map.mp3',
            'heart': 'mp3\heart.mp3',
            'caught': 'mp3\caught.mp3'
        }
        
        for name, filename in sound_files.items():
            try:
                if os.path.exists(filename):
                    sound = pygame.mixer.Sound(filename)
                    # 应用音效音量因子
                    sound.set_volume(self.volume * self.sound_volume_factor)
                    self.sounds[name] = sound
                    print(f"音效 '{filename}' 加载成功")
                else:
                    print(f"警告: 音效文件 '{filename}' 不存在")
                    self.sounds[name] = None
            except Exception as e:
                print(f"加载音效 '{filename}' 失败: {e}")
                self.sounds[name] = None
    
    def _load_background_music(self):
        """加载背景音乐（仅加载探索音乐）"""
        try:
            # 仅加载探索音乐
            if os.path.exists('mp3\wander.mp3'):
                self.wander_music = pygame.mixer.Sound('mp3\wander.mp3')
                # 应用背景音乐音量因子
                self.wander_music.set_volume(self.volume * self.music_volume_factor)
                print("背景音乐 'wander.mp3' 加载成功")
            else:
                print("警告: 背景音乐文件 'wander.mp3' 不存在")
                self.wander_music = None
            
            self.music_loaded = True
            
        except Exception as e:
            print(f"加载背景音乐失败: {e}")
            self.music_loaded = False
    
    def start_background_music(self):
        """开始播放背景音乐（仅播放探索音乐）"""
        if not self.music_loaded or self.paused:
            return
        
        try:
            if self.wander_music and self.wander_channel is None:
                self.wander_channel = self.wander_music.play(loops=-1)
                # 设置固定音量（不再根据幽灵距离调整）
                self.wander_channel.set_volume(self.volume * self.music_volume_factor)
                print("开始播放探索音乐")
                
        except Exception as e:
            print(f"播放背景音乐失败: {e}")
    
    def update_music_volume(self, ghost_distance, max_distance=25.0):
        """更新音乐音量（保持探索音乐音量不变）"""
        if self.paused or not self.music_loaded:
            return
        
        if not self.wander_channel:
            return
        
        # 探索音乐保持固定音量（不随幽灵距离变化）
        wander_volume = self.volume * self.music_volume_factor
        
        # 确保音量不超过1.0
        wander_volume = min(wander_volume, 1.0)
        
        try:
            self.wander_channel.set_volume(wander_volume)
        except:
            pass
            
    def play_sound(self, sound_name):
        """播放指定音效"""
        if self.paused or sound_name not in self.sounds:
            return
        
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except Exception as e:
                print(f"播放音效 '{sound_name}' 失败: {e}")
    
    def play_step_sound(self, moved, dt):
        """播放脚步声（需要移动且有间隔）"""
        if self.paused or not moved:
            self.step_timer = 0
            return
        
        self.step_timer += dt * 1000
        
        if self.step_timer >= self.step_interval:
            self.step_timer = 0
            self.play_sound('step')
    
    def pause(self):
        """暂停所有音效和音乐"""
        if self.paused:
            return
        
        self.paused = True
        
        try:
            if self.wander_channel:
                self.wander_channel.pause()
        except:
            pass
        
        print("音频已暂停")
    
    def resume(self):
        """恢复所有音效和音乐"""
        if not self.paused:
            return
        
        self.paused = False
        
        try:
            if self.wander_channel:
                self.wander_channel.unpause()
        except:
            pass
        
        print("音频已恢复")
    
    def set_volume(self, volume):
        """设置主音量（范围0.0-1.0）"""
        # 限制音量在合理范围内
        self.volume = max(0.0, min(1.0, volume))
        
        # 更新所有音效音量
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.volume * self.sound_volume_factor)
        
        # 如果有音乐正在播放，重新计算音乐音量
        if self.music_loaded and not self.paused:
            try:
                # 探索音乐保持固定音量
                if self.wander_channel:
                    self.wander_channel.set_volume(self.volume * self.music_volume_factor)
            except:
                pass
    
    def adjust_volume_factors(self, music_factor=None, sound_factor=None):
        """动态调整音量因子
        
        参数:
            music_factor: 新的背景音乐音量因子（默认1.2）
            sound_factor: 新的音效音量因子（默认0.5）
        """
        if music_factor is not None:
            self.music_volume_factor = max(0.0, music_factor)
        
        if sound_factor is not None:
            self.sound_volume_factor = max(0.0, sound_factor)
        
        # 应用新的音量因子
        self.set_volume(self.volume)
        
        print(f"音量因子已更新 - 音乐: {self.music_volume_factor:.1f}x, 音效: {self.sound_volume_factor:.1f}x")
    
    def stop_all(self):
        """停止所有声音"""
        try:
            if self.wander_channel:
                self.wander_channel.stop()
            
            pygame.mixer.stop()
            
        except:
            pass
        
        self.wander_channel = None
    
    def get_volume_info(self):
        """获取当前音量信息"""
        return {
            'master_volume': self.volume,
            'music_factor': self.music_volume_factor,
            'sound_factor': self.sound_volume_factor,
            'actual_music_volume': self.volume * self.music_volume_factor,
            'actual_sound_volume': self.volume * self.sound_volume_factor,
            'music_to_sound_ratio': self.music_volume_factor / self.sound_volume_factor if self.sound_volume_factor > 0 else 0
        }
        
# 创建全局音频管理器实例
audio_manager = AudioManager()

# 基础迷宫参数（会被关卡配置覆盖）
BASE_MAZE_WIDTH, BASE_MAZE_HEIGHT = 15, 15
CELL_SIZE = 30

RAY_COUNT = 300 # 渲染粒度

# 玩家参数
PLAYER_RADIUS = 0.3
PLAYER_DISPLAY_RADIUS = 8
FOV = 80
MAX_VIEW_DISTANCE = 10
TRIGGER_DISTANCE = 2.0

# 幽灵参数（会被关卡配置覆盖）
GHOST_MAX_VISIBLE_DISTANCE = 25.0
GHOST_CHASE_RADIUS = 2.0  # 第一关默认值
GHOST_CATCH_DISTANCE = 0.7

# 钥匙参数
KEY_PICKUP_DISTANCE = 0.7  # 拾取距离，与玩家半径和钥匙大小相关
KEY_SIZE_2D = 30  # 2D视图中的显示大小（像素）
KEY_SIZE_3D_BASE = 150  # 3D视图中的大小基准值

# 生命值参数
PLAYER_INITIAL_LIVES = 3  # 玩家初始生命值
HEART_PICKUP_DISTANCE = 0.7  # 爱心拾取距离
HEART_SIZE_2D = 30  # 2D视图中爱心大小
HEART_SIZE_3D_BASE = 120  # 3D视图中爱心大小基准值

# 地图道具参数（新增）
MAP_PICKUP_DISTANCE = 0.7  # 拾取距离
MAP_SIZE_2D = 30  # 2D视图中的显示大小
MAP_SIZE_3D_BASE = 140  # 3D视图中的大小基准值
MAP_REVEAL_DURATION = 10000  # 地图显示持续时间（毫秒），即10秒

# 渐变过渡参数
FADE_DURATION = 1000  # 渐变持续时间（毫秒）
FADE_MAX_ALPHA = 180  # 渐变覆盖层最大透明度

# 关卡过渡参数
LEVEL_TRANSITION_DURATION = 1500  # 关卡过渡渐变持续时间（毫秒）

# 2D缩略图显示参数（新增：用于右上角显示）
MINI_MAP_SIZE = 240  # #右上角缩略图边长（像素）
MINI_MAP_MARGIN = 10  # 右上角缩略图边距
MINI_MAP_FADE_DURATION = 500  # 缩略图淡入淡出时间（毫秒）
MINI_MAP_CELL_SIZE = 8  # 缩略图中每个格子的像素大小

class AStarPathfinder:
    """A*寻路算法实现类"""
    
    def __init__(self, maze_grid):
        self.grid = maze_grid
        self.width = maze_grid.shape[0]
        self.height = maze_grid.shape[1]
        
    class Node:
        """A*算法节点类"""
        def __init__(self, x, y, g=0, h=0, parent=None):
            self.x = x
            self.y = y
            self.g = g  # 从起点到当前节点的代价
            self.h = h  # 启发式估计到目标的代价
            self.f = g + h  # 总代价
            self.parent = parent
            
        def __lt__(self, other):
            # 用于优先队列比较
            return self.f < other.f or (self.f == other.f and self.h < other.h)
    
    def heuristic(self, x1, y1, x2, y2):
        """曼哈顿距离启发式函数"""
        return abs(x1 - x2) + abs(y1 - y2)
    
    def get_neighbors(self, node):
        """获取当前节点的可通行邻居"""
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # 上下左右
        
        for dx, dy in directions:
            nx, ny = node.x + dx, node.y + dy
            
            # 检查边界和墙壁
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if self.grid[nx, ny] == 0:  # 只有路径可以通行
                    neighbors.append((nx, ny))
        
        return neighbors
    
    def find_path(self, start_pos, target_pos):
        """
        使用A*算法寻找从start_pos到target_pos的路径
        start_pos: (x, y) 起点坐标
        target_pos: (x, y) 目标坐标
        返回: 路径列表，每个元素为(x, y)坐标，如果找不到路径则返回空列表
        """
        start_x, start_y = int(start_pos[0]), int(start_pos[1])
        target_x, target_y = int(target_pos[0]), int(target_pos[1])
        
        # 如果起点或终点是墙壁，直接返回空路径
        if (start_x < 0 or start_x >= self.width or start_y < 0 or start_y >= self.height or
            target_x < 0 or target_x >= self.width or target_y < 0 or target_y >= self.height):
            return []
        
        if self.grid[start_x, start_y] == 1 or self.grid[target_x, target_y] == 1:
            return []
        
        # 初始化开放列表和封闭列表
        open_list = []
        closed_set = set()
        
        # 创建起始节点
        start_node = self.Node(start_x, start_y)
        start_node.h = self.heuristic(start_x, start_y, target_x, target_y)
        start_node.f = start_node.g + start_node.h
        
        heapq.heappush(open_list, start_node)
        
        while open_list:
            # 获取f值最小的节点
            current_node = heapq.heappop(open_list)
            
            # 如果到达目标，重构路径
            if current_node.x == target_x and current_node.y == target_y:
                path = []
                while current_node:
                    path.append((current_node.x + 0.5, current_node.y + 0.5))  # 返回格子中心坐标
                    current_node = current_node.parent
                return path[::-1]  # 反转路径，从起点到终点
            
            # 将当前节点加入封闭列表
            closed_set.add((current_node.x, current_node.y))
            
            # 检查所有邻居
            for nx, ny in self.get_neighbors(current_node):
                if (nx, ny) in closed_set:
                    continue
                
                # 计算邻居节点的g值
                new_g = current_node.g + 1  # 每个移动代价为1
                
                # 检查邻居是否已在开放列表中
                neighbor_in_open = None
                for node in open_list:
                    if node.x == nx and node.y == ny:
                        neighbor_in_open = node
                        break
                
                if neighbor_in_open:
                    # 如果找到更优路径，更新节点
                    if new_g < neighbor_in_open.g:
                        neighbor_in_open.g = new_g
                        neighbor_in_open.f = new_g + neighbor_in_open.h
                        neighbor_in_open.parent = current_node
                else:
                    # 创建新节点
                    neighbor_node = self.Node(nx, ny, new_g)
                    neighbor_node.h = self.heuristic(nx, ny, target_x, target_y)
                    neighbor_node.f = neighbor_node.g + neighbor_node.h
                    neighbor_node.parent = current_node
                    heapq.heappush(open_list, neighbor_node)
        
        # 没有找到路径
        return []

class Ghost:
    """幽灵怪物类 - 支持多关卡不同贴图及第一关四向显示"""
    def __init__(self, maze_width, maze_height, maze_grid, level_index=0):
        self.radius = 0.4
        self.width_3d = 0.8
        
        # 根据关卡索引获取幽灵贴图文件名
        self.level_index = level_index
        self.ghost_image_file = LEVEL_GHOST_IMAGES[level_index]
        
        # 根据关卡索引获取颜色
        self.color = LEVEL_COLORS[level_index]['ghost']
        
        # === 新增：幽灵朝向属性 ===
        self.facing_angle = random.uniform(0, 2 * math.pi)  # 初始随机朝向（弧度）
        
        # 2D视图参数
        self.pixel_size = 8

        # 3D视图参数
        self.base_3d_size = 800
        self.scale_3d = 100

        # 移动和追踪参数 - 根据关卡设置追踪半径
        self.chase_radius = LEVEL_GHOST_CHASE_RADIUS[level_index]
        self.slow_speed = 0.03 # 游走速度
        self.fast_speed = 0.05 # 追踪速度
        self.current_speed = self.slow_speed
        
        self.maze_grid = maze_grid
        
        # A*寻路器
        self.pathfinder = AStarPathfinder(maze_grid)
        
        # 路径追踪参数
        self.current_path = [] # 当前要跟随的路径
        self.current_target = None # 当前目标位置
        self.path_index = 0 # 当前路径索引
        self.repath_timer = 0 # 重新寻路计时器
        self.repath_interval = 5000 # 重新寻路间隔（毫秒）
        
        # 随机游走参数
        self.walk_state = "random" # 状态: "random"（随机游走）或 "chase"（追踪玩家）
        self.random_target_timer = 0
        self.random_target_interval = 3000 # 随机目标更新间隔（毫秒）
        
        # 生成幽灵像素画
        self.sprite_2d = self._create_ghost_sprite_2d()
        
        # === 修改：加载贴图（区分第一关和其他关卡） ===
        if self.level_index == 0:
            # 第一关：加载四向贴图
            self.sprite_3d_colors = self._load_ghost_sprite_3d_multi_direction()
        else:
            # 其他关卡：保持原有单贴图逻辑
            self.sprite_3d_colors = self._load_ghost_sprite_3d()
        
        # === 修改：预处理贴图 ===
        self.original_surface = None # 单贴图使用
        self.original_surfaces = {}  # 四向贴图使用
        self.preprocess_sprite()
        
        self.scaled_cache = {}
        
        # 在迷宫中随机放置幽灵
        self.x, self.y = self._place_in_maze(maze_width, maze_height, maze_grid)
        
        # 幽灵动画相关
        self.animation_timer = 0
        self.animation_speed = 0.05
        self.wave_offset = 0
        self.visible = True
        
        # 设置初始随机目标
        self._set_random_target()
        
        # 初始化朝向（朝向初始目标）
        if self.current_target:
            self.facing_angle = math.atan2(self.current_target[1] - self.y, self.current_target[0] - self.x)

    def _create_ghost_sprite_2d(self):
        sprite = [
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 0, 1, 1, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 1, 0, 0, 1, 0, 1],
            [0, 1, 0, 1, 1, 0, 1, 0]
        ]
        return sprite

    def _load_ghost_sprite_3d(self):
        """加载单张幽灵贴图（其他关卡使用）"""
        try:
            image_path = self.ghost_image_file
            if not os.path.exists(image_path):
                print(f"第{self.level_index+1}关幽灵图片文件 '{image_path}' 不存在，使用默认贴图")
                return self._create_default_ghost_sprite_3d_colored()
            ghost_image = pygame.image.load(image_path).convert_alpha()
            if ghost_image.get_width() != 80 or ghost_image.get_height() != 80:
                ghost_image = pygame.transform.scale(ghost_image, (80, 80))
            sprite_colors = []
            for y in range(80):
                row_colors = []
                for x in range(80):
                    pixel_color = ghost_image.get_at((x, y))
                    row_colors.append(pixel_color)
                sprite_colors.append(row_colors)
            return sprite_colors
        except Exception as e:
            print(f"加载第{self.level_index+1}关幽灵图片失败: {e}")
            return self._create_default_ghost_sprite_3d_colored()

    def _load_ghost_sprite_3d_multi_direction(self):
        """加载第一关幽灵的四向贴图（前、后、左、右）"""
        directions = ['front', 'back', 'left', 'right']
        sprites_data = {}
        
        for direction in directions:
            # 假设文件命名格式为 ghost1_front.png 等
            image_path = f"png\\ghost1_{direction}.png" 
            
            sprite_colors = []
            try:
                if os.path.exists(image_path):
                    ghost_image = pygame.image.load(image_path).convert_alpha()
                    if ghost_image.get_width() != 80 or ghost_image.get_height() != 80:
                        ghost_image = pygame.transform.scale(ghost_image, (80, 80))
                    
                    for y in range(80):
                        row_colors = []
                        for x in range(80):
                            pixel_color = ghost_image.get_at((x, y))
                            row_colors.append(pixel_color)
                        sprite_colors.append(row_colors)
                    print(f"成功加载第一关幽灵贴图: {direction}")
                else:
                    print(f"警告: 第一关幽灵贴图 '{image_path}' 不存在，使用默认贴图")
                    sprite_colors = self._create_default_ghost_sprite_3d_colored()
                    
            except Exception as e:
                print(f"加载第一关幽灵贴图 {direction} 失败: {e}")
                sprite_colors = self._create_default_ghost_sprite_3d_colored()
            
            sprites_data[direction] = sprite_colors
            
        return sprites_data

    def _create_default_ghost_sprite_3d_colored(self):
        """创建默认幽灵贴图，根据关卡调整颜色"""
        sprite_colors = [[(0, 0, 0, 0) for _ in range(80)] for _ in range(80)]
        center_x, center_y = 40, 30
        body_radius = 25
        
        # 根据关卡调整颜色强度
        if self.level_index == 0:
            base_r, base_g, base_b = 148, 0, 211
        elif self.level_index == 1:
            base_r, base_g, base_b = 128, 0, 191
        else:
            base_r, base_g, base_b = 108, 0, 161
            
        for y in range(80):
            for x in range(80):
                dist = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                if dist <= body_radius:
                    intensity = 1.0 - (dist / body_radius) * 0.3
                    r = int(base_r * intensity)
                    g = int(base_g * intensity)
                    b = int(base_b * intensity)
                    a = 255
                    sprite_colors[y][x] = (r, g, b, a)
        
        wave_height = 15
        wave_frequency = 0.20
        base_y = center_y + body_radius
        
        for x in range(80):
            wave_offset = int(wave_height * math.sin(x * wave_frequency))
            wave_y = base_y + wave_offset
            for y in range(wave_y, min(80, wave_y + 25)):
                if 0 <= x < 80 and 0 <= y < 80:
                    if self.level_index == 0:
                        sprite_colors[y][x] = (180, 50, 230, 255)
                    elif self.level_index == 1:
                        sprite_colors[y][x] = (160, 40, 210, 255)
                    else:
                        sprite_colors[y][x] = (140, 30, 190, 255)
        
        eye_radius = 6
        left_eye_x = center_x - 12
        right_eye_x = center_x + 12
        eye_y = center_y - 5
        
        for y in range(80):
            for x in range(80):
                left_dist = ((x - left_eye_x) ** 2 + (y - eye_y) ** 2) ** 0.5
                right_dist = ((x - right_eye_x) ** 2 + (y - eye_y) ** 2) ** 0.5
                if left_dist <= eye_radius or right_dist <= eye_radius:
                    if self.level_index == 2:
                        sprite_colors[y][x] = (100, 0, 0, 255)
                    else:
                        sprite_colors[y][x] = (0, 0, 0, 255)
        return sprite_colors

    def preprocess_sprite(self):
        """预处理3D贴图，创建Pygame表面"""
        if self.level_index == 0:
            # 第一关：处理四向贴图
            for direction, colors in self.sprite_3d_colors.items():
                surface = pygame.Surface((80, 80), pygame.SRCALPHA)
                for y in range(80):
                    for x in range(80):
                        pixel_color = colors[y][x]
                        if len(pixel_color) == 4 and pixel_color[3] > 0:
                            surface.set_at((x, y), pixel_color)
                self.original_surfaces[direction] = surface
        else:
            # 其他关卡：处理单张贴图
            self.original_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
            for y in range(80):
                for x in range(80):
                    pixel_color = self.sprite_3d_colors[y][x]
                    if len(pixel_color) == 4 and pixel_color[3] > 0:
                        self.original_surface.set_at((x, y), pixel_color)

    def _place_in_maze(self, maze_width, maze_height, maze_grid):
        available_positions = []
        for x in range(maze_width):
            for y in range(maze_height):
                if maze_grid[x, y] == 0:
                    center_x, center_y = maze_width // 2, maze_height // 2
                    if abs(x - center_x) > 3 or abs(y - center_y) > 3:
                        available_positions.append((x + 0.5, y + 0.5))
        if available_positions:
            return random.choice(available_positions)
        else:
            return (maze_width // 2 + 0.5, maze_height // 2 + 0.5)

    def _set_random_target(self):
        available_positions = []
        for x in range(self.maze_grid.shape[0]):
            for y in range(self.maze_grid.shape[1]):
                if self.maze_grid[x, y] == 0:
                    if abs(x - int(self.x)) > 2 or abs(y - int(self.y)) > 2:
                        available_positions.append((x + 0.5, y + 0.5))
        if available_positions:
            self.current_target = random.choice(available_positions)
            # 更新朝向为新目标
            dx = self.current_target[0] - self.x
            dy = self.current_target[1] - self.y
            if math.sqrt(dx*dx + dy*dy) > 0:
                self.facing_angle = math.atan2(dy, dx)
                
            self.current_path = self.pathfinder.find_path((self.x, self.y), self.current_target)
            self.path_index = 0
            self.random_target_timer = pygame.time.get_ticks()
        else:
            self.current_target = None
            self.current_path = []

    def _find_path_to_player(self, player_x, player_y):
        self.current_target = (player_x, player_y)
        self.current_path = self.pathfinder.find_path((self.x, self.y), (player_x, player_y))
        self.path_index = 0
        self.repath_timer = pygame.time.get_ticks()

    def _follow_path(self, dt):
        if not self.current_path or self.path_index >= len(self.current_path):
            return False
        target_x, target_y = self.current_path[self.path_index]
        
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # === 新增：移动时更新朝向 ===
        if distance > 0.1:
            self.facing_angle = math.atan2(dy, dx)
        
        if distance < 0.1:
            self.path_index += 1
            if self.path_index >= len(self.current_path):
                return True
            return self._follow_path(dt)
        
        move_x = (dx / distance) * self.current_speed
        move_y = (dy / distance) * self.current_speed
        
        new_x = self.x + move_x
        new_y = self.y + move_y
        if not self._check_collision(new_x, new_y):
            self.x = new_x
            self.y = new_y
        else:
            self.path_index += 1
        return False

    def _check_collision(self, x, y):
        points = [
            (x, y), (x + self.radius, y), (x - self.radius, y),
            (x, y + self.radius), (x, y - self.radius),
            (x + self.radius * 0.7, y + self.radius * 0.7),
            (x - self.radius * 0.7, y + self.radius * 0.7),
            (x + self.radius * 0.7, y - self.radius * 0.7),
            (x - self.radius * 0.7, y - self.radius * 0.7)
        ]
        for px, py in points:
            if px < 0 or px >= self.maze_grid.shape[0] or py < 0 or py >= self.maze_grid.shape[1]:
                return True
            if self.maze_grid[int(px), int(py)] == 1:
                return True
        return False

    def update(self, dt, player_x, player_y):
        self.animation_timer += dt * 1000
        self.wave_offset = math.sin(self.animation_timer * self.animation_speed * 0.001) * 0.1
        
        dx = player_x - self.x
        dy = player_y - self.y
        distance_to_player = math.sqrt(dx*dx + dy*dy)
        current_time = pygame.time.get_ticks()
        
        has_wall = self.has_wall_between(self.x, self.y, player_x, player_y)
        
        if not has_wall:
            if self.walk_state != "chase":
                self.walk_state = "chase"
                self.current_speed = self.fast_speed
                self._find_path_to_player(player_x, player_y)
            else:
                if current_time - self.repath_timer > self.repath_interval:
                    self._find_path_to_player(player_x, player_y)
        else:
            if distance_to_player < self.chase_radius:
                if self.walk_state != "chase":
                    self.walk_state = "chase"
                    self.current_speed = self.slow_speed
                    self._find_path_to_player(player_x, player_y)
                else:
                    if current_time - self.repath_timer > self.repath_interval:
                        self._find_path_to_player(player_x, player_y)
            else:
                if self.walk_state != "random":
                    self.walk_state = "random"
                    self.current_speed = self.slow_speed
                    self._set_random_target()
                else:
                    if current_time - self.random_target_timer > self.random_target_interval:
                        self._set_random_target()
        
        if self.current_path:
            reached_target = self._follow_path(dt * 1000)
            if reached_target:
                if self.walk_state == "random":
                    self._set_random_target()
                elif self.walk_state == "chase":
                    if self.walk_state == "chase":
                        self._find_path_to_player(player_x, player_y)
        else:
            if self.walk_state == "random":
                self._set_random_target()
            elif self.walk_state == "chase":
                self._find_path_to_player(player_x, player_y)

    def has_wall_between(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx*dx + dy*dy)
        if distance == 0:
            return False
        step_size = 0.1
        steps = int(distance / step_size) + 1
        step_x = dx / steps
        step_y = dy / steps
        for i in range(steps + 1):
            check_x = x1 + step_x * i
            check_y = y1 + step_y * i
            if check_x < 0 or check_x >= self.maze_grid.shape[0] or check_y < 0 or check_y >= self.maze_grid.shape[1]:
                return True
            if self.maze_grid[int(check_x), int(check_y)] == 1:
                return True
        return False

    def get_relative_position(self, player_x, player_y, player_angle):
        dx = self.x - player_x
        dy = self.y - player_y
        distance = math.sqrt(dx*dx + dy*dy)
        angle_to_ghost = math.atan2(dy, dx)
        relative_angle = angle_to_ghost - player_angle
        while relative_angle > math.pi:
            relative_angle -= 2 * math.pi
        while relative_angle < -math.pi:
            relative_angle += 2 * math.pi
        return distance, relative_angle

    def is_in_fov(self, player_angle, fov_rad):
        if not self.visible:
            return False
        distance, relative_angle = self.get_relative_position(0, 0, player_angle)
        return abs(relative_angle) < fov_rad / 2 and distance < GHOST_MAX_VISIBLE_DISTANCE

    def get_screen_position(self, player_x, player_y, player_angle, fov_degrees, screen_width, view_height):
        if not self.visible:
            return 0, 0, 0, False, 0, 0
        distance, relative_angle = self.get_relative_position(player_x, player_y, player_angle)
        if distance > GHOST_MAX_VISIBLE_DISTANCE:
            return 0, 0, 0, False, 0, 0
        fov_rad = math.radians(fov_degrees)
        if abs(relative_angle) > fov_rad / 2:
            return 0, 0, 0, False, 0, 0
        screen_x_ratio = 0.5 + (relative_angle / fov_rad)
        screen_x = screen_x_ratio * screen_width
        size = int(self.base_3d_size / (distance + 0.5))
        size = max(50, min(1000, size))
        eye_height = view_height // 2
        projection_factor = view_height * 0.5
        floor_y = eye_height + (projection_factor / distance)
        screen_y = min(view_height, int(floor_y))
        alpha = max(120, 255 - int(distance * 8))
        screen_width_projection = (self.width_3d / (distance + 0.5)) * (screen_width / math.tan(fov_rad / 2))
        screen_width_projection = int(max(10, screen_width_projection))
        return screen_x, screen_y, size, True, alpha, screen_width_projection

    def draw_2d(self, surface, offset_x, offset_y, cell_size):
        if not self.visible:
            return
        ghost_screen_x = offset_x + self.x * cell_size
        ghost_screen_y = offset_y + self.y * cell_size
        ghost_surface = pygame.Surface((self.pixel_size * 3, self.pixel_size * 3), pygame.SRCALPHA)
        for py in range(self.pixel_size):
            for px in range(self.pixel_size):
                if self.sprite_2d[py][px] == 1:
                    rect = pygame.Rect(px * 3, py * 3, 3, 3)
                    pygame.draw.rect(ghost_surface, self.color, rect)
        ghost_rect = ghost_surface.get_rect(center=(ghost_screen_x, ghost_screen_y))
        surface.blit(ghost_surface, ghost_rect)

    def draw_3d_sprite_optimized(self, surface, player_x, player_y, player_angle, fov_degrees, screen_width, view_height, wall_distances, line_width, pitch_offset=0):
        screen_x, screen_y, ghost_size, ghost_visible, alpha, ghost_screen_width = self.get_screen_position(
            player_x, player_y, player_angle, fov_degrees, screen_width, view_height
        )
        if not ghost_visible or ghost_size < 20:
            return
        
        # === 新增：根据朝向选择贴图 ===
        current_surface = None
        view_key = 'default'
        
        if self.level_index == 0:
            # 计算玩家相对于幽灵的角度
            angle_to_player = math.atan2(player_y - self.y, player_x - self.x)
            
            # 计算相对角度 (玩家方向 - 幽灵朝向)
            relative_angle = angle_to_player - self.facing_angle
            
            # 归一化到 [-pi, pi]
            while relative_angle > math.pi: relative_angle -= 2 * math.pi
            while relative_angle < -math.pi: relative_angle += 2 * math.pi
            
            # 判断方向
            if -math.pi/4 <= relative_angle < math.pi/4:
                view_key = 'front'
            elif math.pi/4 <= relative_angle < 3*math.pi/4:
                view_key = 'left'
            elif -3*math.pi/4 <= relative_angle < -math.pi/4:
                view_key = 'right'
            else:
                view_key = 'back'
            
            current_surface = self.original_surfaces.get(view_key)
        else:
            current_surface = self.original_surface

        if not current_surface:
            return

        # 计算幽灵在屏幕上的水平绘制范围
        ghost_left_screen = screen_x - ghost_screen_width // 2
        ghost_right_screen = screen_x + ghost_screen_width // 2
        ghost_left_screen = max(0, min(screen_width, ghost_left_screen))
        ghost_right_screen = max(0, min(screen_width, ghost_right_screen))
        
        ghost_distance = self.get_distance_to_player(player_x, player_y)
        num_samples = 41
        sample_points = []
        visible_columns = []
        
        for i in range(num_samples):
            sample_screen_x = ghost_left_screen + (ghost_screen_width * i) / (num_samples - 1)
            sample_screen_x = max(ghost_left_screen, min(ghost_right_screen, sample_screen_x))
            ray_idx = int(sample_screen_x / line_width)
            ray_idx = max(0, min(len(wall_distances) - 1, ray_idx))
            wall_dist_at_sample = wall_distances[ray_idx] if ray_idx < len(wall_distances) else MAX_VIEW_DISTANCE
            is_visible = ghost_distance < wall_dist_at_sample
            sample_points.append((sample_screen_x, is_visible))
            if is_visible:
                column_pos = (sample_screen_x - ghost_left_screen) / ghost_screen_width
                column_pos = max(0.0, min(1.0, column_pos))
                visible_columns.append(column_pos)
        
        if not visible_columns:
            return
        
        scaled_width = int(ghost_screen_width)
        scaled_height = int(ghost_size)
        
        # 缓存Key加入方向标识
        cache_key = (scaled_width, scaled_height, alpha, view_key if self.level_index == 0 else 'default')
        if cache_key in self.scaled_cache:
            full_scaled_surface = self.scaled_cache[cache_key]
        else:
            full_scaled_surface = pygame.transform.scale(current_surface, (scaled_width, scaled_height))
            if alpha < 255:
                temp_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
                temp_surface.blit(full_scaled_surface, (0, 0))
                temp_surface.set_alpha(alpha)
                full_scaled_surface = temp_surface
            self.scaled_cache[cache_key] = full_scaled_surface
        
        if len(self.scaled_cache) > 10:
            keys_to_remove = list(self.scaled_cache.keys())[:-5]
            for key in keys_to_remove:
                del self.scaled_cache[key]
        
        if len(visible_columns) < num_samples:
            final_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
            final_surface.fill((0, 0, 0, 0))
            visible_columns.sort()
            visible_ranges = []
            current_start = visible_columns[0]
            current_end = visible_columns[0]
            for col in visible_columns[1:]:
                if col - current_end < 0.05:
                    current_end = col
                else:
                    visible_ranges.append((current_start, current_end))
                    current_start = current_end = col
            visible_ranges.append((current_start, current_end))
            
            for start_col, end_col in visible_ranges:
                start_px = int(start_col * scaled_width)
                end_px = int(end_col * scaled_width) + 1
                start_px = max(0, min(scaled_width, start_px))
                end_px = max(start_px, min(scaled_width, end_px))
                if start_px < end_px:
                    visible_portion = full_scaled_surface.subsurface(pygame.Rect(start_px, 0, end_px - start_px, scaled_height))
                    final_surface.blit(visible_portion, (start_px, 0))
        else:
            final_surface = full_scaled_surface
        
        adjusted_screen_y = int(screen_y + pitch_offset)
        sprite_rect = final_surface.get_rect(midbottom=(screen_x, adjusted_screen_y))
        surface.blit(final_surface, sprite_rect)

    def get_distance_to_player(self, player_x, player_y):
        dx = self.x - player_x
        dy = self.y - player_y
        return math.sqrt(dx*dx + dy*dy)

    def draw_3d_sprite(self, surface, player_x, player_y, player_angle, fov_degrees, screen_width, view_height, wall_distances, line_width, pitch_offset=0):
        self.draw_3d_sprite_optimized(surface, player_x, player_y, player_angle, fov_degrees, screen_width, view_height, wall_distances, line_width, pitch_offset)

class Key:
    """纯净的钥匙类 - 静态可拾取物品，支持多关卡不同颜色"""
    
    def __init__(self, maze_width, maze_height, maze_grid, level_index=0):
        # 物理属性
        self.radius = 0.4  # 用于碰撞检测的逻辑半径
        self.width_3d = 0.2  # 3D视图中的宽度
        
        # 根据关卡索引获取颜色
        self.level_index = level_index
        self.color = LEVEL_COLORS[level_index]['key']  # 从关卡颜色配置获取
        
        # 位置和状态
        self.x, self.y = self._place_in_maze(maze_width, maze_height, maze_grid)
        self.collected = False
        self.visible = True
        
        # 2D视图参数
        self.pixel_size = 8  # 2D视图中的像素大小
        self.sprite_2d = self._create_key_sprite_2d()  # 8x8二维矩阵
        
        # 3D视图参数
        self.base_3d_size = KEY_SIZE_3D_BASE
        self.sprite_3d_colors = self._load_key_sprite_3d()  # 加载或生成3D贴图
        
        # 预处理3D贴图表面
        self.original_surface = None
        self.preprocess_sprite()
        
        # 动画相关（简单的浮动效果）
        self.animation_timer = 0
        self.float_speed = 0.003
        self.float_offset = 0
        self.float_amplitude = 1
        
        # 3D渲染缓存
        self.scaled_cache = {}
    
    def _create_key_sprite_2d(self):
        """
        创建8×8的2D钥匙像素画
        设计：钥匙柄为环形（大圆中挖去小圆），钥匙齿有更多细节
        """
        # 8x8网格，1表示钥匙部分，0表示透明
        sprite = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 0, 0, 0],
            [1, 0, 0, 1, 0, 0, 0, 0],
            [1, 0, 0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]  # 钥匙齿部分
        ]
        return sprite
    
    def _load_key_sprite_3d(self):
        """加载钥匙的3D贴图，根据关卡使用不同颜色"""
        try:
            # 尝试加载统一的钥匙图片文件
            image_path = "key_30x30.png"
            
            if not os.path.exists(image_path):
                print(f"钥匙图片文件 '{image_path}' 不存在，使用默认贴图")
                return self._create_key_sprite_3d_colored()
            
            key_image = pygame.image.load(image_path).convert_alpha()
            
            # 确保图片是30x30，如果不是则缩放
            if key_image.get_width() != 30 or key_image.get_height() != 30:
                print(f"警告: 钥匙图片尺寸为{key_image.get_width()}x{key_image.get_height()}，缩放至30x30")
                key_image = pygame.transform.scale(key_image, (30, 30))
            
            # 根据关卡颜色调整图片颜色
            sprite_colors = []
            level_color = LEVEL_COLORS[self.level_index]['key']
            
            for y in range(30):
                row_colors = []
                for x in range(30):
                    pixel_color = key_image.get_at((x, y))
                    alpha = pixel_color[3]
                    
                    # 如果像素不是完全透明，应用关卡颜色
                    if alpha > 0:
                        # 根据原像素的亮度调整颜色强度
                        brightness = sum(pixel_color[:3]) / 3 / 255.0
                        r = int(level_color[0] * brightness)
                        g = int(level_color[1] * brightness)
                        b = int(level_color[2] * brightness)
                        row_colors.append((r, g, b, alpha))
                    else:
                        row_colors.append((0, 0, 0, 0))
                sprite_colors.append(row_colors)
            
            print(f"第{self.level_index+1}关钥匙颜色已应用")
            return sprite_colors
            
        except Exception as e:
            print(f"加载钥匙图片失败: {e}")
            return self._create_key_sprite_3d_colored()
        
    def _create_key_sprite_3d_colored(self):
        """
        根据8×8钥匙贴图等比放大到30×30的3D贴图
        根据关卡使用不同颜色
        """
        # 初始化30x30透明矩阵
        sprite_colors = [[(0, 0, 0, 0) for _ in range(30)] for _ in range(30)]
        
        # 8×8钥匙贴图
        key_8x8 = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 0, 0, 0],
            [1, 0, 0, 1, 0, 0, 0, 0],
            [1, 0, 0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        
        # 等比放大8×8到30×30
        scale_factor = 30 / 8
        
        # 根据关卡索引获取基础颜色
        base_color = LEVEL_COLORS[self.level_index]['key']
        
        # 定义颜色变体
        if self.level_index == 0:  # 第一关：金色系
            dark_color = (205, 165, 0)  # 暗金色
            light_color = (255, 235, 100)  # 亮金色
            highlight = (255, 255, 220)  # 高光色
        elif self.level_index == 1:  # 第二关：橙色系
            dark_color = (205, 135, 0)  # 暗橙色
            light_color = (255, 205, 80)  # 亮橙色
            highlight = (255, 235, 180)  # 高光色
        else:  # 第三关：暗橙色系
            dark_color = (205, 85, 0)  # 更暗的橙色
            light_color = (255, 150, 50)  # 亮暗橙色
            highlight = (255, 200, 150)  # 高光色
        
        # 将8×8图案放大到30×30
        for y in range(30):
            for x in range(30):
                # 计算在8×8图案中的对应位置
                src_x = int(x / scale_factor)
                src_y = int(y / scale_factor)
                
                # 确保在8×8范围内
                if 0 <= src_x < 8 and 0 <= src_y < 8:
                    if key_8x8[src_y][src_x] == 1:
                        # 计算距离钥匙中心的相对距离
                        center_x, center_y = 2.5, 3.5  # 8×8图案中钥匙的中心位置
                        rel_x = (x / scale_factor - center_x) / 3
                        rel_y = (y / scale_factor - center_y) / 4
                        distance = (rel_x**2 + rel_y**2)**0.5
                        
                        # 基础颜色
                        if distance < 0.3:
                            # 钥匙柄的中心区域，稍微暗一些
                            r, g, b = base_color
                            intensity = 0.8
                        elif distance < 0.6:
                            # 钥匙柄的边缘，正常颜色
                            r, g, b = base_color
                            intensity = 1.0
                        else:
                            # 钥匙齿部分，稍暗
                            r, g, b = dark_color
                            intensity = 0.9
                        
                        # 添加一些随机噪声，使颜色更自然
                        noise = random.uniform(-0.1, 0.1)
                        intensity = max(0.7, min(1.0, intensity + noise))
                        
                        # 应用渐变
                        final_r = int(max(0, min(255, r * intensity)))
                        final_g = int(max(0, min(255, g * intensity)))
                        final_b = int(max(0, min(255, b * intensity)))
                        
                        sprite_colors[y][x] = (final_r, final_g, final_b, 255)
        
        # 添加平滑效果：对边缘进行模糊处理
        smoothed_colors = [[(0, 0, 0, 0) for _ in range(30)] for _ in range(30)]
        
        for y in range(30):
            for x in range(30):
                current_pixel = sprite_colors[y][x]
                
                # 如果当前像素是透明的，检查周围是否有不透明像素
                if current_pixel[3] == 0:
                    # 检查3×3区域
                    neighbor_count = 0
                    total_r, total_g, total_b = 0, 0, 0
                    
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < 30 and 0 <= ny < 30:
                                neighbor = sprite_colors[ny][nx]
                                if neighbor[3] > 0:  # 不透明
                                    neighbor_count += 1
                                    total_r += neighbor[0]
                                    total_g += neighbor[1]
                                    total_b += neighbor[2]
                    
                    # 如果有不透明邻居，添加半透明边缘
                    if neighbor_count > 0:
                        avg_r = total_r // neighbor_count
                        avg_g = total_g // neighbor_count
                        avg_b = total_b // neighbor_count
                        # 边缘透明度根据邻居数量决定
                        alpha = min(100, neighbor_count * 25)
                        smoothed_colors[y][x] = (avg_r, avg_g, avg_b, alpha)
                else:
                    # 直接复制不透明像素
                    smoothed_colors[y][x] = current_pixel
        
        # 添加高光效果
        # 在钥匙柄的右上角添加高光
        for y in range(8, 14):
            for x in range(8, 14):
                if sprite_colors[y][x][3] > 0:  # 不透明像素
                    r, g, b, a = smoothed_colors[y][x]
                    # 根据位置添加高光
                    if (x-8)*(x-8) + (y-8)*(y-8) < 3:  # 圆形高光区域
                        highlight_intensity = 0.3
                        new_r = int(min(255, r + 50 * highlight_intensity))
                        new_g = int(min(255, g + 50 * highlight_intensity))
                        new_b = int(min(255, b + 20 * highlight_intensity))
                        smoothed_colors[y][x] = (new_r, new_g, new_b, a)
        
        # 在钥匙齿的突出部分添加高光
        for y in range(15, 18):
            for x in range(18, 24):
                if sprite_colors[y][x][3] > 0:
                    r, g, b, a = smoothed_colors[y][x]
                    if x > 20:  # 钥匙齿末端
                        highlight_intensity = 0.2
                        new_r = int(min(255, r + 30 * highlight_intensity))
                        new_g = int(min(255, g + 30 * highlight_intensity))
                        new_b = int(min(255, b + 10 * highlight_intensity))
                        smoothed_colors[y][x] = (new_r, new_g, new_b, a)
        
        return smoothed_colors
    
    def preprocess_sprite(self):
        """预处理3D贴图，创建Pygame表面"""
        self.original_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        
        for y in range(30):
            for x in range(30):
                pixel_color = self.sprite_3d_colors[y][x]
                if len(pixel_color) == 4 and pixel_color[3] > 0:
                    # 确保颜色值在有效范围内
                    r = max(0, min(255, pixel_color[0]))
                    g = max(0, min(255, pixel_color[1]))
                    b = max(0, min(255, pixel_color[2]))
                    a = max(0, min(255, pixel_color[3]))
                    self.original_surface.set_at((x, y), (r, g, b, a))
    
    def _place_in_maze(self, maze_width, maze_height, maze_grid):
        """在迷宫中随机找一个可通行的位置放置钥匙"""
        available_positions = []
        
        for x in range(maze_width):
            for y in range(maze_height):
                if maze_grid[x, y] == 0:  # 是路径
                    # 避免放在出口或起始点附近
                    center_x, center_y = maze_width // 2, maze_height // 2
                    if abs(x - center_x) > 2 or abs(y - center_y) > 2:
                        available_positions.append((x + 0.5, y + 0.5))
        
        if available_positions:
            return random.choice(available_positions)
        else:
            # 备用位置
            return (maze_width // 2 + 2.5, maze_height // 2 + 2.5)
    
    def update(self, dt, player_x, player_y):
        """更新钥匙状态（动画和拾取检测在Player类中进行）"""
        if self.collected:
            self.visible = False
            return
            
        # 更新浮动动画
        self.animation_timer += dt * 1000
        self.float_offset = math.sin(self.animation_timer * self.float_speed) * self.float_amplitude
    
    def get_distance_to_player(self, player_x, player_y):
        """计算钥匙到玩家的距离"""
        dx = self.x - player_x
        dy = self.y - player_y
        return math.sqrt(dx*dx + dy*dy)
    
    def is_near_player(self, player_x, player_y):
        """检查玩家是否在拾取距离内"""
        if self.collected:
            return False
        distance = self.get_distance_to_player(player_x, player_y)
        return distance < KEY_PICKUP_DISTANCE
    
    def collect(self):
        """拾取钥匙"""
        if not self.collected:
            self.collected = True
            self.visible = False
            # 播放拾取音效
            audio_manager.play_sound('key')
            return True
        return False
    
    def get_relative_position(self, player_x, player_y, player_angle):
        """获取钥匙相对于玩家的位置（距离和角度）"""
        dx = self.x - player_x
        dy = self.y - player_y
        
        distance = math.sqrt(dx*dx + dy*dy)
        angle_to_key = math.atan2(dy, dx)
        relative_angle = angle_to_key - player_angle
        
        # 规范化角度到[-π, π]
        while relative_angle > math.pi:
            relative_angle -= 2 * math.pi
        while relative_angle < -math.pi:
            relative_angle += 2 * math.pi
            
        return distance, relative_angle
    
    def get_screen_position(self, player_x, player_y, player_angle, fov_degrees, screen_width, view_height):
        """
        计算钥匙在屏幕上的位置
        返回：(screen_x, screen_y, size, visible, alpha, screen_width_projection)
        """
        if not self.visible or self.collected:
            return 0, 0, 0, False, 0, 0
        
        distance, relative_angle = self.get_relative_position(player_x, player_y, player_angle)
        
        # 将相对角度转换为屏幕x坐标
        fov_rad = math.radians(fov_degrees)
        
        # 检查是否在视野内
        if abs(relative_angle) > fov_rad / 2:
            return 0, 0, 0, False, 0, 0
        
        # 计算屏幕x坐标（0在最左边，1在最右边）
        screen_x_ratio = 0.5 + (relative_angle / fov_rad)
        screen_x = screen_x_ratio * screen_width
        
        # 根据距离计算钥匙大小（透视投影）
        size = int(self.base_3d_size / (distance + 0.5))
        size = max(20, min(500, size))  # 限制大小范围
        
        # 计算钥匙底部在地板上的位置（加上浮动偏移）
        eye_height = view_height // 2
        projection_factor = view_height * 0.5
        # 添加浮动效果：钥匙在离地0.2单位高度浮动
        float_height = 0.2 + self.float_offset * 0.05
        floor_y = eye_height + (projection_factor / distance) - (float_height * projection_factor / distance)
        
        screen_y = min(view_height, int(floor_y))
        
        # 根据距离设置透明度
        alpha = max(150, 255 - int(distance * 10))
        
        # 计算钥匙宽度在屏幕上的投影（像素）
        screen_width_projection = (self.width_3d / (distance + 0.5)) * (screen_width / math.tan(fov_rad / 2))
        screen_width_projection = int(max(8, screen_width_projection))
        
        return screen_x, screen_y, size, True, alpha, screen_width_projection
    
    def draw_2d(self, surface, offset_x, offset_y, cell_size):
        """在2D视图中绘制钥匙（使用8×8像素画）"""
        if not self.visible or self.collected:
            return
            
        key_screen_x = offset_x + self.x * cell_size
        key_screen_y = offset_y + self.y * cell_size
        
        # 创建钥匙表面（放大显示）
        scale_factor = 3  # 放大3倍以便在2D视图中清晰显示
        key_surface = pygame.Surface((self.pixel_size * scale_factor, self.pixel_size * scale_factor), pygame.SRCALPHA)
        
        # 绘制钥匙像素画
        for py in range(self.pixel_size):
            for px in range(self.pixel_size):
                if self.sprite_2d[py][px] == 1:
                    # 绘制放大后的像素
                    rect = pygame.Rect(px * scale_factor, py * scale_factor, scale_factor, scale_factor)
                    pygame.draw.rect(key_surface, self.color, rect)
        
        # 将钥匙绘制到屏幕
        key_rect = key_surface.get_rect(center=(key_screen_x, key_screen_y))
        surface.blit(key_surface, key_rect)
        
        # 绘制钥匙发光效果
        glow_radius = (self.pixel_size * scale_factor) // 2 + 2
        for i in range(2):
            glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
            alpha = 30 - i * 10
            pygame.draw.circle(glow_surface, (*self.color[:3], alpha), 
                             (glow_radius, glow_radius), glow_radius - i)
            surface.blit(glow_surface, (key_screen_x - glow_radius, key_screen_y - glow_radius))

    def draw_3d_sprite(self, surface, player_x, player_y, player_angle, fov_degrees, screen_width, view_height, wall_distances, line_width, pitch_offset=0):
        """
        在3D视图中绘制钥匙精灵
        使用独立的绘制逻辑，与幽灵完全分离
        """
        # 获取钥匙的屏幕位置、大小、宽度和可见性
        screen_x, screen_y, key_size, key_visible, alpha, key_screen_width = self.get_screen_position(
            player_x, player_y, player_angle, fov_degrees, screen_width, view_height
        )
        
        if not key_visible or key_size < 10 or self.collected:
            return

        # 计算钥匙在屏幕上的水平绘制范围
        key_left_screen = screen_x - key_screen_width // 2
        key_right_screen = screen_x + key_screen_width // 2
        key_left_screen = max(0, min(screen_width, key_left_screen))
        key_right_screen = max(0, min(screen_width, key_right_screen))

        # 计算钥匙到玩家的真实距离
        key_distance = self.get_distance_to_player(player_x, player_y)

        # 简单的遮挡检测：检查钥匙中心点是否被墙挡住
        center_screen_x = screen_x
        ray_idx = int(center_screen_x / line_width)
        ray_idx = max(0, min(len(wall_distances) - 1, ray_idx))
        
        wall_dist_at_center = wall_distances[ray_idx] if ray_idx < len(wall_distances) else MAX_VIEW_DISTANCE
        
        # 如果钥匙距离大于墙壁距离，则被遮挡
        if key_distance > wall_dist_at_center:
            return

        # 创建缩放后的钥匙表面
        scaled_width = int(key_screen_width)
        scaled_height = int(key_size)
        
        # 使用缓存的缩放纹理
        cache_key = (scaled_width, scaled_height, alpha)
        if cache_key in self.scaled_cache:
            scaled_surface = self.scaled_cache[cache_key]
        else:
            # 使用pygame内置的缩放函数
            scaled_surface = pygame.transform.scale(self.original_surface, (scaled_width, scaled_height))
            
            # 应用距离透明度
            if alpha < 255:
                temp_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
                temp_surface.blit(scaled_surface, (0, 0))
                temp_surface.set_alpha(alpha)
                scaled_surface = temp_surface
            
            # 缓存结果
            if len(self.scaled_cache) < 5:  # 限制缓存大小
                self.scaled_cache[cache_key] = scaled_surface
        
        # 清理过期的缓存
        if len(self.scaled_cache) > 10:
            keys_to_remove = list(self.scaled_cache.keys())[:-5]
            for key in keys_to_remove:
                del self.scaled_cache[key]
        
        # 绘制到屏幕上
        adjusted_screen_y = int(screen_y + pitch_offset)
        sprite_rect = scaled_surface.get_rect(midbottom=(screen_x, adjusted_screen_y))
        surface.blit(scaled_surface, sprite_rect)
        
class Heart:
    """生命值道具类 - 可拾取的爱心，增加玩家生命值"""
    
    def __init__(self, maze_width, maze_height, maze_grid, level_index=0):
        # 物理属性
        self.radius = 0.4  # 用于碰撞检测的逻辑半径
        self.width_3d = 0.15  # 3D视图中的宽度
        
        # 根据关卡索引获取颜色（爱心颜色保持不变）
        self.color = LEVEL_COLORS[level_index]['heart']
        
        # 位置和状态
        self.x, self.y = self._place_in_maze(maze_width, maze_height, maze_grid)
        self.collected = False
        self.visible = True
        
        # 2D视图参数
        self.pixel_size = 8  # 2D视图中的像素大小
        self.sprite_2d = self._create_heart_sprite_2d()  # 8x8二维矩阵
        
        # 3D视图参数
        self.base_3d_size = HEART_SIZE_3D_BASE
        self.sprite_3d_colors = self._load_heart_sprite_3d()  # 加载或生成3D贴图
        
        # 预处理3D贴图表面
        self.original_surface = None
        self.preprocess_sprite()
        
        # 动画相关（简单的浮动和脉动效果）
        self.animation_timer = 0
        self.float_speed = 0.004
        self.float_offset = 0
        self.float_amplitude = 1
        self.pulse_timer = 0
        self.pulse_speed = 0.005
        self.pulse_scale = 1.0
        
        # 3D渲染缓存
        self.scaled_cache = {}
    
    def _create_heart_sprite_2d(self):
        """
        创建8×8的2D爱心像素画
        设计：经典的爱心形状
        """
        # 8x8网格，1表示爱心部分，0表示透明
        sprite = [
            [0, 1, 1, 0, 0, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        return sprite
    
    def _load_heart_sprite_3d(self):
        """加载爱心的3D贴图，优先读取文件，否则生成默认图案"""
        try:
            image_path = "heart_30x30.png"
            
            if not os.path.exists(image_path):
                print(f"爱心图片文件 '{image_path}' 不存在，使用默认贴图")
                return self._create_heart_sprite_3d_colored()
            
            heart_image = pygame.image.load(image_path).convert_alpha()
            
            # 确保图片是30x30，如果不是则缩放
            if heart_image.get_width() != 30 or heart_image.get_height() != 30:
                print(f"警告: 爱心图片尺寸为{heart_image.get_width()}x{heart_image.get_height()}，缩放至30x30")
                heart_image = pygame.transform.scale(heart_image, (30, 30))
            
            sprite_colors = []
            
            for y in range(30):
                row_colors = []
                for x in range(30):
                    pixel_color = heart_image.get_at((x, y))
                    # 确保颜色值在0-255范围内
                    r = max(0, min(255, pixel_color[0]))
                    g = max(0, min(255, pixel_color[1]))
                    b = max(0, min(255, pixel_color[2]))
                    a = max(0, min(255, pixel_color[3]))
                    row_colors.append((r, g, b, a))
                sprite_colors.append(row_colors)
            
            print("成功加载爱心图片")
            return sprite_colors
            
        except Exception as e:
            print(f"加载爱心图片失败: {e}")
            return self._create_heart_sprite_3d_colored()
    
    def _create_heart_sprite_3d_colored(self):
        """
        根据8×8爱心贴图等比放大到30×30的3D贴图
        生成带有红色渐变的爱心图案
        """
        # 初始化30x30透明矩阵
        sprite_colors = [[(0, 0, 0, 0) for _ in range(30)] for _ in range(30)]
        
        # 8×8爱心贴图
        heart_8x8 = [
            [0, 1, 1, 0, 0, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        
        # 等比放大8×8到30×30
        scale_factor = 30 / 8
        
        # 定义颜色（爱心颜色保持不变）
        base_red = self.color  # 使用初始化时设置的颜色
        dark_red = (220, 60, 60)      # 暗红色
        light_red = (255, 150, 150)   # 亮红色
        highlight = (255, 200, 200)   # 高光色
        
        # 将8×8图案放大到30×30
        for y in range(30):
            for x in range(30):
                # 计算在8×8图案中的对应位置
                src_x = int(x / scale_factor)
                src_y = int(y / scale_factor)
                
                # 确保在8×8范围内
                if 0 <= src_x < 8 and 0 <= src_y < 8:
                    if heart_8x8[src_y][src_x] == 1:
                        # 计算距离爱心中心的相对距离
                        center_x, center_y = 3.5, 3.0  # 8×8图案中爱心的中心位置
                        rel_x = (x / scale_factor - center_x) / 3
                        rel_y = (y / scale_factor - center_y) / 3
                        distance = (rel_x**2 + rel_y**2)**0.5
                        
                        # 基础颜色
                        if distance < 0.3:
                            # 爱心的中心区域，较亮
                            r, g, b = light_red
                            intensity = 1.0
                        elif distance < 0.6:
                            # 爱心的中间区域，正常红色
                            r, g, b = base_red
                            intensity = 0.9
                        else:
                            # 爱心的边缘，稍暗
                            r, g, b = dark_red
                            intensity = 0.8
                        
                        # 添加一些随机噪声，使颜色更自然
                        noise = random.uniform(-0.05, 0.05)
                        intensity = max(0.7, min(1.0, intensity + noise))
                        
                        # 应用渐变
                        final_r = int(max(0, min(255, r * intensity)))
                        final_g = int(max(0, min(255, g * intensity)))
                        final_b = int(max(0, min(255, b * intensity)))
                        
                        sprite_colors[y][x] = (final_r, final_g, final_b, 255)
        
        # 添加平滑效果：对边缘进行模糊处理
        smoothed_colors = [[(0, 0, 0, 0) for _ in range(30)] for _ in range(30)]
        
        for y in range(30):
            for x in range(30):
                current_pixel = sprite_colors[y][x]
                
                # 如果当前像素是透明的，检查周围是否有不透明像素
                if current_pixel[3] == 0:
                    # 检查3×3区域
                    neighbor_count = 0
                    total_r, total_g, total_b = 0, 0, 0
                    
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < 30 and 0 <= ny < 30:
                                neighbor = sprite_colors[ny][nx]
                                if neighbor[3] > 0:  # 不透明
                                    neighbor_count += 1
                                    total_r += neighbor[0]
                                    total_g += neighbor[1]
                                    total_b += neighbor[2]
                    
                    # 如果有不透明邻居，添加半透明边缘
                    if neighbor_count > 0:
                        avg_r = total_r // neighbor_count
                        avg_g = total_g // neighbor_count
                        avg_b = total_b // neighbor_count
                        alpha = min(80, neighbor_count * 20)
                        smoothed_colors[y][x] = (avg_r, avg_g, avg_b, alpha)
                else:
                    # 直接复制不透明像素
                    smoothed_colors[y][x] = current_pixel
        
        # 添加高光效果
        # 在爱心的左上角添加高光
        for y in range(10, 16):
            for x in range(10, 16):
                if sprite_colors[y][x][3] > 0:  # 不透明像素
                    r, g, b, a = smoothed_colors[y][x]
                    # 根据位置添加高光（左上角区域）
                    if (x-10)*(x-10) + (y-10)*(y-10) < 4:  # 圆形高光区域
                        highlight_intensity = 0.4
                        new_r = int(min(255, r + 60 * highlight_intensity))
                        new_g = int(min(255, g + 40 * highlight_intensity))
                        new_b = int(min(255, b + 40 * highlight_intensity))
                        smoothed_colors[y][x] = (new_r, new_g, new_b, a)
        
        return smoothed_colors
    
    def preprocess_sprite(self):
        """预处理3D贴图，创建Pygame表面"""
        self.original_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        
        for y in range(30):
            for x in range(30):
                pixel_color = self.sprite_3d_colors[y][x]
                if len(pixel_color) == 4 and pixel_color[3] > 0:
                    # 确保颜色值在有效范围内
                    r = max(0, min(255, pixel_color[0]))
                    g = max(0, min(255, pixel_color[1]))
                    b = max(0, min(255, pixel_color[2]))
                    a = max(0, min(255, pixel_color[3]))
                    self.original_surface.set_at((x, y), (r, g, b, a))
    
    def _place_in_maze(self, maze_width, maze_height, maze_grid):
        """在迷宫中随机找一个可通行的位置放置爱心"""
        available_positions = []
        
        for x in range(maze_width):
            for y in range(maze_height):
                if maze_grid[x, y] == 0:  # 是路径
                    # 避免放在出口、起始点或钥匙附近
                    center_x, center_y = maze_width // 2, maze_height // 2
                    if abs(x - center_x) > 3 or abs(y - center_y) > 3:
                        available_positions.append((x + 0.5, y + 0.5))
        
        if available_positions:
            return random.choice(available_positions)
        else:
            # 备用位置
            return (maze_width // 2 + 3.5, maze_height // 2 + 3.5)
    
    def update(self, dt, player_x, player_y):
        """更新爱心状态（动画和拾取检测在Player类中进行）"""
        if self.collected:
            self.visible = False
            return
            
        # 更新浮动动画
        self.animation_timer += dt * 1000
        self.float_offset = math.sin(self.animation_timer * self.float_speed) * self.float_amplitude
        
        # 更新脉动动画
        self.pulse_timer += dt * 1000
        self.pulse_scale = 1.0 + 0.1 * math.sin(self.pulse_timer * self.pulse_speed)
    
    def get_distance_to_player(self, player_x, player_y):
        """计算爱心到玩家的距离"""
        dx = self.x - player_x
        dy = self.y - player_y
        return math.sqrt(dx*dx + dy*dy)
    
    def is_near_player(self, player_x, player_y):
        """检查玩家是否在拾取距离内"""
        if self.collected:
            return False
        distance = self.get_distance_to_player(player_x, player_y)
        return distance < HEART_PICKUP_DISTANCE
    
    def collect(self):
        """拾取爱心"""
        if not self.collected:
            self.collected = True
            self.visible = False
            # 播放拾取音效
            audio_manager.play_sound('heart')
            return True
        return False
    
    def get_relative_position(self, player_x, player_y, player_angle):
        """获取爱心相对于玩家的位置（距离和角度）"""
        dx = self.x - player_x
        dy = self.y - player_y
        
        distance = math.sqrt(dx*dx + dy*dy)
        angle_to_heart = math.atan2(dy, dx)
        relative_angle = angle_to_heart - player_angle
        
        # 规范化角度到[-π, π]
        while relative_angle > math.pi:
            relative_angle -= 2 * math.pi
        while relative_angle < -math.pi:
            relative_angle += 2 * math.pi
            
        return distance, relative_angle
    
    def get_screen_position(self, player_x, player_y, player_angle, fov_degrees, screen_width, view_height):
        """
        计算爱心在屏幕上的位置
        返回：(screen_x, screen_y, size, visible, alpha, screen_width_projection)
        """
        if not self.visible or self.collected:
            return 0, 0, 0, False, 0, 0
        
        distance, relative_angle = self.get_relative_position(player_x, player_y, player_angle)
        
        # 将相对角度转换为屏幕x坐标
        fov_rad = math.radians(fov_degrees)
        
        # 检查是否在视野内
        if abs(relative_angle) > fov_rad / 2:
            return 0, 0, 0, False, 0, 0
        
        # 计算屏幕x坐标（0在最左边，1在最右边）
        screen_x_ratio = 0.5 + (relative_angle / fov_rad)
        screen_x = screen_x_ratio * screen_width
        
        # 根据距离计算爱心大小（透视投影），并应用脉动效果
        base_size = int(self.base_3d_size / (distance + 0.5))
        size = int(base_size * self.pulse_scale)
        size = max(20, min(400, size))  # 限制大小范围
        
        # 计算爱心底部在地板上的位置（加上浮动偏移）
        eye_height = view_height // 2
        projection_factor = view_height * 0.5
        # 添加浮动效果：爱心在离地0.2单位高度浮动
        float_height = 0.2 + self.float_offset * 0.05
        floor_y = eye_height + (projection_factor / distance) - (float_height * projection_factor / distance)
        
        screen_y = min(view_height, int(floor_y))
        
        # 根据距离设置透明度
        alpha = max(150, 255 - int(distance * 10))
        
        # 计算爱心宽度在屏幕上的投影（像素），并应用脉动效果
        base_width_projection = (self.width_3d / (distance + 0.5)) * (screen_width / math.tan(fov_rad / 2))
        screen_width_projection = int(base_width_projection * self.pulse_scale)
        screen_width_projection = int(max(8, screen_width_projection))
        
        return screen_x, screen_y, size, True, alpha, screen_width_projection
    
    def draw_2d(self, surface, offset_x, offset_y, cell_size):
        """在2D视图中绘制爱心（使用8×8像素画）"""
        if not self.visible or self.collected:
            return
            
        heart_screen_x = offset_x + self.x * cell_size
        heart_screen_y = offset_y + self.y * cell_size
        
        # 创建爱心表面（放大显示）
        scale_factor = 3  # 放大3倍以便在2D视图中清晰显示
        heart_surface = pygame.Surface((self.pixel_size * scale_factor, self.pixel_size * scale_factor), pygame.SRCALPHA)
        
        # 绘制爱心像素画
        for py in range(self.pixel_size):
            for px in range(self.pixel_size):
                if self.sprite_2d[py][px] == 1:
                    # 绘制放大后的像素
                    rect = pygame.Rect(px * scale_factor, py * scale_factor, scale_factor, scale_factor)
                    pygame.draw.rect(heart_surface, self.color, rect)
        
        # 将爱心绘制到屏幕
        heart_rect = heart_surface.get_rect(center=(heart_screen_x, heart_screen_y))
        surface.blit(heart_surface, heart_rect)
        
        # 绘制爱心发光效果
        glow_radius = (self.pixel_size * scale_factor) // 2 + 2
        for i in range(2):
            glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
            alpha = 40 - i * 15
            pygame.draw.circle(glow_surface, (*self.color[:3], alpha), 
                             (glow_radius, glow_radius), glow_radius - i)
            surface.blit(glow_surface, (heart_screen_x - glow_radius, heart_screen_y - glow_radius))
    
    def draw_3d_sprite(self, surface, player_x, player_y, player_angle, fov_degrees, screen_width, view_height, wall_distances, line_width, pitch_offset=0):
        """
        在3D视图中绘制爱心精灵
        使用独立的绘制逻辑，与钥匙和幽灵完全分离
        """
        # 获取爱心的屏幕位置、大小、宽度和可见性
        screen_x, screen_y, heart_size, heart_visible, alpha, heart_screen_width = self.get_screen_position(
            player_x, player_y, player_angle, fov_degrees, screen_width, view_height
        )
        
        if not heart_visible or heart_size < 10 or self.collected:
            return

        # 计算爱心在屏幕上的水平绘制范围
        heart_left_screen = screen_x - heart_screen_width // 2
        heart_right_screen = screen_x + heart_screen_width // 2
        heart_left_screen = max(0, min(screen_width, heart_left_screen))
        heart_right_screen = max(0, min(screen_width, heart_right_screen))

        # 计算爱心到玩家的真实距离
        heart_distance = self.get_distance_to_player(player_x, player_y)

        # 简单的遮挡检测：检查爱心中心点是否被墙挡住
        center_screen_x = screen_x
        ray_idx = int(center_screen_x / line_width)
        ray_idx = max(0, min(len(wall_distances) - 1, ray_idx))
        
        wall_dist_at_center = wall_distances[ray_idx] if ray_idx < len(wall_distances) else MAX_VIEW_DISTANCE
        
        # 如果爱心距离大于墙壁距离，则被遮挡
        if heart_distance > wall_dist_at_center:
            return

        # 创建缩放后的爱心表面
        scaled_width = int(heart_screen_width)
        scaled_height = int(heart_size)
        
        # 使用缓存的缩放纹理
        cache_key = (scaled_width, scaled_height, alpha, int(self.pulse_scale * 10))
        if cache_key in self.scaled_cache:
            scaled_surface = self.scaled_cache[cache_key]
        else:
            # 使用pygame内置的缩放函数
            scaled_surface = pygame.transform.scale(self.original_surface, (scaled_width, scaled_height))
            
            # 应用距离透明度
            if alpha < 255:
                temp_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
                temp_surface.blit(scaled_surface, (0, 0))
                temp_surface.set_alpha(alpha)
                scaled_surface = temp_surface
            
            # 缓存结果
            if len(self.scaled_cache) < 5:  # 限制缓存大小
                self.scaled_cache[cache_key] = scaled_surface
        
        # 清理过期的缓存
        if len(self.scaled_cache) > 10:
            keys_to_remove = list(self.scaled_cache.keys())[:-5]
            for key in keys_to_remove:
                del self.scaled_cache[key]
        
        # 绘制到屏幕上
        adjusted_screen_y = int(screen_y + pitch_offset)
        sprite_rect = scaled_surface.get_rect(midbottom=(screen_x, adjusted_screen_y))
        surface.blit(scaled_surface, sprite_rect)
        
        # 绘制爱心的脉动发光效果
        if alpha > 150 and self.pulse_scale > 1.05:
            pulse_alpha = int((self.pulse_scale - 1.0) * 100)
            glow_surface = pygame.Surface((scaled_width + 6, scaled_height + 6), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surface, (255, 150, 150, pulse_alpha), 
                               glow_surface.get_rect())
            glow_rect = glow_surface.get_rect(center=(screen_x, adjusted_screen_y - scaled_height // 4))
            surface.blit(glow_surface, glow_rect)

class Map:
    """地图道具类 - 拾取后在右上角显示2D缩略图10秒"""
    
    def __init__(self, maze_width, maze_height, maze_grid, level_index=0):
        # 物理属性
        self.radius = 0.4  # 用于碰撞检测的逻辑半径
        self.width_3d = 0.1  # 3D视图中的宽度
        
        # 根据关卡索引获取颜色
        self.level_index = level_index
        self.color = LEVEL_COLORS[level_index]['map']  # 从关卡颜色配置获取
        
        # 位置和状态
        self.x, self.y = self._place_in_maze(maze_width, maze_height, maze_grid)
        self.collected = False
        self.visible = True
        
        # 2D视图参数
        self.pixel_size = 8  # 2D视图中的像素大小
        self.sprite_2d = self._create_map_sprite_2d()  # 8x8二维矩阵
        
        # 3D视图参数
        self.base_3d_size = MAP_SIZE_3D_BASE
        self.sprite_3d_colors = self._load_map_sprite_3d()  # 加载或生成3D贴图
        
        # 预处理3D贴图表面
        self.original_surface = None
        self.preprocess_sprite()
        
        # 动画相关（旋转效果）
        self.animation_timer = 0
        self.rotation_speed = 0.001
        self.rotation_angle = 0
        
        # 3D渲染缓存
        self.scaled_cache = {}
        
        print(f"第{level_index+1}关地图道具已生成在位置 ({self.x:.1f}, {self.y:.1f})")
    
    def _create_map_sprite_2d(self):
        """
        创建8×8的2D地图像素画
        设计：卷轴地图样式
        """
        # 8x8网格，1表示地图部分，0表示透明
        sprite = [
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 0, 0, 1, 1, 0],
            [1, 1, 0, 1, 1, 0, 1, 1],
            [1, 1, 0, 1, 1, 0, 1, 1],
            [0, 1, 1, 0, 0, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0]
        ]
        return sprite
    
    def _load_map_sprite_3d(self):
        """加载地图的3D贴图，根据关卡使用不同颜色"""
        try:
            # 尝试加载统一的地图图片文件
            image_path = "map_30x30.png"
            
            if not os.path.exists(image_path):
                print(f"地图图片文件 '{image_path}' 不存在，使用默认贴图")
                return self._create_map_sprite_3d_colored()
            
            map_image = pygame.image.load(image_path).convert_alpha()
            
            # 确保图片是30x30，如果不是则缩放
            if map_image.get_width() != 30 or map_image.get_height() != 30:
                print(f"警告: 地图图片尺寸为{map_image.get_width()}x{map_image.get_height()}，缩放至30x30")
                map_image = pygame.transform.scale(map_image, (30, 30))
            
            # 根据关卡颜色调整图片颜色
            sprite_colors = []
            level_color = LEVEL_COLORS[self.level_index]['map']
            
            for y in range(30):
                row_colors = []
                for x in range(30):
                    pixel_color = map_image.get_at((x, y))
                    alpha = pixel_color[3]
                    
                    # 如果像素不是完全透明，应用关卡颜色
                    if alpha > 0:
                        # 根据原像素的亮度调整颜色强度
                        brightness = sum(pixel_color[:3]) / 3 / 255.0
                        r = int(level_color[0] * brightness)
                        g = int(level_color[1] * brightness)
                        b = int(level_color[2] * brightness)
                        row_colors.append((r, g, b, alpha))
                    else:
                        row_colors.append((0, 0, 0, 0))
                sprite_colors.append(row_colors)
            
            print(f"第{self.level_index+1}关地图颜色已应用")
            return sprite_colors
            
        except Exception as e:
            print(f"加载地图图片失败: {e}")
            return self._create_map_sprite_3d_colored()
        
    def _create_map_sprite_3d_colored(self):
        """
        根据8×8地图贴图等比放大到30×30的3D贴图
        根据关卡使用不同颜色
        """
        # 初始化30x30透明矩阵
        sprite_colors = [[(0, 0, 0, 0) for _ in range(30)] for _ in range(30)]
        
        # 8×8地图贴图
        map_8x8 = [
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 0, 0, 1, 1, 0],
            [1, 1, 0, 1, 1, 0, 1, 1],
            [1, 1, 0, 1, 1, 0, 1, 1],
            [0, 1, 1, 0, 0, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0]
        ]
        
        # 等比放大8×8到30×30
        scale_factor = 30 / 8
        
        # 根据关卡索引获取基础颜色
        base_color = LEVEL_COLORS[self.level_index]['map']
        
        # 定义颜色变体
        if self.level_index == 0:  # 第一关：亮蓝色系
            dark_color = (30, 150, 220)  # 暗蓝色
            light_color = (100, 230, 255)  # 亮蓝色
            highlight = (180, 240, 255)  # 高光色
        elif self.level_index == 1:  # 第二关：中蓝色系
            dark_color = (20, 130, 200)  # 暗蓝色
            light_color = (80, 200, 240)  # 亮蓝色
            highlight = (150, 220, 255)  # 高光色
        else:  # 第三关：深蓝色系
            dark_color = (10, 110, 180)  # 更暗的蓝色
            light_color = (60, 170, 230)  # 亮深蓝色
            highlight = (120, 200, 245)  # 高光色
        
        # 将8×8图案放大到30×30
        for y in range(30):
            for x in range(30):
                # 计算在8×8图案中的对应位置
                src_x = int(x / scale_factor)
                src_y = int(y / scale_factor)
                
                # 确保在8×8范围内
                if 0 <= src_x < 8 and 0 <= src_y < 8:
                    if map_8x8[src_y][src_x] == 1:
                        # 计算距离地图中心的相对距离
                        center_x, center_y = 3.5, 3.5  # 8×8图案中地图的中心位置
                        rel_x = (x / scale_factor - center_x) / 3
                        rel_y = (y / scale_factor - center_y) / 3
                        distance = (rel_x**2 + rel_y**2)**0.5
                        
                        # 基础颜色
                        if distance < 0.3:
                            # 地图的中心区域，较亮
                            r, g, b = light_color
                            intensity = 1.0
                        elif distance < 0.6:
                            # 地图的中间区域，正常颜色
                            r, g, b = base_color
                            intensity = 0.9
                        else:
                            # 地图的边缘，稍暗
                            r, g, b = dark_color
                            intensity = 0.8
                        
                        # 添加一些随机噪声，使颜色更自然
                        noise = random.uniform(-0.05, 0.05)
                        intensity = max(0.7, min(1.0, intensity + noise))
                        
                        # 应用渐变
                        final_r = int(max(0, min(255, r * intensity)))
                        final_g = int(max(0, min(255, g * intensity)))
                        final_b = int(max(0, min(255, b * intensity)))
                        
                        sprite_colors[y][x] = (final_r, final_g, final_b, 255)
        
        # 添加平滑效果：对边缘进行模糊处理
        smoothed_colors = [[(0, 0, 0, 0) for _ in range(30)] for _ in range(30)]
        
        for y in range(30):
            for x in range(30):
                current_pixel = sprite_colors[y][x]
                
                # 如果当前像素是透明的，检查周围是否有不透明像素
                if current_pixel[3] == 0:
                    # 检查3×3区域
                    neighbor_count = 0
                    total_r, total_g, total_b = 0, 0, 0
                    
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < 30 and 0 <= ny < 30:
                                neighbor = sprite_colors[ny][nx]
                                if neighbor[3] > 0:  # 不透明
                                    neighbor_count += 1
                                    total_r += neighbor[0]
                                    total_g += neighbor[1]
                                    total_b += neighbor[2]
                    
                    # 如果有不透明邻居，添加半透明边缘
                    if neighbor_count > 0:
                        avg_r = total_r // neighbor_count
                        avg_g = total_g // neighbor_count
                        avg_b = total_b // neighbor_count
                        # 边缘透明度根据邻居数量决定
                        alpha = min(100, neighbor_count * 25)
                        smoothed_colors[y][x] = (avg_r, avg_g, avg_b, alpha)
                else:
                    # 直接复制不透明像素
                    smoothed_colors[y][x] = current_pixel
        
        # 添加高光效果
        # 在地图的中心添加高光，模拟卷轴的凸起
        for y in range(12, 18):
            for x in range(12, 18):
                if sprite_colors[y][x][3] > 0:  # 不透明像素
                    r, g, b, a = smoothed_colors[y][x]
                    # 中心区域添加更多高光
                    if (x-15)*(x-15) + (y-15)*(y-15) < 4:  # 圆形高光区域
                        highlight_intensity = 0.5
                        new_r = int(min(255, r + 40 * highlight_intensity))
                        new_g = int(min(255, g + 60 * highlight_intensity))
                        new_b = int(min(255, b + 70 * highlight_intensity))
                        smoothed_colors[y][x] = (new_r, new_g, new_b, a)
        
        return smoothed_colors
    
    def preprocess_sprite(self):
        """预处理3D贴图，创建Pygame表面"""
        self.original_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        
        for y in range(30):
            for x in range(30):
                pixel_color = self.sprite_3d_colors[y][x]
                if len(pixel_color) == 4 and pixel_color[3] > 0:
                    # 确保颜色值在有效范围内
                    r = max(0, min(255, pixel_color[0]))
                    g = max(0, min(255, pixel_color[1]))
                    b = max(0, min(255, pixel_color[2]))
                    a = max(0, min(255, pixel_color[3]))
                    self.original_surface.set_at((x, y), (r, g, b, a))
    
    def _place_in_maze(self, maze_width, maze_height, maze_grid):
        """在迷宫中随机找一个可通行的位置放置地图"""
        available_positions = []
        
        for x in range(maze_width):
            for y in range(maze_height):
                if maze_grid[x, y] == 0:  # 是路径
                    # 避免放在出口、起始点或钥匙附近
                    center_x, center_y = maze_width // 2, maze_height // 2
                    if abs(x - center_x) > 4 or abs(y - center_y) > 4:
                        available_positions.append((x + 0.5, y + 0.5))
        
        if available_positions:
            return random.choice(available_positions)
        else:
            # 备用位置
            return (maze_width // 2 + 4.5, maze_height // 2 + 4.5)
    
    def update(self, dt, player_x, player_y):
        """更新地图状态（动画和拾取检测在Player类中进行）"""
        if self.collected:
            self.visible = False
            return
            
        # 更新旋转动画
        self.animation_timer += dt * 1000
        self.rotation_angle = (self.animation_timer * self.rotation_speed) % (2 * math.pi)
    
    def get_distance_to_player(self, player_x, player_y):
        """计算地图到玩家的距离"""
        dx = self.x - player_x
        dy = self.y - player_y
        return math.sqrt(dx*dx + dy*dy)
    
    def is_near_player(self, player_x, player_y):
        """检查玩家是否在拾取距离内"""
        if self.collected:
            return False
        distance = self.get_distance_to_player(player_x, player_y)
        return distance < MAP_PICKUP_DISTANCE
    
    def collect(self):
        """拾取地图"""
        if not self.collected:
            self.collected = True
            self.visible = False
            # 播放拾取音效
            audio_manager.play_sound('map')
            print(f"地图已拾取！将在右上角显示缩略图{MAP_REVEAL_DURATION/1000}秒")
            return True
        return False
    
    def get_relative_position(self, player_x, player_y, player_angle):
        """获取地图相对于玩家的位置（距离和角度）"""
        dx = self.x - player_x
        dy = self.y - player_y
        
        distance = math.sqrt(dx*dx + dy*dy)
        angle_to_map = math.atan2(dy, dx)
        relative_angle = angle_to_map - player_angle
        
        # 规范化角度到[-π, π]
        while relative_angle > math.pi:
            relative_angle -= 2 * math.pi
        while relative_angle < -math.pi:
            relative_angle += 2 * math.pi
            
        return distance, relative_angle
    
    def get_screen_position(self, player_x, player_y, player_angle, fov_degrees, screen_width, view_height):
        """
        计算地图在屏幕上的位置
        返回：(screen_x, screen_y, size, visible, alpha, screen_width_projection)
        """
        if not self.visible or self.collected:
            return 0, 0, 0, False, 0, 0
        
        distance, relative_angle = self.get_relative_position(player_x, player_y, player_angle)
        
        # 将相对角度转换为屏幕x坐标
        fov_rad = math.radians(fov_degrees)
        
        # 检查是否在视野内
        if abs(relative_angle) > fov_rad / 2:
            return 0, 0, 0, False, 0, 0
        
        # 计算屏幕x坐标（0在最左边，1在最右边）
        screen_x_ratio = 0.5 + (relative_angle / fov_rad)
        screen_x = screen_x_ratio * screen_width
        
        # 根据距离计算地图大小（透视投影）
        size = int(self.base_3d_size / (distance + 0.5))
        size = max(20, min(500, size))  # 限制大小范围
        
        # 计算地图底部在地板上的位置（地图悬浮高度略高于钥匙）
        eye_height = view_height // 2
        projection_factor = view_height * 0.5
        # 地图在离地0.3单位高度旋转悬浮
        map_height = 0.3
        floor_y = eye_height + (projection_factor / distance) - (map_height * projection_factor / distance)
        
        screen_y = min(view_height, int(floor_y))
        
        # 根据距离设置透明度
        alpha = max(150, 255 - int(distance * 10))
        
        # 计算地图宽度在屏幕上的投影（像素）
        screen_width_projection = (self.width_3d / (distance + 0.5)) * (screen_width / math.tan(fov_rad / 2))
        screen_width_projection = int(max(8, screen_width_projection))
        
        return screen_x, screen_y, size, True, alpha, screen_width_projection
    
    def draw_2d(self, surface, offset_x, offset_y, cell_size):
        """在2D视图中绘制地图（使用8×8像素画）"""
        if not self.visible or self.collected:
            return
            
        map_screen_x = offset_x + self.x * cell_size
        map_screen_y = offset_y + self.y * cell_size
        
        # 创建地图表面（放大显示）
        scale_factor = 3  # 放大3倍以便在2D视图中清晰显示
        map_surface = pygame.Surface((self.pixel_size * scale_factor, self.pixel_size * scale_factor), pygame.SRCALPHA)
        
        # 绘制地图像素画
        for py in range(self.pixel_size):
            for px in range(self.pixel_size):
                if self.sprite_2d[py][px] == 1:
                    # 绘制放大后的像素
                    rect = pygame.Rect(px * scale_factor, py * scale_factor, scale_factor, scale_factor)
                    pygame.draw.rect(map_surface, self.color, rect)
        
        # 将地图绘制到屏幕
        map_rect = map_surface.get_rect(center=(map_screen_x, map_screen_y))
        surface.blit(map_surface, map_rect)
        
        # 绘制地图发光效果（蓝色光晕）
        glow_radius = (self.pixel_size * scale_factor) // 2 + 2
        for i in range(2):
            glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
            alpha = 40 - i * 15
            pygame.draw.circle(glow_surface, (*self.color[:3], alpha), 
                             (glow_radius, glow_radius), glow_radius - i)
            surface.blit(glow_surface, (map_screen_x - glow_radius, map_screen_y - glow_radius))

    def draw_3d_sprite(self, surface, player_x, player_y, player_angle, fov_degrees, screen_width, view_height, wall_distances, line_width, pitch_offset=0):
        """
        在3D视图中绘制地图精灵
        使用独立的绘制逻辑，带有旋转效果
        """
        # 获取地图的屏幕位置、大小、宽度和可见性
        screen_x, screen_y, map_size, map_visible, alpha, map_screen_width = self.get_screen_position(
            player_x, player_y, player_angle, fov_degrees, screen_width, view_height
        )
        
        if not map_visible or map_size < 10 or self.collected:
            return

        # 计算地图在屏幕上的水平绘制范围
        map_left_screen = screen_x - map_screen_width // 2
        map_right_screen = screen_x + map_screen_width // 2
        map_left_screen = max(0, min(screen_width, map_left_screen))
        map_right_screen = max(0, min(screen_width, map_right_screen))

        # 计算地图到玩家的真实距离
        map_distance = self.get_distance_to_player(player_x, player_y)

        # 简单的遮挡检测：检查地图中心点是否被墙挡住
        center_screen_x = screen_x
        ray_idx = int(center_screen_x / line_width)
        ray_idx = max(0, min(len(wall_distances) - 1, ray_idx))
        
        wall_dist_at_center = wall_distances[ray_idx] if ray_idx < len(wall_distances) else MAX_VIEW_DISTANCE
        
        # 如果地图距离大于墙壁距离，则被遮挡
        if map_distance > wall_dist_at_center:
            return

        # 创建缩放后的地图表面
        scaled_width = int(map_screen_width)
        scaled_height = int(map_size)
        
        # 使用缓存的缩放纹理
        cache_key = (scaled_width, scaled_height, alpha, int(self.rotation_angle * 10))
        if cache_key in self.scaled_cache:
            scaled_surface = self.scaled_cache[cache_key]
        else:
            # 使用pygame内置的缩放函数
            scaled_surface = pygame.transform.scale(self.original_surface, (scaled_width, scaled_height))
            
            # 应用旋转效果
            if self.rotation_angle != 0:
                # 旋转模拟地图卷轴的浮动效果
                rotation_degrees = math.degrees(self.rotation_angle)
                scaled_surface = pygame.transform.rotate(scaled_surface, rotation_degrees)
                # 更新尺寸以适应旋转
                scaled_width, scaled_height = scaled_surface.get_size()
            
            # 应用距离透明度
            if alpha < 255:
                temp_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
                temp_surface.blit(scaled_surface, (0, 0))
                temp_surface.set_alpha(alpha)
                scaled_surface = temp_surface
            
            # 缓存结果
            if len(self.scaled_cache) < 5:  # 限制缓存大小
                self.scaled_cache[cache_key] = scaled_surface
        
        # 清理过期的缓存
        if len(self.scaled_cache) > 10:
            keys_to_remove = list(self.scaled_cache.keys())[:-5]
            for key in keys_to_remove:
                del self.scaled_cache[key]
        
        # 绘制到屏幕上
        adjusted_screen_y = int(screen_y + pitch_offset)
        sprite_rect = scaled_surface.get_rect(midbottom=(screen_x, adjusted_screen_y))
        surface.blit(scaled_surface, sprite_rect)
        
class Maze:
    """迷宫类 - 支持多关卡配置"""
    
    def __init__(self, level_index=0):
        self.level_index = level_index
        
        # 根据关卡索引获取迷宫尺寸
        self.width, self.height = LEVEL_MAZE_SIZES[level_index]
        
        # 初始化网格
        self.grid = np.ones((self.width, self.height), dtype=int)  # 1表示墙，0表示路径
        self.exit_pos = None
        self.exit_direction = None
        
        # 道具列表
        self.ghost = None      # 幽灵实例
        self.keys = []         # 钥匙实例列表（支持多个钥匙）
        self.heart = None      # 爱心实例
        self.map_item = None   # 新增：地图道具实例
        
        # 生成迷宫和道具
        self.generate_maze()
        
    def reset_ghost_position(self):
        """重置幽灵到迷宫中的随机位置"""
        if self.ghost:
            # 保存幽灵的其他状态，只重置位置
            old_visible = self.ghost.visible
            old_path = self.ghost.current_path
            old_state = self.ghost.walk_state
            
            # 重新放置幽灵到随机位置
            self.ghost.x, self.ghost.y = self.ghost._place_in_maze(self.width, self.height, self.grid)
            
            # 重置幽灵的寻路状态
            self.ghost._set_random_target()
            self.ghost.walk_state = "random"
            self.ghost.current_speed = self.ghost.slow_speed
            
            print(f"幽灵已重新生成在位置 ({self.ghost.x:.1f}, {self.ghost.y:.1f})")
    
    def generate_maze(self):
        """生成迷宫和所有道具"""
        # 使用深度优先搜索生成迷宫
        self.grid.fill(1)
            
        start_x, start_y = self.width // 2, self.height // 2
        self.grid[start_x, start_y] = 0
        
        stack = [(start_x, start_y)]
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        
        while stack:
            x, y = stack[-1]
            random.shuffle(directions)
            found = False
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 < nx < self.width-1 and 0 < ny < self.height-1 and self.grid[nx, ny] == 1:
                    self.grid[x + dx//2, y + dy//2] = 0
                    self.grid[nx, ny] = 0
                    stack.append((nx, ny))
                    found = True
                    break
                    
            if not found:
                stack.pop()
                
        # 设置出口
        exit_side = random.randint(0, 3)
        if exit_side == 0:
            exit_x = random.randint(1, self.width-2)
            self.exit_pos = (exit_x, 0)
            self.exit_direction = 0
            self.grid[exit_x, 0] = 0
            self.grid[exit_x, 1] = 0
        elif exit_side == 1:
            exit_y = random.randint(1, self.height-2)
            self.exit_pos = (self.width-1, exit_y)
            self.exit_direction = 1
            self.grid[self.width-1, exit_y] = 0
            self.grid[self.width-2, exit_y] = 0
        elif exit_side == 2:
            exit_x = random.randint(1, self.width-2)
            self.exit_pos = (exit_x, self.height-1)
            self.exit_direction = 2
            self.grid[exit_x, self.height-1] = 0
            self.grid[exit_x, self.height-2] = 0
        else:
            exit_y = random.randint(1, self.height-2)
            self.exit_pos = (0, exit_y)
            self.exit_direction = 3
            self.grid[0, exit_y] = 0
            self.grid[1, exit_y] = 0
            
        # 确保中心区域是开放的
        center_x, center_y = self.width // 2, self.height // 2
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if 0 <= center_x+dx < self.width and 0 <= center_y+dy < self.height:
                    self.grid[center_x+dx, center_y+dy] = 0
                    
        # ================================================
        # 根据关卡添加额外路径（提高连通度）
        # ================================================
        # 根据关卡设置不同的额外路径数量：
        # 第一关：3条额外路径（简单，保持一定复杂度）
        # 第二关：10条额外路径（中等，增加一些循环）
        # 第三关：20条额外路径（困难，更多连通路径）
        extra_paths_count_by_level = [3, 10, 20]
        
        if self.level_index < len(extra_paths_count_by_level):
            extra_paths_count = extra_paths_count_by_level[self.level_index]
        else:
            extra_paths_count = 5  # 默认值
        
        print(f"第{self.level_index+1}关: 添加{extra_paths_count}条额外路径提高连通度")
        
        extra_paths_added = 0
        max_attempts = extra_paths_count * 10  # 最大尝试次数，避免无限循环
        
        for attempt in range(max_attempts):
            if extra_paths_added >= extra_paths_count:
                break
            
            # 随机选择一个位置
            x = random.randint(1, self.width-2)
            y = random.randint(1, self.height-2)
            
            # 只处理墙壁位置
            if self.grid[x, y] == 1:
                # 检查上下左右四个方向的邻居
                neighbors = [
                    (x+1, y),  # 右
                    (x-1, y),  # 左
                    (x, y+1),  # 下
                    (x, y-1)   # 上
                ]
                
                # 检查是否是合适的墙壁位置：
                # 1. 至少有一个邻居是路径（确保不是孤立墙壁）
                # 2. 打通后不会创建太大的开放区域（可选）
                path_neighbors = 0
                for nx, ny in neighbors:
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if self.grid[nx, ny] == 0:
                            path_neighbors += 1
                
                # 如果至少有一个路径邻居，则打通这面墙
                if path_neighbors >= 1:
                    self.grid[x, y] = 0
                    extra_paths_added += 1
        
        print(f"第{self.level_index+1}关: 成功添加{extra_paths_added}条额外路径")
        
        # 在添加额外路径后，确保出口可达
        self._ensure_exit_reachable()
        
        # 创建幽灵实例（使用优化后的Ghost类）
        self.ghost = Ghost(self.width, self.height, self.grid, self.level_index)
        
        # 创建钥匙实例（根据关卡数量）
        self.keys = []
        key_count = LEVEL_KEY_COUNTS[self.level_index]
        
        for i in range(key_count):
            # 确保每个钥匙位置不重叠
            key_placed = False
            attempts = 0
            while not key_placed and attempts < 100:
                key_instance = Key(self.width, self.height, self.grid, self.level_index)
                
                # 检查是否与其他钥匙位置重叠
                overlap = False
                for existing_key in self.keys:
                    if (abs(key_instance.x - existing_key.x) < 1.0 and 
                        abs(key_instance.y - existing_key.y) < 1.0):
                        overlap = True
                        break
                
                if not overlap:
                    self.keys.append(key_instance)
                    key_placed = True
                attempts += 1
            
            if not key_placed:
                print(f"警告: 无法为第{i+1}把钥匙找到合适位置")
        
        print(f"第{self.level_index+1}关: 已生成{len(self.keys)}把钥匙")
        
        # 创建爱心实例
        self.heart = Heart(self.width, self.height, self.grid, self.level_index)
        
        # 创建地图道具实例（新增：每关1个）
        self.map_item = Map(self.width, self.height, self.grid, self.level_index)
        print(f"第{self.level_index+1}关: 地图道具已生成")
        
    def _ensure_exit_reachable(self):
        """
        确保出口点连接到迷宫主体路径。
        如果出口点孤立，则打通一条路径到最近的现有路径。
        """
        if not self.exit_pos:
            return
        
        exit_x, exit_y = self.exit_pos
        # 根据出口方向确定内部起始点（出口相邻的迷宫内部点）
        if self.exit_direction == 0:  # 上
            start_x, start_y = exit_x, 1
        elif self.exit_direction == 1:  # 右
            start_x, start_y = self.width - 2, exit_y
        elif self.exit_direction == 2:  # 下
            start_x, start_y = exit_x, self.height - 2
        else:  # 左
            start_x, start_y = 1, exit_y
        
        # 如果起始点已是路径，则检查连通性；否则先设置为路径
        if self.grid[start_x, start_y] == 1:
            self.grid[start_x, start_y] = 0
        
        # 使用BFS查找从起始点到任何现有路径的最短连接
        from collections import deque
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        visited = [[False] * self.height for _ in range(self.width)]
        queue = deque()
        queue.append((start_x, start_y, []))  # 每个元素为(x, y, path)
        visited[start_x][start_y] = True
        found_path = None
        
        while queue:
            x, y, path = queue.popleft()
            # 如果当前点是路径且不是起始点，则找到连接
            if self.grid[x, y] == 0 and (x != start_x or y != start_y):
                found_path = path
                break
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and not visited[nx][ny]:
                    visited[nx][ny] = True
                    new_path = path + [(nx, ny)]
                    queue.append((nx, ny, new_path))
        
        # 如果找到连接，打通路径上的墙壁
        if found_path:
            for px, py in found_path:
                if self.grid[px, py] == 1:  # 如果是墙，则打通
                    self.grid[px, py] = 0
            print(f"出口已通过 {len(found_path)} 个单元格连接到迷宫主体。")
        else:
            # 如果未找到（理论上不应发生），则简单打通从起始点到中心的直线路径作为后备
            print("警告：未找到现有路径连接，使用后备方案打通到中心的路径。")
            current_x, current_y = start_x, start_y
            center_x, center_y = self.width // 2, self.height // 2
            while not (current_x == center_x and current_y == center_y):
                if current_x < center_x:
                    next_x, next_y = current_x + 1, current_y
                elif current_x > center_x:
                    next_x, next_y = current_x - 1, current_y
                elif current_y < center_y:
                    next_x, next_y = current_x, current_y + 1
                else:
                    next_x, next_y = current_x, current_y - 1
                if 0 <= next_x < self.width and 0 <= next_y < self.height:
                    if self.grid[next_x, next_y] == 1:
                        self.grid[next_x, next_y] = 0
                    current_x, current_y = next_x, next_y
                else:
                    break
        
    def is_wall(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        return self.grid[int(x), int(y)] == 1
    
    def is_exit(self, x, y):
        if not self.exit_pos:
            return False
            
        exit_x, exit_y = self.exit_pos
        return abs(x - exit_x) < 0.5 and abs(y - exit_y) < 0.5
    
    def get_all_keys_collected(self):
        """检查是否所有钥匙都被收集了"""
        if not self.keys:
            return True  # 如果没有钥匙，默认已收集所有
        
        for key in self.keys:
            if not key.collected:
                return False
        return True
    
    def get_keys_collected_count(self):
        """获取已收集的钥匙数量"""
        if not self.keys:
            return 0
        
        count = 0
        for key in self.keys:
            if key.collected:
                count += 1
        return count
    
    def get_total_keys_count(self):
        """获取本关钥匙总数"""
        return len(self.keys)
    
    def is_map_collected(self):
        """检查地图是否被收集"""
        if self.map_item:
            return self.map_item.collected
        return True  # 如果没有地图，默认已收集
    
    def draw(self, surface, offset_x, offset_y, cell_size):
        """绘制迷宫和所有道具"""
        # 绘制迷宫
        for x in range(self.width):
            for y in range(self.height):
                rect = pygame.Rect(
                    offset_x + x * cell_size,
                    offset_y + y * cell_size,
                    cell_size, cell_size
                )
                if self.grid[x, y] == 1:
                    # 使用当前关卡的颜色
                    pygame.draw.rect(surface, LEVEL_COLORS[self.level_index]['wall'], rect)
                else:
                    pygame.draw.rect(surface, LEVEL_COLORS[self.level_index]['path'], rect)
                    pygame.draw.rect(surface, (40, 40, 50), rect, 1)
        
        # 绘制出口
        if self.exit_pos:
            exit_x, exit_y = self.exit_pos
            exit_rect = pygame.Rect(
                offset_x + exit_x * cell_size,
                offset_y + exit_y * cell_size,
                cell_size, cell_size
            )
            # 出口颜色保持不变（使用第一关的出口颜色）
            pygame.draw.rect(surface, LEVEL_COLORS[0]['exit'], exit_rect)
            
            try:
                exit_text = font_normal.render("EXIT", True, (0, 0, 0))
                text_rect = exit_text.get_rect(center=exit_rect.center)
                surface.blit(exit_text, text_rect)
            except:
                pygame.draw.line(surface, (0, 0, 0), exit_rect.topleft, exit_rect.bottomright, 2)
                pygame.draw.line(surface, (0, 0, 0), exit_rect.topright, exit_rect.bottomleft, 2)
        
        # 绘制所有钥匙（2D视图）- 仅在未被拾取时绘制
        for key in self.keys:
            if not key.collected:
                key.draw_2d(surface, offset_x, offset_y, cell_size)
        
        # 绘制爱心（2D视图）- 仅在未被拾取时绘制
        if self.heart and not self.heart.collected:
            self.heart.draw_2d(surface, offset_x, offset_y, cell_size)
        
        # 绘制地图道具（2D视图）- 仅在未被拾取时绘制（新增）
        if self.map_item and not self.map_item.collected:
            self.map_item.draw_2d(surface, offset_x, offset_y, cell_size)
        
        # 绘制幽灵（2D视图）
        if self.ghost:
            self.ghost.draw_2d(surface, offset_x, offset_y, cell_size)

class Player:
    def __init__(self, maze, level_index=0):
        self.x = maze.width // 2 + 0.5
        self.y = maze.height // 2 + 0.5
        self.angle = 0
        self.maze = maze
        
        # 移动参数
        self.normal_speed = 0.04
        self.sprint_speed = 0.06
        self.speed = self.normal_speed
        self.rotation_speed = 0.05
        
        self.mouse_sensitivity = 0.005  # 鼠标灵敏度，可调整
        self.pitch_sensitivity = 0.35   # 鼠标Y轴俯仰灵敏度（像素）
        self.pitch_key_speed = 220      # 键盘俯仰速度（像素/秒）
        self.pitch = 0.0                # 视角俯仰偏移（像素，+向下，-向上）
        
        # 疾跑控制参数（新增：双击前进键实现疾跑）
        self.is_sprinting = False
        self.last_forward_press_time = 0
        self.double_tap_threshold = 300  # 毫秒，双击时间阈值
        self.forward_key_held = False
        
        # 游戏状态
        self.reached_exit = False
        self.mouse_control = True  # 修改：默认启用鼠标控制
        self.last_mouse_x = 0
        self.trigger_active = False
        self.radius = PLAYER_RADIUS
        self.near_ghost = False
        self.ghost_distance = float('inf')
        
        # 关卡系统属性 - 新增
        self.current_level = level_index  # 当前关卡索引
        self.keys_collected_in_level = 0  # 本关已收集钥匙数
        self.total_keys_in_level = LEVEL_KEY_COUNTS[level_index]  # 本关钥匙总数
        
        # 生命值系统
        self.lives = PLAYER_INITIAL_LIVES  # 初始生命值
        self.max_lives = PLAYER_INITIAL_LIVES
        self.is_caught = False  # 是否被幽灵抓住（瞬间状态）
        self.game_over = False  # 游戏是否结束
        
        # 道具收集状态
        self.heart_collected = False  # 本次游戏是否已收集过爱心
        self.heart_pickup_cooldown = 0  # 爱心拾取冷却时间
        self.map_collected = False  # 是否已收集地图（新增）
        self.map_reveal_timer = 0  # 地图显示计时器（新增）
        self.map_visible = False  # 地图是否正在显示（新增）
        
        # 渐变过渡系统 - 扩展支持关卡过渡
        self.fade_state = "none"  # 状态: "none", "fading_out", "fading_in", "dark", "level_transition_out", "level_transition_in"
        self.fade_alpha = 0  # 当前透明度 (0-255)
        self.fade_timer = 0  # 渐变计时器
        self.fade_duration = FADE_DURATION  # 渐变持续时间（毫秒）
        self.fade_max_alpha = FADE_MAX_ALPHA  # 最大透明度
        
        # 关卡过渡专用属性
        self.level_transition_text = ""  # 过渡时显示的文字
        self.next_level_index = 0  # 要进入的下一关索引
        
        # 重生位置（每关更新）
        self.spawn_x = maze.width // 2 + 0.5
        self.spawn_y = maze.height // 2 + 0.5
        self.spawn_angle = 0
        self.spawn_pitch = 0.0
        
        print(f"玩家初始化 - 第{self.current_level+1}关，需要收集{self.total_keys_in_level}把钥匙")
    
    def get_pitch_limit(self):
        """根据窗口高度动态计算俯仰偏移上限"""
        return int(HEIGHT * 0.35)
    
    def check_collision(self, x, y):
        """检查给定位置是否与墙碰撞"""
        points = [
            (x, y),
            (x + self.radius, y),
            (x - self.radius, y),
            (x, y + self.radius),
            (x, y - self.radius),
            (x + self.radius * 0.7, y + self.radius * 0.7),
            (x - self.radius * 0.7, y + self.radius * 0.7),
            (x + self.radius * 0.7, y - self.radius * 0.7),
            (x - self.radius * 0.7, y - self.radius * 0.7)
        ]
        
        for px, py in points:
            if self.maze.is_wall(px, py):
                return True
        return False
    
    def check_key_pickup(self):
        """检查并处理钥匙拾取"""
        if not self.maze.keys:
            return False
            
        keys_collected_this_frame = 0
        
        for key in self.maze.keys:
            if not key.collected and key.is_near_player(self.x, self.y):
                if key.collect():
                    self.keys_collected_in_level += 1
                    keys_collected_this_frame += 1
                    print(f"钥匙已拾取！({self.keys_collected_in_level}/{self.total_keys_in_level})")
        
        return keys_collected_this_frame > 0
    
    def check_heart_pickup(self):
        """检查并处理爱心拾取"""
        # 移除对heart_collected的检查，允许每关重新拾取
        
        if self.maze.heart and not self.maze.heart.collected:
            if self.maze.heart.is_near_player(self.x, self.y):
                if self.maze.heart.collect():
                    self.lives += 1  # 增加生命值
                    print(f"爱心已拾取！生命值: {self.lives}")
                    return True
        return False
    
    def check_map_pickup(self):
        """检查并处理地图拾取（新增）"""
        if self.maze.map_item and not self.maze.map_item.collected:
            if self.maze.map_item.is_near_player(self.x, self.y):
                if self.maze.map_item.collect():
                    self.map_collected = True
                    # 地图拾取后立即显示
                    self.map_visible = True
                    self.map_reveal_timer = pygame.time.get_ticks()
                    print(f"地图已拾取！")
                    return True
        return False
    
    def update_map_reveal(self, dt):
        """更新地图显示状态（新增）"""
        if self.map_visible:
            current_time = pygame.time.get_ticks()
            if current_time - self.map_reveal_timer > MAP_REVEAL_DURATION:
                self.map_visible = False
                print("地图显示时间结束")
    
    def start_fade_out(self, fade_type="caught", next_level=-1):
        """开始渐变变暗效果
        fade_type: "caught"=被抓住, "level_transition"=关卡过渡
        next_level: 关卡过渡时指定下一关索引
        """
        self.fade_state = "fading_out" if fade_type == "caught" else "level_transition_out"
        self.fade_timer = 0
        self.fade_alpha = 0
        
        if fade_type == "caught":
            self.level_transition_text = "被幽灵抓住了！"
            # 播放被抓住音效
            audio_manager.play_sound('caught')
            print("开始被抓渐变变暗...")
        else:
            self.next_level_index = next_level
            if next_level < TOTAL_LEVELS:
                self.level_transition_text = f"第{self.current_level+1}关通过！进入第{next_level+1}关..."
            else:
                self.level_transition_text = "恭喜！通关所有关卡！"
            print(f"开始关卡过渡: {self.level_transition_text}")
    
    def start_fade_in(self, fade_type="caught"):
        """开始渐变恢复效果"""
        if fade_type == "caught":
            self.fade_state = "fading_in"
        else:
            self.fade_state = "level_transition_in"
        self.fade_timer = 0
        self.fade_alpha = self.fade_max_alpha
        print("开始渐变恢复...")
    
    def update_fade(self, dt):
        """更新渐变效果"""
        if self.fade_state == "none":
            return
            
        self.fade_timer += dt * 1000  # 转换为毫秒
        
        # 被抓渐变逻辑
        if self.fade_state == "fading_out":
            # 计算透明度：从0线性增加到最大透明度
            progress = min(1.0, self.fade_timer / self.fade_duration)
            self.fade_alpha = int(progress * self.fade_max_alpha)
            
            if progress >= 1.0:
                # 变暗完成，进入全黑状态
                self.fade_state = "dark"
                self.fade_alpha = self.fade_max_alpha
                print("变暗完成，准备重生...")
                
                # 在黑暗状态下重置玩家位置
                self.reset_to_spawn()
                
                # 减少生命值
                self.lives -= 1
                print(f"生命值减少: {self.lives}/{self.max_lives}")
                
                # 检查游戏是否结束
                if self.lives <= 0:
                    self.game_over = True
                    print("游戏结束！")
                    # 生命值耗尽，直接进入游戏结束状态，不再渐变恢复
                    self.fade_state = "none"
                    self.fade_alpha = 0
                else:
                    # 生命值大于0，开始渐变恢复
                    self.start_fade_in("caught")
        
        elif self.fade_state == "fading_in":
            # 计算透明度：从最大透明度线性减少到0
            progress = min(1.0, self.fade_timer / self.fade_duration)
            self.fade_alpha = int((1.0 - progress) * self.fade_max_alpha)
            
            if progress >= 1.0:
                # 恢复完成
                self.fade_state = "none"
                self.fade_alpha = 0
                self.is_caught = False  # 重置被抓状态
                print("渐变恢复完成")
        
        # 关卡过渡渐变逻辑
        elif self.fade_state == "level_transition_out":
            # 计算透明度：从0线性增加到最大透明度
            progress = min(1.0, self.fade_timer / LEVEL_TRANSITION_DURATION)
            self.fade_alpha = int(progress * self.fade_max_alpha)
            
            if progress >= 1.0:
                # 变暗完成，进入关卡加载状态
                self.fade_state = "dark"
                self.fade_alpha = self.fade_max_alpha
                print("关卡过渡变暗完成，准备加载下一关...")
                # 这里不直接加载关卡，由Game类处理
        
        elif self.fade_state == "level_transition_in":
            # 计算透明度：从最大透明度线性减少到0
            progress = min(1.0, self.fade_timer / LEVEL_TRANSITION_DURATION)
            self.fade_alpha = int((1.0 - progress) * self.fade_max_alpha)
            
            if progress >= 1.0:
                # 恢复完成
                self.fade_state = "none"
                self.fade_alpha = 0
                print("关卡过渡渐变恢复完成")
        
        elif self.fade_state == "dark":
            # 全黑状态，等待外部指令开始恢复
            pass
            
    def reset_to_spawn(self):
        """重置玩家到出生点"""
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.angle = self.spawn_angle
        self.pitch = self.spawn_pitch
        self.is_caught = False  # 重置被抓状态
        
        # 重新生成幽灵到随机位置
        if self.maze:
            self.maze.reset_ghost_position()
    
    def update_spawn_position(self):
        """更新重生点为当前位置（用于关卡开始）"""
        self.spawn_x = self.x
        self.spawn_y = self.y
        self.spawn_angle = self.angle
        self.spawn_pitch = self.pitch
        print(f"重生点更新为: ({self.spawn_x:.1f}, {self.spawn_y:.1f})")
    
    def move_with_collision(self, dx, dy):
        """考虑碰撞的移动，返回实际移动的距离"""
        new_x = self.x + dx
        new_y = self.y
        
        if not self.check_collision(new_x, new_y):
            self.x = new_x
        else:
            for i in range(5):
                test_dx = dx * (0.8 - i * 0.15)
                test_x = self.x + test_dx
                if not self.check_collision(test_x, new_y):
                    self.x = test_x
                    dx = test_dx
                    break
            else:
                dx = 0
        
        new_x = self.x
        new_y = self.y + dy
        
        if not self.check_collision(new_x, new_y):
            self.y = new_y
        else:
            for i in range(5):
                test_dy = dy * (0.8 - i * 0.15)
                test_y = self.y + test_dy
                if not self.check_collision(new_x, test_y):
                    self.y = test_y
                    dy = test_dy
                    break
            else:
                dy = 0
        
        return dx, dy
        
    def update(self, keys, mouse_rel, dt):
        # 如果游戏结束，不更新玩家移动和幽灵
        if self.game_over:
            return False
            
        # 如果玩家正在渐变过渡中，不处理移动
        if self.fade_state != "none":
            self.update_fade(dt)
            return False
        
        # 如果玩家被幽灵抓住（瞬时状态），开始渐变变暗
        if self.is_caught and self.fade_state == "none":
            self.start_fade_out("caught")
            return False
        
        # 更新地图显示状态
        if self.map_visible:
            current_time = pygame.time.get_ticks()
            if current_time - self.map_reveal_timer >= MAP_REVEAL_DURATION:
                self.map_visible = False
                print("地图显示时间结束")
        
        # 如果启用了鼠标控制，将鼠标重置到屏幕中心，避免到达边界
        if self.mouse_control:
            pygame.mouse.set_pos((WIDTH//2, HEIGHT//2))
        
        # ====================================================================
        # 修改：疾跑控制方式改为双击前进键
        # ====================================================================
        current_time = pygame.time.get_ticks()
        
        # 检查前进键状态（仅使用W键）
        forward_pressed = keys[pygame.K_w]
        
        if forward_pressed and not self.forward_key_held:
            # 第一次按下前进键
            self.forward_key_held = True
            time_since_last_press = current_time - self.last_forward_press_time
            
            # 如果在双击阈值内再次按下，触发疾跑
            if time_since_last_press < self.double_tap_threshold:
                self.is_sprinting = True
                print("疾跑激活！")
            else:
                self.is_sprinting = False
            
            self.last_forward_press_time = current_time
        elif not forward_pressed:
            self.forward_key_held = False
        
        # 设置移动速度：如果正在疾跑且前进键被按住，使用疾跑速度
        if self.is_sprinting and forward_pressed:
            self.speed = self.sprint_speed
        else:
            self.speed = self.normal_speed
        
        moved = False
        
        if forward_pressed:
            dx = math.cos(self.angle) * self.speed
            dy = math.sin(self.angle) * self.speed
            actual_dx, actual_dy = self.move_with_collision(dx, dy)
            if abs(actual_dx) > 0.001 or abs(actual_dy) > 0.001:
                moved = True
                
        if keys[pygame.K_s]:
            dx = -math.cos(self.angle) * self.speed
            dy = -math.sin(self.angle) * self.speed
            actual_dx, actual_dy = self.move_with_collision(dx, dy)
            if abs(actual_dx) > 0.001 or abs(actual_dy) > 0.001:
                moved = True
        
        if keys[pygame.K_a]:
            dx = math.cos(self.angle - math.pi/2) * self.speed
            dy = math.sin(self.angle - math.pi/2) * self.speed
            actual_dx, actual_dy = self.move_with_collision(dx, dy)
            if abs(actual_dx) > 0.001 or abs(actual_dy) > 0.001:
                moved = True
                
        if keys[pygame.K_d]:
            dx = math.cos(self.angle + math.pi/2) * self.speed
            dy = math.sin(self.angle + math.pi/2) * self.speed
            actual_dx, actual_dy = self.move_with_collision(dx, dy)
            if abs(actual_dx) > 0.001 or abs(actual_dy) > 0.001:
                moved = True
        
        # 鼠标控制视角
        if self.mouse_control:
            if mouse_rel[0] != 0:
                self.angle += mouse_rel[0] * self.mouse_sensitivity
                # 注意：set_pos 需要根据当前屏幕尺寸设置，已在 run 中每帧处理
                pygame.mouse.set_pos((WIDTH//2, HEIGHT//2))
            if mouse_rel[1] != 0:
                # 鼠标上移抬头，下移低头
                self.pitch -= mouse_rel[1] * self.pitch_sensitivity
        
        # 方向键控制视角（左右键控制旋转，上下键控制俯仰）
        if keys[pygame.K_LEFT]:
            self.angle -= self.rotation_speed
        if keys[pygame.K_RIGHT]:
            self.angle += self.rotation_speed
        
        # 键盘俯仰（方向键上下、PageUp/PageDown 与 I/K）- 提高灵敏度
        pitch_step = self.pitch_key_speed * dt * 1.5  # 提高俯仰灵敏度 50%
        if keys[pygame.K_UP] or keys[pygame.K_PAGEUP] or keys[pygame.K_i]:
            self.pitch += pitch_step  # 上键抬头
        if keys[pygame.K_DOWN] or keys[pygame.K_PAGEDOWN] or keys[pygame.K_k]:
            self.pitch -= pitch_step  # 下键低头
            
        self.angle %= 2 * math.pi
        pitch_limit = self.get_pitch_limit()
        self.pitch = max(-pitch_limit, min(pitch_limit, self.pitch))
        
        # 播放脚步声
        audio_manager.play_step_sound(moved, dt)
        
        # 更新爱心拾取冷却时间
        if self.heart_pickup_cooldown > 0:
            self.heart_pickup_cooldown -= dt * 1000  # 转换为毫秒
        
        # 检查钥匙拾取
        if self.check_key_pickup():
            # 不需要冷却时间，可以连续拾取多个钥匙
            pass
        
        # 检查爱心拾取
        if self.heart_pickup_cooldown <= 0:
            if self.check_heart_pickup():
                self.heart_pickup_cooldown = 500  # 设置500毫秒冷却时间，防止重复触发
        
        # 检查地图拾取（新增）
        if not self.map_collected:
            if self.check_map_pickup():
                print("地图已拾取，右上角将显示缩略图")
        
        # 检查是否在出口触发区域
        self.trigger_active = self.is_in_trigger_zone()
        
        # 检查是否满足通关条件：在出口区域且已收集所有钥匙
        # 注意：这里只是检查条件，真正的通关触发在Game类中
        if self.trigger_active and not self.reached_exit:
            if self.maze.get_all_keys_collected():
                print(f"可以通关！已收集{self.keys_collected_in_level}/{self.total_keys_in_level}把钥匙，按E键进入下一关")
            else:
                keys_needed = self.total_keys_in_level - self.keys_collected_in_level
                print(f"需要找到所有钥匙才能打开出口！还差{keys_needed}把钥匙")
        
        # 更新幽灵距离并检查是否被抓住
        self.update_ghost_distance()
        
        # 检查是否被幽灵抓住（瞬时触发）
        if not self.is_caught and not self.reached_exit and not self.game_over:
            if self.ghost_distance < GHOST_CATCH_DISTANCE:
                self.is_caught = True
                print("被幽灵抓住了！")
        
        return moved
        
    def is_in_trigger_zone(self):
        if not self.maze.exit_pos:
            return False
            
        exit_x, exit_y = self.maze.exit_pos
        dx = self.x - exit_x
        dy = self.y - exit_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        return distance < TRIGGER_DISTANCE
    
    def update_ghost_distance(self):
        """更新玩家与幽灵的距离，并检查是否被抓住"""
        if not self.maze.ghost:
            self.near_ghost = False
            self.ghost_distance = float('inf')
            return
            
        self.ghost_distance = self.maze.ghost.get_distance_to_player(self.x, self.y)
        self.near_ghost = self.ghost_distance < TRIGGER_DISTANCE * 2
    
    def cast_ray(self, angle):
        """
        发射一条射线，返回：
        - wall_distance: 到墙壁的距离
        - hit_exit: 是否击中出口
        """
        ray_x, ray_y = self.x, self.y
        ray_dir_x = math.cos(angle)
        ray_dir_y = math.sin(angle)
        
        # 初始化返回值
        wall_distance = MAX_VIEW_DISTANCE
        hit_exit = False
        
        # 检查射线是否击中墙壁
        max_steps = 100
        step_size = 0.1
        
        for step in range(max_steps):
            ray_x += ray_dir_x * step_size
            ray_y += ray_dir_y * step_size
            
            if self.maze.is_wall(ray_x, ray_y):
                dx = ray_x - self.x
                dy = ray_y - self.y
                dist = math.sqrt(dx*dx + dy*dy)
                
                angle_diff = angle - self.angle
                dist *= math.cos(angle_diff)
                
                wall_distance = min(dist, MAX_VIEW_DISTANCE)
                hit_exit = self.maze.is_exit(ray_x, ray_y)
                break
        
        return wall_distance, hit_exit
    
    def get_ray_distances(self):
        """获取所有射线的距离和击中信息"""
        wall_distances = []
        hit_exits = []
        half_fov_rad = math.radians(FOV / 2)
        
        for i in range(RAY_COUNT):
            ray_angle = self.angle - half_fov_rad + (i / RAY_COUNT) * math.radians(FOV)
            ray_angle %= 2 * np.pi
            
            wall_dist, hit_exit = self.cast_ray(ray_angle)
            wall_distances.append(wall_dist)
            hit_exits.append(hit_exit)
            
        return wall_distances, hit_exits
    
    def draw(self, surface, offset_x, offset_y, cell_size):
        player_x = offset_x + self.x * cell_size
        player_y = offset_y + self.y * cell_size
        player_radius_pixels = int(self.radius * cell_size)
        
        # 使用当前关卡的颜色
        player_color = LEVEL_COLORS[self.current_level]['player']
        
        gfxdraw.filled_circle(surface, int(player_x), int(player_y), player_radius_pixels, player_color)
        gfxdraw.aacircle(surface, int(player_x), int(player_y), player_radius_pixels, player_color)
        
        end_x = player_x + math.cos(self.angle) * player_radius_pixels * 2
        end_y = player_y + math.sin(self.angle) * player_radius_pixels * 2
        pygame.draw.line(surface, (255, 255, 255), (player_x, player_y), (end_x, end_y), 2)
        
        half_fov_rad = math.radians(FOV / 2)
        start_angle = self.angle - half_fov_rad
        end_angle = self.angle + half_fov_rad
        
        ray_length = cell_size * 3
        left_x = player_x + math.cos(start_angle) * ray_length
        left_y = player_y + math.sin(start_angle) * ray_length
        right_x = player_x + math.cos(end_angle) * ray_length
        right_y = player_y + math.sin(end_angle) * ray_length
        
        ray_color = LEVEL_COLORS[self.current_level]['ray']
        pygame.draw.line(surface, ray_color, (player_x, player_y), (left_x, left_y), 1)
        pygame.draw.line(surface, ray_color, (player_x, player_y), (right_x, right_y), 1)
        
        if self.trigger_active and not self.reached_exit:
            trigger_radius = TRIGGER_DISTANCE * cell_size
            trigger_surface = pygame.Surface((int(trigger_radius*2), int(trigger_radius*2)), pygame.SRCALPHA)
            trigger_color = LEVEL_COLORS[self.current_level]['trigger_zone']
            gfxdraw.aacircle(trigger_surface, int(trigger_radius), int(trigger_radius), int(trigger_radius), trigger_color)
            surface.blit(trigger_surface, (player_x - trigger_radius, player_y - trigger_radius))
            
            # 根据是否收集齐钥匙显示不同的提示信息
            if self.maze.get_all_keys_collected():
                trigger_text = font_small.render("按E键使用钥匙打开出口", True, trigger_color)
            else:
                keys_needed = self.total_keys_in_level - self.keys_collected_in_level
                trigger_text = font_small.render(f"需要{keys_needed}把钥匙才能打开出口", True, (255, 100, 100))
            text_rect = trigger_text.get_rect(center=(player_x, player_y - trigger_radius - 10))
            surface.blit(trigger_text, text_rect)
            
class Game:
    def __init__(self):
        # 初始化为第一关
        self.current_level = 0
        self.game_won = False  # 是否赢得整个游戏（通过所有关卡）
        self.is_paused = False  # 新增：游戏暂停状态
        
        # 2D缩略图显示控制（新增）
        self.show_mini_map = False  # 右上角缩略图是否显示
        self.mini_map_alpha = 0  # 缩略图透明度 (0-255)
        self.mini_map_fade_state = "none"  # "none", "fade_in", "fade_out", "visible"
        self.mini_map_fade_timer = 0
        self.mini_map_reveal_end_time = 0  # 地图显示结束时间
        
        # 创建第一关迷宫
        self.maze = Maze(self.current_level)
        
        # 创建玩家
        self.player = Player(self.maze, self.current_level)
        
        # 视图设置
        self.show_2d = False  # 修改：默认不显示2D视图
        self.fullscreen = False
        self.view_width = BASE_WINDOW_WIDTH  # 修改：使用基础宽度
        self.view_height = BASE_WINDOW_HEIGHT  # 修改：使用基础高度
        
        # 动态计算格子大小（用于迷你地图）
        self.cell_size = self.calculate_cell_size()
        self.maze_offset_x = (MINI_MAP_SIZE - self.maze.width * MINI_MAP_CELL_SIZE) // 2
        self.maze_offset_y = (MINI_MAP_SIZE - self.maze.height * MINI_MAP_CELL_SIZE) // 2
        
        # 设置全局颜色为第一关颜色
        global COLORS
        COLORS = LEVEL_COLORS[self.current_level]
        
        # 隐藏鼠标光标
        pygame.mouse.set_visible(False)
        
        # 启动背景音乐
        audio_manager.start_background_music()
        
        print(f"游戏初始化 - 第{self.current_level+1}关开始")
        print(f"迷宫尺寸: {self.maze.width}×{self.maze.height}")
        print(f"需要收集钥匙: {self.player.total_keys_in_level}把")
        print(f"幽灵追踪半径: {LEVEL_GHOST_CHASE_RADIUS[self.current_level]}单位")
        print("控制说明:")
        print("  - WASD/方向键: 移动")
        print("  - 鼠标: 视角转动 + 抬头/低头（默认启用）")
        print("  - PageUp/PageDown 或 I/K: 抬头/低头")
        print("  - 双击前进键(W/↑)并按住第二下: 疾跑")
        print("  - 空格键: 暂停/继续游戏")
        print("  - Ctrl+M: 切换右上角2D缩略图显示")
        print("  - F: 切换全屏")
        print("  - R: 重新开始游戏")
        print("  - ESC: 退出游戏")
        print("  - E: 在出口处使用钥匙进入下一关")
        print("游戏目标: 收集所有钥匙，避开幽灵，找到出口")
        
    def calculate_cell_size(self):
        """动态计算格子大小以适应2D视图（用于迷你地图）"""
        max_cell_width = (MINI_MAP_SIZE - 20) // self.maze.width  # 留出边距
        max_cell_height = (MINI_MAP_SIZE - 20) // self.maze.height  # 留出边距
        return min(max_cell_width, max_cell_height, MINI_MAP_CELL_SIZE)  # 使用迷你地图的格子大小

    def update_maze_offsets(self):
        """更新迷宫偏移量（用于迷你地图）"""
        self.maze_offset_x = (MINI_MAP_SIZE - self.maze.width * self.cell_size) // 2
        self.maze_offset_y = (MINI_MAP_SIZE - self.maze.height * self.cell_size) // 2
    
    def load_level(self, level_index):
        """加载指定关卡"""
        self.current_level = level_index
        
        # 更新全局颜色
        global COLORS
        COLORS = LEVEL_COLORS[level_index]
        
        # 创建新关卡迷宫
        self.maze = Maze(level_index)
        
        # 重置玩家状态，保留生命值，重置爱心拾取状态
        old_lives = self.player.lives if hasattr(self.player, 'lives') else PLAYER_INITIAL_LIVES
        # 重置爱心拾取冷却时间
        old_heart_cooldown = self.player.heart_pickup_cooldown if hasattr(self.player, 'heart_pickup_cooldown') else 0
        
        self.player = Player(self.maze, level_index)
        self.player.lives = old_lives
        self.player.heart_pickup_cooldown = old_heart_cooldown
        # 重置地图收集状态（每关都可以重新拾取地图）
        self.player.map_collected = False
        self.player.map_visible = False
        self.player.map_reveal_timer = 0
        
        # 更新重生点为关卡中心
        self.player.update_spawn_position()
        
        # 重置迷你地图显示状态
        self.show_mini_map = False
        self.mini_map_alpha = 0
        self.mini_map_fade_state = "none"
        self.mini_map_fade_timer = 0
        self.mini_map_reveal_end_time = 0
        
        # 重新计算格子大小和偏移（用于迷你地图）
        self.cell_size = self.calculate_cell_size()
        self.update_maze_offsets()
        
        print(f"第{level_index+1}关加载完成")
        print(f"迷宫尺寸: {self.maze.width}×{self.maze.height}")
        print(f"需要收集钥匙: {self.player.total_keys_in_level}把")
        print(f"幽灵追踪半径: {LEVEL_GHOST_CHASE_RADIUS[level_index]}单位")
        print(f"当前生命值: {self.player.lives}")
    
    def toggle_mini_map(self):
        """切换右上角2D缩略图的显示状态（调试功能，与地图拾取无关）"""
        if self.mini_map_fade_state == "none" or self.mini_map_fade_state == "visible":
            # 开始淡入或淡出
            if self.show_mini_map:
                # 当前显示，开始淡出
                self.mini_map_fade_state = "fade_out"
                self.mini_map_fade_timer = 0
                print("调试: 隐藏2D缩略图...")
            else:
                # 当前隐藏，开始淡入
                self.mini_map_fade_state = "fade_in"
                self.mini_map_fade_timer = 0
                self.show_mini_map = True
                print("调试: 显示2D缩略图...")
            
    def update_mini_map_fade(self, dt):
        """更新迷你地图的淡入淡出效果"""
        if self.mini_map_fade_state == "none":
            return
            
        self.mini_map_fade_timer += dt * 1000  # 转换为毫秒
        
        if self.mini_map_fade_state == "fade_in":
            # 淡入：透明度从0增加到255
            progress = min(1.0, self.mini_map_fade_timer / MINI_MAP_FADE_DURATION)
            self.mini_map_alpha = int(progress * 255)
            
            if progress >= 1.0:
                self.mini_map_fade_state = "visible"
                self.mini_map_alpha = 255
                print("2D缩略图完全显示")
                
        elif self.mini_map_fade_state == "fade_out":
            # 淡出：透明度从255减少到0
            progress = min(1.0, self.mini_map_fade_timer / MINI_MAP_FADE_DURATION)
            self.mini_map_alpha = int((1.0 - progress) * 255)
            
            if progress >= 1.0:
                self.mini_map_fade_state = "none"
                self.mini_map_alpha = 0
                self.show_mini_map = False
                print("2D缩略图完全隐藏")
    
    def toggle_pause(self):
        """切换游戏暂停状态"""
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            audio_manager.pause()
            print("游戏已暂停")
        else:
            audio_manager.resume()
            print("游戏继续")
    
    def check_level_completion(self):
        """检查是否完成当前关卡 - 简化逻辑"""
        # 如果玩家已经到达出口或正在渐变过渡中，不再检查
        if self.player.reached_exit or self.player.fade_state != "none":
            return False
        
        # 检查是否满足通关条件：在出口区域、收集齐钥匙、按E键
        if (self.player.trigger_active and 
            self.maze.get_all_keys_collected()):
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_e]:  # 按E键触发通关
                self.player.reached_exit = True
                
                if self.current_level < TOTAL_LEVELS - 1:
                    # 不是最后一关，进入下一关
                    next_level = self.current_level + 1
                    print(f"第{self.current_level+1}关通过！准备进入第{next_level+1}关...")
                    self.player.start_fade_out("level_transition", next_level)
                    return True
                else:
                    # 最后一关完成，游戏胜利
                    self.game_won = True
                    print("恭喜！通关所有关卡！")
                    return True
        
        return False
    
    def handle_level_transition(self):
        """处理关卡过渡 - 简化逻辑"""
        # 只在黑暗状态且是关卡过渡时处理
        if (self.player.fade_state == "dark" and 
            hasattr(self.player, 'next_level_index') and 
            self.player.next_level_index is not None):
            
            next_level = self.player.next_level_index
            
            if next_level < TOTAL_LEVELS:
                # 加载下一关
                print(f"正在加载第{next_level+1}关...")
                self.load_level(next_level)
                # 开始渐变恢复
                self.player.start_fade_in("level_transition")
                print(f"第{next_level+1}关加载完成，开始游戏！")
            else:
                # 游戏胜利，不需要再渐变恢复
                self.player.fade_state = "none"
                self.player.fade_alpha = 0
                print("所有关卡通关！")
                
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:  # F键切换全屏
                    self.toggle_fullscreen()
                elif event.key == pygame.K_r:  # R键重新开始游戏
                    self.restart_game()
                elif event.key == pygame.K_ESCAPE:  # ESC键退出
                    return False
                elif event.key == pygame.K_SPACE:  # 新增：空格键暂停/继续
                    if not self.player.game_over and not self.game_won:
                        self.toggle_pause()
                elif event.key == pygame.K_m and pygame.key.get_mods() & pygame.KMOD_CTRL:  # Ctrl+M切换2D缩略图
                    self.toggle_mini_map()
        
        return True
    
    def restart_game(self):
        """重新开始游戏（从第一关开始）"""
        self.__init__()
        print("游戏已重新开始！")
    
    def toggle_fullscreen(self):
        """切换全屏模式（根据参考文档2修改）"""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            # 更新窗口尺寸
            global WIDTH, HEIGHT
            WIDTH, HEIGHT = screen.get_size()
        else:
            screen = pygame.display.set_mode((BASE_WINDOW_WIDTH, BASE_WINDOW_HEIGHT))
            WIDTH, HEIGHT = BASE_WINDOW_WIDTH, BASE_WINDOW_HEIGHT
        
        # 更新视图尺寸 - 根据show_2d状态决定
        if self.show_2d:
            self.view_width = WIDTH // 2
        else:
            self.view_width = WIDTH
        
        self.view_height = HEIGHT
        
        # 更新迷你地图偏移（重新计算居中位置）
        self.cell_size = self.calculate_cell_size()
        self.update_maze_offsets()
        
        # 确保光标保持隐藏
        pygame.mouse.set_visible(False)
        
        print(f"切换到{'全屏' if self.fullscreen else '窗口'}模式: {WIDTH}x{HEIGHT}")
        
    def _draw_sprite_icon(self, surface, rect, sprite_matrix, color, pixel_scale=2):
        """
        绘制8x8像素图标
        rect: 图标的位置和大小（PyGame Rect对象）
        sprite_matrix: 8x8的二维矩阵，1表示绘制，0表示透明
        color: 绘制颜色
        pixel_scale: 像素放大倍数
        """
        # 计算每个像素在图标中的大小
        pixel_width = rect.width // 8
        pixel_height = rect.height // 8
        
        # 确保像素大小至少为1
        pixel_width = max(1, pixel_width)
        pixel_height = max(1, pixel_height)
        
        # 计算图标在surface中的起始位置（居中）
        start_x = rect.x + (rect.width - pixel_width * 8) // 2
        start_y = rect.y + (rect.height - pixel_height * 8) // 2
        
        # 遍历8x8矩阵并绘制像素
        for y in range(8):
            for x in range(8):
                if sprite_matrix[y][x] == 1:
                    pixel_rect = pygame.Rect(
                        start_x + x * pixel_width,
                        start_y + y * pixel_height,
                        pixel_width,
                        pixel_height
                    )
                    pygame.draw.rect(surface, color, pixel_rect)

    def draw_game_status(self, surface):
        """绘制游戏状态信息（左上角状态栏）"""
        # 使用pygame.display.get_surface()获取当前屏幕尺寸
        current_screen = pygame.display.get_surface()
        if not current_screen:
            return
        
        screen_width, screen_height = current_screen.get_size()
        
        # 创建状态栏背景（左上角区域）
        status_width = 230  # 宽度调整为显示更多信息
        status_height = 170  # #高度调整为显示更多信息
        status_surface = pygame.Surface((status_width, status_height), pygame.SRCALPHA)
        pygame.draw.rect(status_surface, (20, 25, 40, 200), (0, 0, status_width, status_height), border_radius=5)
        pygame.draw.rect(status_surface, (60, 70, 100, 200), (0, 0, status_width, status_height), 2, border_radius=5)
    
        # 绘制渐变覆盖层（用于被抓、关卡过渡等效果）
        if self.player.fade_alpha > 0:
            # 获取当前屏幕尺寸
            screen_width, screen_height = surface.get_size()
            fade_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, self.player.fade_alpha))
            surface.blit(fade_surface, (0, 0))
            
            # 在渐变层上显示文字
            if self.player.fade_state in ["fading_out", "dark", "fading_in", "level_transition_out", "level_transition_in"]:
                if hasattr(self.player, 'level_transition_text'):
                    # 根据状态显示不同的文字
                    if self.player.fade_state == "fading_out" or self.player.fade_state == "fading_in":
                        text_content = "被幽灵抓住了！"
                        text_color = (255, 100, 100)
                    elif self.player.fade_state == "level_transition_out":
                        if hasattr(self.player, 'next_level_index') and self.player.next_level_index < TOTAL_LEVELS:
                            text_content = f"第{self.current_level+1}关通过！"
                            text_color = (100, 255, 100)
                        else:
                            text_content = "恭喜！通关所有关卡！"
                            text_color = (255, 215, 0)
                    else:
                        text_content = getattr(self.player, 'level_transition_text', "")
                        text_color = (255, 255, 255)
    
        # 绘制生命值UI - 使用文本和爱心图标
        lives_text = font_normal.render("生命: ", True, LEVEL_COLORS[self.current_level]['lives_ui'])
        status_surface.blit(lives_text, (10, 15))
        
        # 绘制爱心图标
        heart_x = 10 + lives_text.get_width() + 5
        heart_sprite = self.maze.heart.sprite_2d if self.maze and self.maze.heart else self._get_default_heart_sprite()
        
        # 绘制所有爱心（每个爱心20x20像素）
        for i in range(self.player.lives):
            heart_rect = pygame.Rect(heart_x + i * 25, 10, 20, 20)
            self._draw_sprite_icon(
                status_surface, 
                heart_rect, 
                heart_sprite,
                LEVEL_COLORS[self.current_level]['heart_ui'],
                pixel_scale=2
            )
        
        # 绘制钥匙状态UI - 显示本关收集进度
        keys_collected = self.maze.get_keys_collected_count()
        keys_total = self.maze.get_total_keys_count()
        key_status_text = f"钥匙: {keys_collected}/{keys_total}"
        key_status = font_normal.render(key_status_text, True, LEVEL_COLORS[self.current_level]['key_ui'])
        status_surface.blit(key_status, (10, 45))
        
        # 绘制钥匙图标 - 绘制所有钥匙，已收集的用彩色，未收集的用灰色
        key_icon_x = 10 + key_status.get_width() + 5
        key_sprite = self.maze.keys[0].sprite_2d if self.maze and self.maze.keys else self._get_default_key_sprite()
        
        for i in range(keys_total):
            key_icon_rect = pygame.Rect(key_icon_x + i * 25, 40, 20, 20)
            if i < keys_collected:
                # 已收集的钥匙使用彩色
                key_color = LEVEL_COLORS[self.current_level]['key_ui']
            else:
                # 未收集的钥匙使用灰色
                key_color = (100, 100, 100)
            
            self._draw_sprite_icon(
                status_surface,
                key_icon_rect,
                key_sprite,
                key_color,
                pixel_scale=2
            )
        
        # 绘制地图状态
        map_status_text = "地图: "
        if self.player.map_collected:
            map_status_text += "已获取"
            map_color = LEVEL_COLORS[self.current_level]['map_ui']
        else:
            map_status_text += "未获取"
            map_color = (100, 100, 100)
        
        map_text = font_normal.render(map_status_text, True, map_color)
        status_surface.blit(map_text, (10, 75))
        
        # 绘制地图图标
        map_icon_x = 10 + map_text.get_width() + 5
        map_sprite = self.maze.map_item.sprite_2d if self.maze and self.maze.map_item else self._get_default_map_sprite()
        map_rect = pygame.Rect(map_icon_x, 70, 20, 20)
        
        self._draw_sprite_icon(
            status_surface,
            map_rect,
            map_sprite,
            map_color,
            pixel_scale=2
        )
        
        # 绘制关卡进度
        level_progress = font_normal.render(f"关卡: {self.current_level+1}/{TOTAL_LEVELS}", True, LEVEL_COLORS[self.current_level]['text'])
        status_surface.blit(level_progress, (10, 105))
            
        # 绘制幽灵警示信息（当玩家进入追踪半径时，显示闪动的“HAUNTED”）
        if self.maze.ghost and self.player.near_ghost and not self.player.reached_exit and not self.player.game_over:
            # 计算闪动效果：基于时间的正弦函数，使透明度在128到255之间循环
            flash_factor = int(128 * (1 + math.sin(pygame.time.get_ticks() * 0.01)))  # 0.01控制闪动速度
            alpha = max(128, min(255, flash_factor))  # 将值限制在128-255之间，确保最低可见度

            # 创建带有闪动透明度的红色（255, 0, 0）
            flash_color = (255, 0, 0, alpha)

            # 加载或使用粗体字体（假设存在 font_bold）
            # 如果不存在粗体字体，可以使用默认字体并设置粗体属性，这里假设已定义 font_bold
            haunted_text = font_bold.render("HAUNTED", True, (255, 0, 0))  # 先渲染不透明的文本
            # 创建一个带透明度的表面来实现闪动
            haunted_surface = pygame.Surface(haunted_text.get_size(), pygame.SRCALPHA)
            haunted_text_with_alpha = font_bold.render("HAUNTED", True, flash_color)
            haunted_surface.blit(haunted_text_with_alpha, (0, 0))

            # 计算在状态栏内的绘制位置（位于“关卡”信息下方，大约y=135的位置）
            # 状态栏左上角坐标是 (10, 10)，所以内部y坐标135对应屏幕y坐标145
            text_x = 10
            text_y = 135  # 状态栏内部y坐标

            # 将闪动的“HAUNTED”字样绘制到状态栏表面
            status_surface.blit(haunted_surface, (text_x, text_y))
        
        # 将状态栏绘制到主屏幕左上角
        surface.blit(status_surface, (10, 10))
        
        # 如果地图正在显示，显示倒计时
        if self.player.map_visible and self.show_mini_map:
            current_time = pygame.time.get_ticks()
            time_left = max(0, MAP_REVEAL_DURATION - (current_time - self.player.map_reveal_timer))
            seconds_left = time_left // 1000 + 1
            
            if seconds_left <= 5:  # 最后5秒显示倒计时
                countdown_text = font_small.render(f"地图显示: {seconds_left}秒", True, (255, 100, 100))
                countdown_rect = countdown_text.get_rect(topright=(screen_width - 10, 10))
                
                # 绘制倒计时背景
                countdown_bg = pygame.Surface((countdown_text.get_width() + 10, countdown_text.get_height() + 5), pygame.SRCALPHA)
                pygame.draw.rect(countdown_bg, (0, 0, 0, 150), countdown_bg.get_rect(), border_radius=3)
                surface.blit(countdown_bg, (screen_width - 20 - countdown_text.get_width(), 8))
                
                surface.blit(countdown_text, (screen_width - countdown_text.get_width() - 15, 10))
        
    def _get_default_heart_sprite(self):
        """获取默认爱心像素矩阵"""
        return [
            [0, 1, 1, 0, 0, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]

    def _get_default_key_sprite(self):
        """获取默认钥匙像素矩阵"""
        return [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 0, 0, 0],
            [1, 0, 0, 1, 0, 0, 0, 0],
            [1, 0, 0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]

    def _get_default_map_sprite(self):
        """获取默认地图像素矩阵"""
        return [
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 0, 0, 1, 1, 0],
            [1, 1, 0, 1, 1, 0, 1, 1],
            [1, 1, 0, 1, 1, 0, 1, 1],
            [0, 1, 1, 0, 0, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0]
        ]
        
    def draw_mini_map(self, surface):
        """绘制右上角迷你地图（2D缩略图）"""
        if not self.show_mini_map or self.mini_map_alpha <= 0:
            return
        
        # 使用pygame.display.get_surface()获取当前屏幕尺寸
        current_screen = pygame.display.get_surface()
        if not current_screen:
            return
        
        screen_width, screen_height = current_screen.get_size()
        
        # 计算位置（右上角，带边距）
        mini_map_x = screen_width - MINI_MAP_SIZE - MINI_MAP_MARGIN
        mini_map_y = MINI_MAP_MARGIN
        
        # 创建半透明背景
        mini_map_surface = pygame.Surface((MINI_MAP_SIZE, MINI_MAP_SIZE), pygame.SRCALPHA)
        
        # 设置透明度
        if self.mini_map_alpha < 255:
            mini_map_surface.set_alpha(self.mini_map_alpha)
        
        # 绘制背景
        pygame.draw.rect(mini_map_surface, (30, 35, 50, 200), 
                        (0, 0, MINI_MAP_SIZE, MINI_MAP_SIZE), border_radius=5)
        pygame.draw.rect(mini_map_surface, (60, 70, 100), 
                        (0, 0, MINI_MAP_SIZE, MINI_MAP_SIZE), 2, border_radius=5)
        
        # 动态计算格子大小
        cell_size = self.calculate_cell_size()
        maze_offset_x = (MINI_MAP_SIZE - self.maze.width * cell_size) // 2
        maze_offset_y = (MINI_MAP_SIZE - self.maze.height * cell_size) // 2
        
        # 绘制迷宫
        for x in range(self.maze.width):
            for y in range(self.maze.height):
                rect = pygame.Rect(
                    maze_offset_x + x * cell_size,
                    maze_offset_y + y * cell_size,
                    cell_size, cell_size
                )
                if self.maze.grid[x, y] == 1:
                    # 墙壁
                    pygame.draw.rect(mini_map_surface, LEVEL_COLORS[self.current_level]['wall'], rect)
                else:
                    # 路径
                    pygame.draw.rect(mini_map_surface, LEVEL_COLORS[self.current_level]['path'], rect)
                    pygame.draw.rect(mini_map_surface, (40, 40, 50), rect, 1)
        
        # 绘制出口
        if self.maze.exit_pos:
            exit_x, exit_y = self.maze.exit_pos
            exit_rect = pygame.Rect(
                maze_offset_x + exit_x * cell_size,
                maze_offset_y + exit_y * cell_size,
                cell_size, cell_size
            )
            # 出口颜色保持不变
            pygame.draw.rect(mini_map_surface, LEVEL_COLORS[0]['exit'], exit_rect)
            
            # 绘制出口标记
            try:
                exit_text = font_small.render("E", True, (0, 0, 0))
                text_rect = exit_text.get_rect(center=exit_rect.center)
                mini_map_surface.blit(exit_text, text_rect)
            except:
                pygame.draw.line(mini_map_surface, (0, 0, 0), exit_rect.topleft, exit_rect.bottomright, 1)
                pygame.draw.line(mini_map_surface, (0, 0, 0), exit_rect.topright, exit_rect.bottomleft, 1)
        
        # 绘制玩家
        player_x = maze_offset_x + self.player.x * cell_size
        player_y = maze_offset_y + self.player.y * cell_size
        player_radius = max(2, int(cell_size * 0.3))
        pygame.draw.circle(mini_map_surface, LEVEL_COLORS[self.current_level]['player'], 
                          (int(player_x), int(player_y)), player_radius)
        
        # 绘制玩家朝向
        end_x = player_x + math.cos(self.player.angle) * player_radius * 2
        end_y = player_y + math.sin(self.player.angle) * player_radius * 2
        pygame.draw.line(mini_map_surface, (255, 255, 255), 
                        (player_x, player_y), (end_x, end_y), 1)
        
        # 绘制幽灵（如果存在）
        if self.maze.ghost:
            ghost_x = maze_offset_x + self.maze.ghost.x * cell_size
            ghost_y = maze_offset_y + self.maze.ghost.y * cell_size
            ghost_radius = max(2, int(cell_size * 0.4))
            pygame.draw.circle(mini_map_surface, LEVEL_COLORS[self.current_level]['ghost'], 
                              (int(ghost_x), int(ghost_y)), ghost_radius)
        
        # 绘制未收集的钥匙
        for key in self.maze.keys:
            if not key.collected:
                key_x = maze_offset_x + key.x * cell_size
                key_y = maze_offset_y + key.y * cell_size
                key_size = max(2, int(cell_size * 0.6))
                # 绘制钥匙图标（简化版）
                key_rect = pygame.Rect(key_x - key_size//2, key_y - key_size//2, key_size, key_size)
                pygame.draw.rect(mini_map_surface, LEVEL_COLORS[self.current_level]['key'], key_rect, border_radius=2)
        
        # 绘制未收集的爱心
        if self.maze.heart and not self.maze.heart.collected:
            heart_x = maze_offset_x + self.maze.heart.x * cell_size
            heart_y = maze_offset_y + self.maze.heart.y * cell_size
            heart_size = max(2, int(cell_size * 0.6))
            # 绘制爱心图标（简化版）
            pygame.draw.circle(mini_map_surface, LEVEL_COLORS[self.current_level]['heart'], 
                              (int(heart_x), int(heart_y)), heart_size//2)
        
        # 绘制未收集的地图
        if self.maze.map_item and not self.maze.map_item.collected:
            map_x = maze_offset_x + self.maze.map_item.x * cell_size
            map_y = maze_offset_y + self.maze.map_item.y * cell_size
            map_size = max(2, int(cell_size * 0.6))
            # 绘制地图图标（简化版）
            map_rect = pygame.Rect(map_x - map_size//2, map_y - map_size//2, map_size, map_size)
            pygame.draw.rect(mini_map_surface, LEVEL_COLORS[self.current_level]['map'], 
                            map_rect, border_radius=3)
        
        # 绘制标题
        title = font_small.render(f"第{self.current_level+1}关地图", True, LEVEL_COLORS[self.current_level]['text'])
        mini_map_surface.blit(title, (MINI_MAP_SIZE//2 - title.get_width()//2, 5))
        
        # 绘制到主屏幕
        surface.blit(mini_map_surface, (mini_map_x, mini_map_y))
        
        # 如果地图即将消失，显示倒计时
        if self.player.map_visible:
            current_time = pygame.time.get_ticks()
            time_left = max(0, MAP_REVEAL_DURATION - (current_time - self.player.map_reveal_timer))
            seconds_left = time_left // 1000 + 1
            
            if seconds_left <= 5:  # 最后5秒显示倒计时
                countdown_text = font_small.render(f"{seconds_left}", True, (255, 100, 100))
                countdown_rect = countdown_text.get_rect(center=(mini_map_x + MINI_MAP_SIZE//2, 
                                                                mini_map_y + MINI_MAP_SIZE - 15))
                surface.blit(countdown_text, countdown_rect)
    
    def draw_3d_view(self, surface):
        """绘制3D视图 - 适应窗口比例"""
        # 直接使用传入的surface的尺寸（应该是全屏或窗口的尺寸）
        screen_width, screen_height = surface.get_size()
        
        # 使用整个屏幕绘制3D视图
        view_surface = pygame.Surface((screen_width, screen_height))
        
        # 使用当前关卡的天空和地板颜色
        sky_color_top = LEVEL_COLORS[self.current_level]['sky_top']
        sky_color_bottom = LEVEL_COLORS[self.current_level]['sky_bottom']
        floor_color = LEVEL_COLORS[self.current_level]['floor']
        
        # 按俯仰偏移动态设置地平线
        horizon_y = int(screen_height // 2 + self.player.pitch)
        horizon_y = max(0, min(screen_height, horizon_y))

        # 绘制天空渐变（地平线以上）
        sky_height = max(1, horizon_y)
        for y in range(horizon_y):
            # 计算渐变因子 (0 到 1)
            t = y / sky_height if sky_height > 0 else 0
            # 从顶部颜色渐变到底部颜色
            r = int(sky_color_top[0] * (1 - t) + sky_color_bottom[0] * t)
            g = int(sky_color_top[1] * (1 - t) + sky_color_bottom[1] * t)
            b = int(sky_color_top[2] * (1 - t) + sky_color_bottom[2] * t)
            
            pygame.draw.line(view_surface, (r, g, b), (0, y), (screen_width, y))
        
        # 绘制地板（保持纯色）
        pygame.draw.rect(view_surface, floor_color, (0, horizon_y, screen_width, screen_height - horizon_y))
        
        # 检查游戏状态
        if self.is_paused:
            # 绘制暂停界面
            self.draw_normal_game_view(view_surface, screen_width, screen_height)
            self.draw_pause_screen(view_surface, screen_width, screen_height)
        elif self.player.game_over:
            # 游戏失败界面
            self.draw_game_over_screen(view_surface, screen_width, screen_height)
        elif self.game_won:
            # 游戏胜利界面
            self.draw_game_won_screen(view_surface, screen_width, screen_height)
        elif self.player.reached_exit:
            # 关卡通过界面（等待进入下一关）
            self.draw_level_complete_screen(view_surface, screen_width, screen_height)
        elif self.player.fade_state == "none":
            # 正常游戏状态
            self.draw_normal_game_view(view_surface, screen_width, screen_height)
        else:
            # 渐变过渡状态，仍然绘制正常视图
            self.draw_normal_game_view(view_surface, screen_width, screen_height)
        
        # 将3D视图绘制到主屏幕
        surface.blit(view_surface, (0, 0))
        
        # 绘制左上角游戏状态信息
        self.draw_game_status(surface)
        
        # 绘制右上角迷你地图（如果应该显示）
        self.draw_mini_map(surface)
    
    def draw_normal_game_view(self, view_surface, screen_width, screen_height):
        """绘制正常游戏状态下的3D视图 - 适应任意尺寸"""
        # 获取射线距离和击中信息
        wall_distances, hit_exits = self.player.get_ray_distances()
        horizon_y = int(screen_height // 2 + self.player.pitch)
        horizon_y = max(0, min(screen_height, horizon_y))
        
        # 计算每条射线的线段宽度，基于屏幕宽度
        line_width = screen_width / RAY_COUNT
        
        # 1. 先绘制墙壁（背景层）
        for i in range(RAY_COUNT):
            wall_dist = wall_distances[i]
            hit_exit = hit_exits[i]
            
            if wall_dist < MAX_VIEW_DISTANCE:
                # 根据距离计算墙壁线段高度
                wall_height = min(screen_height, screen_height * 0.8 / (wall_dist + 0.1))
                
                # 根据距离计算亮度
                brightness = max(50, 255 - wall_dist * 2)
                
                # 选择颜色：如果击中出口，使用绿色，否则使用关卡墙壁颜色
                if hit_exit:
                    # 出口颜色保持不变（使用第一关的出口颜色）
                    color = LEVEL_COLORS[0]['exit']
                else:
                    # 使用当前关卡的墙壁颜色，并根据距离调整亮度
                    wall_color = LEVEL_COLORS[self.current_level]['wall']
                    r = int(wall_color[0] * brightness / 255)
                    g = int(wall_color[1] * brightness / 255)
                    b = int(wall_color[2] * brightness / 255)
                    color = (r, g, b)
                
                # 计算线段的顶部和底部位置
                wall_top = int(horizon_y - wall_height / 2)
                wall_bottom = wall_top + wall_height
                
                # 绘制墙壁线段
                pygame.draw.rect(view_surface, color, 
                                (i * line_width, wall_top, line_width + 1, wall_height))
        
        # 2. 绘制幽灵（使用优化后的3D精灵绘制）
        if self.maze.ghost and not self.player.game_over:
            self.maze.ghost.draw_3d_sprite(view_surface, 
                                          self.player.x, self.player.y, 
                                          self.player.angle, FOV, 
                                          screen_width, screen_height,
                                          wall_distances, line_width,
                                          self.player.pitch)
        
        # 3. 绘制所有钥匙（3D视图）
        for key in self.maze.keys:
            if not key.collected:
                key.draw_3d_sprite(view_surface,
                                  self.player.x, self.player.y,
                                  self.player.angle, FOV,
                                  screen_width, screen_height,
                                  wall_distances, line_width,
                                  self.player.pitch)
        
        # 4. 绘制爱心（3D视图）
        if self.maze.heart and not self.maze.heart.collected:
            self.maze.heart.draw_3d_sprite(view_surface,
                                          self.player.x, self.player.y,
                                          self.player.angle, FOV,
                                          screen_width, screen_height,
                                          wall_distances, line_width,
                                          self.player.pitch)
        
        # 5. 绘制地图道具（3D视图）- 新增
        if self.maze.map_item and not self.maze.map_item.collected:
            self.maze.map_item.draw_3d_sprite(view_surface,
                                             self.player.x, self.player.y,
                                             self.player.angle, FOV,
                                             screen_width, screen_height,
                                             wall_distances, line_width,
                                             self.player.pitch)
    
    def draw_pause_screen(self, view_surface, screen_width, screen_height):
        """绘制暂停界面"""
        # 半透明黑色背景
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        view_surface.blit(overlay, (0, 0))
        
        # 暂停文字
        pause_text = font_large.render("游戏暂停", True, (255, 255, 255))
        text_rect = pause_text.get_rect(center=(screen_width//2, screen_height//2 - 50))
        view_surface.blit(pause_text, text_rect)
        
        # 提示继续
        resume_text = font_normal.render("按 空格键 继续游戏", True, (200, 200, 200))
        resume_rect = resume_text.get_rect(center=(screen_width//2, screen_height//2 + 20))
        view_surface.blit(resume_text, resume_rect)
        
        # 显示控制提示
        hint_text = font_small.render("按 R 键重新开始 | 按 ESC 键退出游戏", True, (150, 150, 150))
        hint_rect = hint_text.get_rect(center=(screen_width//2, screen_height//2 + 60))
        view_surface.blit(hint_text, hint_rect)
                                         
    def draw_game_over_screen(self, view_surface, screen_width, screen_height):
        """绘制游戏结束界面"""
        # 半透明黑色背景
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        view_surface.blit(overlay, (0, 0))
        
        # 游戏结束文字
        game_over_text = font_large.render("游戏结束", True, (255, 50, 50))
        text_rect = game_over_text.get_rect(center=(screen_width//2, screen_height//2 - 50))
        view_surface.blit(game_over_text, text_rect)
        
        # 提示重新开始
        restart_text = font_normal.render("按 R 键重新开始游戏", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(screen_width//2, screen_height//2 + 20))
        view_surface.blit(restart_text, restart_rect)
        
        # 显示最终成绩
        score_text = font_normal.render(f"最终关卡: 第{self.current_level+1}关", True, (200, 200, 200))
        score_rect = score_text.get_rect(center=(screen_width//2, screen_height//2 + 60))
        view_surface.blit(score_text, score_rect)

    def draw_game_won_screen(self, view_surface, screen_width, screen_height):
        """绘制游戏胜利界面"""
        # 半透明绿色背景
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 50, 0, 180))
        view_surface.blit(overlay, (0, 0))
        
        # 胜利文字
        victory_text = font_large.render("恭喜通关！", True, (255, 215, 0))
        text_rect = victory_text.get_rect(center=(screen_width//2, screen_height//2 - 50))
        view_surface.blit(victory_text, text_rect)
        
        # 显示通关信息
        info_text = font_normal.render("你成功通过了所有三关迷宫！", True, (200, 255, 200))
        info_rect = info_text.get_rect(center=(screen_width//2, screen_height//2 + 10))
        view_surface.blit(info_text, info_rect)
        
        # 提示重新开始
        restart_text = font_normal.render("按 R 键重新开始游戏", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(screen_width//2, screen_height//2 + 60))
        view_surface.blit(restart_text, restart_rect)

    def draw_level_complete_screen(self, view_surface, screen_width, screen_height):
        """绘制关卡完成界面"""
        # 半透明蓝色背景
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 50, 150))
        view_surface.blit(overlay, (0, 0))
        
        # 关卡完成文字
        if self.current_level < TOTAL_LEVELS - 1:
            level_text = font_large.render(f"第{self.current_level+1}关完成！", True, (100, 255, 100))
            next_text = font_normal.render("正在进入下一关...", True, (200, 255, 200))
        else:
            level_text = font_large.render("最终关卡完成！", True, (255, 215, 0))
            next_text = font_normal.render("正在计算最终成绩...", True, (200, 255, 200))
        
        level_rect = level_text.get_rect(center=(screen_width//2, screen_height//2 - 30))
        next_rect = next_text.get_rect(center=(screen_width//2, screen_height//2 + 20))
        
        view_surface.blit(level_text, level_rect)
        view_surface.blit(next_text, next_rect)
        
        # 显示本关成绩
        keys_text = font_normal.render(f"收集钥匙: {self.maze.get_keys_collected_count()}/{self.maze.get_total_keys_count()}", 
                                      True, (200, 200, 255))
        lives_text = font_normal.render(f"剩余生命: {self.player.lives}", True, (200, 200, 255))
        
        keys_rect = keys_text.get_rect(center=(screen_width//2, screen_height//2 + 70))
        lives_rect = lives_text.get_rect(center=(screen_width//2, screen_height//2 + 100))
        
        view_surface.blit(keys_text, keys_rect)
        view_surface.blit(lives_text, lives_rect)
    
    def update(self, dt):
        """更新游戏状态"""
        # 如果游戏暂停，不更新游戏逻辑
        if self.is_paused:
            return
        
        # 如果游戏胜利或失败，不更新游戏逻辑
        if self.game_won or self.player.game_over:
            return
            
        # 处理键盘输入
        keys = pygame.key.get_pressed()
        
        # 检查是否完成当前关卡
        self.check_level_completion()
        
        # 处理关卡过渡
        self.handle_level_transition()
        
        # 获取鼠标相对移动
        mouse_rel = pygame.mouse.get_rel()
        
        # 如果启用了鼠标控制，将鼠标重置到屏幕中心，避免到达边界
        if self.player.mouse_control:
            # 使用pygame.display.get_surface()获取当前屏幕尺寸
            current_screen = pygame.display.get_surface()
            if current_screen:
                screen_width, screen_height = current_screen.get_size()
                pygame.mouse.set_pos((screen_width // 2, screen_height // 2))
        
        # 更新玩家状态
        self.player.update(keys, mouse_rel, dt)
        
        # 如果玩家正在渐变过渡中，不更新幽灵和道具
        if self.player.fade_state != "none":
            # 但需要更新渐变效果
            self.player.update_fade(dt)
            return
            
        # 更新幽灵动画和移动（使用A*算法优化）
        if self.maze.ghost:
            self.maze.ghost.update(dt, self.player.x, self.player.y)
        
        # 更新所有钥匙动画
        for key in self.maze.keys:
            key.update(dt, self.player.x, self.player.y)
        
        # 更新爱心动画
        if self.maze.heart:
            self.maze.heart.update(dt, self.player.x, self.player.y)
        
        # 更新地图道具动画
        if self.maze.map_item:
            self.maze.map_item.update(dt, self.player.x, self.player.y)
        
        # 更新迷你地图淡入淡出效果
        self.update_mini_map_fade(dt)
        
        # 响应地图显示状态：自动显示或自动隐藏迷你地图
        if self.player.map_collected:
            if self.player.map_visible and not self.show_mini_map:
                # 状态为“需显示”，且当前未显示，则触发显示
                self.show_mini_map = True
                self.mini_map_fade_state = "fade_in"
                self.mini_map_fade_timer = 0
                self.mini_map_alpha = 0
                print("地图拾取后自动显示缩略图")
            elif not self.player.map_visible and self.show_mini_map:
                # 状态为“需隐藏”，且当前正显示，则触发隐藏
                # 注意：这里调用toggle_mini_map()会开始淡出流程
                self.toggle_mini_map()
                print("地图显示时间结束，自动隐藏缩略图")
        
        # 更新背景音乐音量（根据幽灵距离）
        if self.maze.ghost:
            audio_manager.update_music_volume(self.player.ghost_distance)
    
    def run(self):
        """主游戏循环"""
        clock = pygame.time.Clock()
        running = True
        
        print("游戏开始！")
        
        while running:
            dt = clock.tick(120) / 1000.0  # 转换为秒（刷新率）
            self.dt = dt
            
            # 处理事件
            running = self.handle_events()
            
            # 更新游戏状态
            self.update(dt)
            
            # 绘制游戏
            # 使用pygame.display.get_surface()获取当前屏幕
            current_screen = pygame.display.get_surface()
            if current_screen:
                current_screen.fill(LEVEL_COLORS[self.current_level]['bg'])
                
                # 只绘制3D视图（默认状态）
                self.draw_3d_view(current_screen)
            
            pygame.display.flip()
            
        # 游戏退出时清理音频
        audio_manager.stop_all()
        pygame.quit()
        sys.exit()
        
# 主程序入口
if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"游戏运行出错: {e}")
        import traceback
        traceback.print_exc()
        # 确保出错时也清理资源
        audio_manager.stop_all()
        pygame.quit()
        sys.exit()