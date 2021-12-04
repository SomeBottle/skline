from view import View

if __name__ == '__main__':  # 不是作为模块调用
    game_view=View()
    game_view.first_page() # 显示初始页
    game_view.menu() # 显示游戏菜单
    print('Next Step')