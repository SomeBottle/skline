# coding:utf-8
from view import BasicView

if __name__ == '__main__':  # 不是作为模块调用
    menu_view = BasicView()
    menu_view.first_page()  # 显示初始页
    menu_view.menu()  # 显示游戏菜单
    print('SomeBottle: Goodbye my friend~')
