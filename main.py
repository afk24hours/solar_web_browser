#Thanks to https://icons8.com/
#Used their free icons for this small project
#Написано с помощью библиотеки PyQt5 и так же небольшой функционал от requests и bs4 для парсинга HTML кода
#Если нажали увидеть код страницы то придётся ждать пока полностью завершится процесс парсинга

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *

import sys
import os

import requests
from bs4 import BeautifulSoup

class AboutDialog(QDialog): 

    def __init__(self,*args,action_number,**kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowIcon(QIcon(os.path.join('icons','solar_icon.png')))
        Q_Button = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(Q_Button)
        self.buttonBox.accepted.connect(self.accept)
        self.action_number = action_number

        
        url_from_urlbar = self.url_from_urlbar
        #Shows About Dialog Window
        if self.action_number == 1:

            layout = QVBoxLayout()
            title = QLabel("Solar Web Browser")
            font = title.font()
            font.setPointSize(14)
            title.setFont(font)
            title.setAlignment( Qt.AlignHCenter )
            layout.addWidget(title)
            logo = QLabel()
            logo.setPixmap ( QPixmap (os.path.join('icons','solar_icon_128.png')))
            logo.setAlignment (Qt.AlignHCenter)
            layout.addWidget(logo)
            text_from_author = QLabel("Have fun!")
            text_from_author.move(200, 200)
            text_from_author.setAlignment(Qt.AlignHCenter)
            layout.addWidget(text_from_author)
            program_version = QLabel("Version 1.01")
            program_version.setAlignment(Qt.AlignHCenter)
            layout.addWidget(program_version)
            program_author = QLabel("(c) 2020 Serikbol's Imaginary Company.")
            program_author.setAlignment(Qt.AlignHCenter)
            layout.addWidget(program_author)
            layout.addWidget(self.buttonBox)
            self.setLayout(layout)
            self.show()


        #Shows HTML code Dialog Window 
        if self.action_number == 2:

            layout2 = QVBoxLayout()
            sample_html = requests.get(url_from_urlbar).text
            soup = BeautifulSoup(sample_html,'html.parser')
            text = (soup.prettify())
            code = QLabel()
            code.setText(text)
            font = code.font()
            code.setFont(QFont('Arial', 10)) 
            code.setTextFormat(Qt.PlainText)
            code.setStyleSheet("border: 1px solid black; background-color: grey; width: 480; height: 600") 
            code.setAlignment(Qt.AlignTop)
            code.setTextInteractionFlags(Qt.TextSelectableByMouse)
            scroll_area = QScrollArea(widgetResizable=True)
            scroll_area.setWidget(code)
            layout2.addWidget(scroll_area)
            self.setLayout(layout2)
            self.show()


class MainWindow(QMainWindow):

    htmlFinished = pyqtSignal() #for async events
    url_from_urlbar = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #Init tabs section
        self.tabs = QTabWidget()
        self.tabs.setTabShape(QTabWidget.Triangular)
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.new_tab_opened)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.setCentralWidget(self.tabs)
        navigation_toolbar = QToolBar("Navigation")
        self.addToolBar(navigation_toolbar)
        navigation_toolbar.setIconSize(QSize(32, 32))

        #Back button
        back_button = QAction(QIcon(os.path.join('icons','back_button.png')), "Back", self)
        back_button.setStatusTip("Go back")
        back_button.triggered.connect(lambda: self.tabs.currentWidget().back())
        navigation_toolbar.addAction(back_button)

        #Forward button
        forward_button = QAction(QIcon(os.path.join('icons','forward_button.png')), "Forward", self)
        forward_button.setStatusTip("Go forward")
        forward_button.triggered.connect(lambda: self.tabs.currentWidget().forward())
        navigation_toolbar.addAction(forward_button)

        #Refresh 
        refresh_button = QAction(QIcon(os.path.join('icons','refresh_button.png')), "Refresh", self)
        refresh_button.setStatusTip("Refresh current page")
        refresh_button.triggered.connect(lambda: self.tabs.currentWidget().reload())
        navigation_toolbar.addAction(refresh_button)

        #GoHomePage
        home_button = QAction(QIcon(os.path.join('icons','home_button.png')),"Home",self)
        home_button.setStatusTip("Go home page")
        home_button.triggered.connect(self.go_to_home)
        navigation_toolbar.addAction(home_button)
        
        navigation_toolbar.addSeparator() #separation

        #Security logo
        self.httpsicon = QLabel() 
        secure_pixmap = QPixmap(os.path.join('icons','secure_logo.png'))
        secure_pixmap = secure_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.httpsicon.setPixmap(secure_pixmap)
        navigation_toolbar.addWidget(self.httpsicon)

        #URL bar 
        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.go_to_website)
        navigation_toolbar.addWidget(self.urlbar)

        #Cancel button
        cancel_button = QAction(QIcon(os.path.join('icons','cancel_button.png')), "Cancel", self)
        cancel_button.setStatusTip("Stop loading current page")
        cancel_button.triggered.connect(lambda: self.tabs.currentWidget().stop())
        navigation_toolbar.addAction(cancel_button)

        self.menuBar().setNativeMenuBar(False)
        #Menu 
        main_menu = self.menuBar().addMenu('&File')

        #New Tab
        new_tab = QAction(QIcon(os.path.join('icons','new_tab_icon.png')),"New tab",self)
        new_tab.setStatusTip("New tab")
        new_tab.triggered.connect(lambda x: self.add_tab())
        main_menu.addAction(new_tab)

        #Open...
        open_file = QAction(QIcon(os.path.join('icons','open_file_icon.png')),"Open...",self)
        open_file.setStatusTip("Open selected page")
        open_file.triggered.connect(self.open_selected_file)
        main_menu.addAction(open_file)

        #Save...
        save_file = QAction(QIcon(os.path.join('icons','save_file_icon.png')),"Save as...",self)
        save_file.setStatusTip("Save current page")
        save_file.triggered.connect(self.save_current_file)
        main_menu.addAction(save_file)

        #Print...
        print_page = QAction( QIcon(os.path.join('icons','print_icon.png')), "Print...", self)
        print_page.setStatusTip("Print current page")
        print_page.triggered.connect(self.print_current_page)
        main_menu.addAction(print_page)

        #Help Menu
        help_menu = self.menuBar().addMenu("&Help")

        #About web browser
        about = QAction( QIcon (os.path.join('icons','solar_icon.png')), "About Solar", self)
        about.setStatusTip("About Solar web browser")
        about.triggered.connect(self.about_browser)
        help_menu.addAction(about)
        #Navigate to broswer's website 
        navigate = QAction( QIcon (os.path.join('icons','info_icon.png')), "Visit Solar website", self)
        navigate.setStatusTip("Visit Solar homepage")
        navigate.triggered.connect(self.navigate_to_solar)
        help_menu.addAction(navigate)
        #Page Elements
        page_elements = QAction( QIcon(os.path.join('icons','page_elements_icon.png')),"View page elements", self)
        page_elements.setStatusTip("View page elements")
        page_elements.triggered.connect(self.show_page_elements)
        help_menu.addAction(page_elements)


        self.add_tab(QUrl("https://www.google.com"),"Homepage")
        self.show()
        self.setWindowTitle("Solar")
        self.setWindowIcon(QIcon(os.path.join('icons','solar_icon.png')))
    
    #Adds tab to TabWidget
    def add_tab(self, url=None, label="Blank"):

        if url is None:
            url = QUrl("")

        browser = QWebEngineView()
        browser.setUrl(url)
        selected_tab = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(selected_tab)
        browser.urlChanged.connect(lambda url, browser=browser: self.update_urlbar(url, browser))
        #Tab title naming
        browser.loadFinished.connect(lambda _, i=selected_tab,
                                    browser=browser: self.tabs.setTabText(i,browser.page().title()) if browser.page().title() != 'about:blank' else _)  
    
    #Check if clicked empty space on tab bar
    def new_tab_opened(self,i):
        if i == -1:
            self.add_tab()

    #Set url in new tab
    def current_tab_changed(self,i):
        url = self.tabs.currentWidget().url()
        self.update_urlbar(url,self.tabs.currentWidget())

    #Close current tab
    def close_current_tab(self,tab_index):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(tab_index)

    #Navigate to Solar Homepage
    def navigate_to_solar(self):
        self.tabs.currentWidget().setUrl(QUrl("https://www.instagram.com/sxrxkbxl/"))

    #About that inits dialog box
    def about_browser(self):
        dialog = AboutDialog(self,action_number = 1)
        dialog.exec_()
    
    #Show page elements in side window
    def show_page_elements(self):
        dialog = AboutDialog(self,action_number = 2)
        dialog.exec_()

    #Function to open selected file. 
    def open_selected_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                        "Hypertext Markup Language (*.htm *.html);;"
                        "All files (*.*)")
        if filename:
            with open(filename, 'r', encoding = 'utf-8') as f:
                html = f.read()
            self.tabs.currentWidget().setHtml(html)
            self.urlbar.setText(filename)

    #Callback function to catch async signal
    def callback(self, html):
        self.mHtml = html
        self.htmlFinished.emit()

    #Save function. Catches save signal and encodes current page to HTML
    def save_current_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Page As", "", 
                        "Hypertext Markup Language (*.htm *.html);;" 
                        "All files(*.*)")
        if filename:
            self.tabs.currentWidget().toHtml(self.callback)
            loop = QEventLoop()
            self.htmlFinished.connect(loop.quit)
            loop.exec_()
            with open(filename, 'wb') as f:
                f.write(self.mHtml.encode('utf8'))
    
    #Init a dialog window with print settings (works in Windows 10, not sure about other OS)
    def print_current_page(self):
        dialog = QPrintDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.text.document().print_(dialog.printer()) #Doesn't work)

    #Basic homepage redirection to google.kz
    def go_to_home(self):
        self.tabs.currentWidget().setUrl(QUrl("https://www.google.kz"))

    #Directs to adress inside urlbar
    def go_to_website(self):
        go_to_url = QUrl(self.urlbar.text())
        if go_to_url.scheme() == "":
            go_to_url.setScheme("http")

        self.tabs.currentWidget().setUrl(QUrl(go_to_url))
        
    #Checks if HTTP connection is secure or not(so lame xD i know)
    def update_urlbar(self, n, browser=None):
        
        if browser != self.tabs.currentWidget():
            return

        if n.scheme() == 'https': #Checks url
            secure_pixmap = QPixmap(os.path.join('icons','secure_logo.png'))
            secure_pixmap = secure_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.FastTransformation)
            self.httpsicon.setPixmap(secure_pixmap)
        else:
            secure_pixmap = QPixmap(os.path.join('icons','not_secure_logo.png'))
            secure_pixmap = secure_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.FastTransformation)
            self.httpsicon.setPixmap(secure_pixmap)       

        self.urlbar.setText(n.toString())
        self.urlbar.setCursorPosition(0)
        if self.urlbar.text() != '':
            AboutDialog.url_from_urlbar = self.urlbar.text()

            
app = QApplication(sys.argv)
app.setApplicationName("Solar")
window = MainWindow()
window.show()

app.exec_()

#More functionality to be added. Maybe.