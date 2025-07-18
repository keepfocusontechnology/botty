import os, sys
import keyboard
import subprocess
import locale
import template_finder
import cv2
import numpy as np
import mouse
import time
from PIL import ImageGrab
from utils.misc import wait, set_d2r_always_on_top,set_battle_always_on_top
from screen import get_offset_state, grab
from ui.main_menu import MAIN_MENU_MARKERS
from ui import main_menu



def process_exists(process_name):
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    # use buildin check_output right away
    output = subprocess.check_output(call).decode(locale.getpreferredencoding())
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())

def safe_exit(error_code=0):
    kill_game()
    os._exit(error_code)

def kill_game():
    while process_exists("D2R.exe"):
        os.system("taskkill /f /im  BlizzardError.exe")
        os.system("taskkill /f /im  D2R.exe")
        wait(1.0, 1.5)

def restart_game(d2r_path, launch_options):
    kill_game()
    wait(1.0, 1.5)
    # This method should function similar to opening the exe via double-click
    os.startfile(f"{d2r_path}/D2R.exe", arguments = launch_options)
    wait(4.4, 5.5)
    for _ in range(20):
        keyboard.send("space")
        wait(0.5, 1.0)
    success = False
    attempts = 0
    set_d2r_always_on_top()
    while not success:
        success = get_offset_state()
        wait(0.5, 1.0)

    while not template_finder.search(MAIN_MENU_MARKERS, grab(), best_match=True).valid:
        keyboard.send("space")
        wait(2.0, 4.0)
        attempts += 1
        if attempts >= 5:
            return False
    return True

def restart_game_v1():
    # 1.将暴雪战网的窗口突出在最前排
    # 2.找到暴雪战网左下角的启动游戏（蓝色按钮）
    # 3.点击启动游戏，并等待游戏启动
    set_battle_always_on_top()
    
    # 测试按钮点击
    button_path = "assets/templates/ui/battle/btn_battle_load_game.png"
    print("2秒后开始查找按钮...")
    time.sleep(2) 
    
    success = click_button_by_template(button_path)
    if not success:
        print("查找按钮失败")
        return False
    else:
        wait(4.4, 5.5)
        for _ in range(20):
            keyboard.send("space")
            wait(0.5, 1.0)
        success = False
        attempts = 0
        set_d2r_always_on_top()
        while not success:
            success = get_offset_state()
            wait(0.5, 1.0)

        while not template_finder.search(MAIN_MENU_MARKERS, grab(), best_match=True).valid:
            keyboard.send("space")
            wait(2.0, 4.0)
            attempts += 1
            if attempts >= 5:
                return False
        return True
    


def click_button_by_template(template_path, threshold=0.85, max_attempts=5, delay_between_attempts=1.0):
    """
    在屏幕上查找模板图像并点击对应的按钮（简化版，直接移动鼠标）
    
    参数:
        template_path: 模板图片路径
        threshold: 匹配阈值（0-1，默认0.85）
        max_attempts: 最大尝试次数（默认5次）
        delay_between_attempts: 尝试间隔时间（秒，默认1.0）
    
    返回:
        True: 成功点击；False: 未找到
    """
    # 读取模板图像
    template = cv2.imread(template_path)
    if template is None:
        print(f"错误：无法加载模板 {template_path}")
        return False
    
    h, w = template.shape[:2]  # 模板高、宽

    # 多次尝试查找
    for attempt in range(max_attempts):
        # 截取屏幕
        screenshot = ImageGrab.grab()
        screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # 模板匹配
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)  # 只关注最高匹配值和位置

        if max_val >= threshold:
            # 计算按钮中心点坐标
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            
            # 移动鼠标并点击
            mouse.move(center_x, center_y, duration=0.1)  # 0.1秒平滑移动
            time.sleep(0.05)  # 移动后稍等
            mouse.click('left')
            print(f"成功点击按钮（匹配度：{max_val:.2f}）")
            return True
        
        # 未找到则等待下次尝试
        print(f"尝试 {attempt+1}/{max_attempts}：未找到匹配（最高匹配度：{max_val:.2f}）")
        time.sleep(delay_between_attempts)
    
    print(f"超过最大尝试次数，未找到按钮")
    return False


# For testing
if __name__ == "__main__":
    restart_game_v1()
    print("游戏重启成功")
    time.sleep(3) 
    main_menu.start_game()
        
        

    # if len(sys.argv) > 1:
    #     result = restart_game(sys.argv[1])
    #     print(result)
    # else:
    #     result = restart_game()
    #     print(result)
  
