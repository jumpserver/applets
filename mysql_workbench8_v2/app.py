import sys

if sys.platform == 'win32':
    from pywinauto.controls.uia_controls import (
        ButtonWrapper, EditWrapper, MenuItemWrapper
    )

from base import BaseApplication


class AppletApplication(BaseApplication):

    def run(self):
        menubar = self.app.window(title="MySQL Workbench", auto_id="MainForm", control_type="Window").child_window(
            title="Database", control_type="MenuItem")
        menubar.wait('ready', timeout=10, retry_interval=5)
        MenuItemWrapper(menubar.element_info).select()
        cdb = menubar.child_window(title="Connect to Database", control_type="MenuItem")
        cdb.wait('ready', timeout=10, retry_interval=5)
        MenuItemWrapper(cdb.element_info).click_input()

        # 输入 host
        host_ele = self.app.top_window().child_window(title="Host Name", auto_id="Host Name", control_type="Edit")
        EditWrapper(host_ele.element_info).set_edit_text(self.host)

        # 输入 port
        port_ele = self.app.top_window().child_window(title="Port", auto_id="Port", control_type="Edit")
        EditWrapper(port_ele.element_info).set_edit_text(self.port)

        # 输入 username
        user_ele = self.app.top_window().child_window(title="User Name", auto_id="User Name", control_type="Edit")
        EditWrapper(user_ele.element_info).set_edit_text(self.username)

        # 输入 db
        db_ele = self.app.top_window().child_window(title="Default Schema", auto_id="Default Schema",
                                                    control_type="Edit")
        EditWrapper(db_ele.element_info).set_edit_text(self.db)

        ok_ele = self.app.top_window().child_window(title="Connection", auto_id="Connection",
                                                    control_type="Window").child_window(title="OK",
                                                                                        control_type="Button")
        ButtonWrapper(ok_ele.element_info).click()

        # 输入 password
        password_ele = self.app.top_window().child_window(title="Password", auto_id="Password", control_type="Edit")
        password_ele.wait('ready', timeout=10, retry_interval=5)
        EditWrapper(password_ele.element_info).set_edit_text(self.password)

        ok_ele = self.app.top_window().child_window(title="Button Bar", auto_id="Button Bar",
                                                    control_type="Pane").child_window(title="OK", control_type="Button")
        ButtonWrapper(ok_ele.element_info).click()
