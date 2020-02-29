# 使用QtCreator建立的ui文件路径
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit, QMessageBox

qtCreatorFile = "CanMesGenerate.ui"
# 使用uic加载
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QMainWindow, Ui_MainWindow):
    '''
    使用PyQt5做GUI界面，调用百度文字识别API识别图片文字
    '''
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        super().__init__()
        self.initUI()       # 调用自定义的UI初始化函数initUI()
        self.status = False # 状态变量，如果是打开图片来转换的，设置status为True，以区分截图时调用的图片转换函数
        self.start_bit= 0
        self.bit_length= 0
        self.resolution = 0
        self.offset = 1
        self.signalphys = 0
        self.lsb_checked = 0
        self.msb_checked = 0
        self.CAN = [0] * 64

    def initUI(self):
        '''
        Initialize the window's UI
        '''
        self.setupUi(self)
        self.setWindowTitle("CAN报文生成工具")
        self.initButton()       # 初始化按钮
        self.show()             # 显示

    #检查输入数值是否符合要求
    def checked_value(self,start_bit, bit_length, resolution, offset, signalphys, lsb_checked, msb_checked):
        if lsb_checked == 0 and msb_checked == 0:
            QMessageBox.critical(self, "标题", "请至少选择一种编码格式", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if start_bit =='' or not start_bit.isdigit() :
            QMessageBox.critical(self, "标题", "请输入起始位，且为正整数", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if bit_length =='' or not bit_length.isdigit():
            QMessageBox.critical(self, "标题", "请输入信号长度，且为正整数", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if resolution =='':
            QMessageBox.critical(self, "标题", "请输入精度", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if offset =='':
            QMessageBox.critical(self, "标题", "请输入偏移量", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if signalphys =='':
            QMessageBox.critical(self, "标题", "请输入信号值，物理值-十进制数", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    # 十进制转换成倒序二进制list
    def octToBin(self, octNum, bit):
        while (octNum != 0):
            # 求模运算，2的模值要么0，要么1
            bit.append(octNum % 2)
            # 除运算，15/2=7,int取整数
            octNum = int(octNum / 2)
        # 当输入的信号值二进制长度是小于总的信号长度，就在后面补0，倒序
        #如 如果 octnum 为 2 信号长度 bit_length为5 则 bit为[0,1,0,0,0]
        while len(bit) < self.bit_length:
            bit.append(0)
        #print(bit)

    #对64位CAN信号进行处理 并输出显示到界面上
    def message_fill(self):
        self.first_byte = hex(int(''.join(map(str, self.CAN[7::-1])), 2)).upper().lstrip("0").lstrip("X").zfill(2) + " "
        self.second_byte = hex(int(''.join(map(str, self.CAN[15:7:-1])), 2)).upper().lstrip("0").lstrip("X").zfill(
            2) + " "
        self.third_byte = hex(int(''.join(map(str, self.CAN[23:15:-1])), 2)).upper().lstrip("0").lstrip("X").zfill(
            2) + " "
        self.fourth_byte = hex(int(''.join(map(str, self.CAN[31:23:-1])), 2)).upper().lstrip("0").lstrip("X").zfill(
            2) + " "
        self.fifth_byte = hex(int(''.join(map(str, self.CAN[39:31:-1])), 2)).upper().lstrip("0").lstrip("X").zfill(
            2) + " "
        self.sixth_byte = hex(int(''.join(map(str, self.CAN[47:39:-1])), 2)).upper().lstrip("0").lstrip("X").zfill(
            2) + " "
        self.seventh_byte = hex(int(''.join(map(str, self.CAN[55:47:-1])), 2)).upper().lstrip("0").lstrip("X").zfill(
            2) + " "
        self.eighth_byte = hex(int(''.join(map(str, self.CAN[63:55:-1])), 2)).upper().lstrip("0").lstrip("X").zfill(2)
        # 输出报文
        self.message_le.setText(
            self.first_byte + self.second_byte + self.third_byte + self.fourth_byte + self.fifth_byte +
            self.sixth_byte + self.seventh_byte + self.eighth_byte)

    def CANMessage_msb(self):
        print("格式为Motorola MSB")
        output_message=True
        # 长度未超过1Byte的情况且未跨字节的信号
        if (self.bit_length <= 8) and (int(self.start_bit/8) == int((self.start_bit - self.bit_length + 1)/8)):
            bit = []  # 已经是二进制倒序排列了
            # setValue的二进制值按字节位从低到高填
            self.octToBin(self.signalphys, bit)
            # 填满字节长度值20 = [0, 0, 1]
            for i in range(self.bit_length):
                self.CAN[self.start_bit - i] = bit[len(bit) - 1 - i]
        # 跨字节的信号
        elif (self.bit_length - (int(self.start_bit % 8) + 1) <= 8): #共2个字节 跨了1个字节
            # 高字节位数和低字节位数
            low_len = self.start_bit % 8 + 1
            high_len = self.bit_length - low_len
            bit = []
            # setValue的二进制值按字节位从低到高填
            self.octToBin(self.signalphys, bit)
            # 先填进信号的高位
            for j1 in range(low_len):
                self.CAN[self.start_bit - j1] = bit[len(bit) - 1 - j1]
            # 再填进低字节，低字节一般比起始位第一个8位
            for j2 in range(high_len):
                self.CAN[(int(self.start_bit / 8) + 1) * 8 + (8 - high_len) + j2] = bit[j2]
        elif (self.bit_length - (int(self.start_bit % 8) + 1) <= 16) and \
                self.bit_length - (int(self.start_bit % 8) + 1) > 8:  #共3个字节 跨了2个字节
            # 高字节位数和低字节位数
            low_len = self.start_bit % 8 + 1
            high_len = self.bit_length - low_len - 8
            bit = []
            # setValue的二进制值按字节位从低到高填
            self.octToBin(self.signalphys, bit)
            # 先填进信号的高位
            for j1 in range(low_len):
                self.CAN[self.start_bit - j1] = bit[len(bit) - 1 - j1]
            # 再填进低字节，低字节一般比起始位第一个8位
            for j2 in range(high_len):
                self.CAN[self.start_bit+(8-low_len)+8+(8-high_len)+1+j2] = bit[j2]
            for j3 in range(8): #填充中间的那行
                self.CAN[(int(self.start_bit/8) +1)*8 +j3 ] = bit[high_len + j3]
        elif (self.bit_length - (int(self.start_bit % 8) + 1) <= 24) and \
                self.bit_length - (int(self.start_bit % 8) + 1) > 16:  #共4个字节 跨了3个字节
            low_len = self.start_bit % 8 + 1
            high_len = self.bit_length - low_len - 8*2
            bit = []
            self.octToBin(self.signalphys, bit)
            for j1 in range(low_len):
                self.CAN[self.start_bit - j1] = bit[len(bit) - 1 - j1]
                print(self.CAN)
            for j2 in range(high_len):
                self.CAN[self.start_bit+(8-low_len)+8*2+(8-high_len)+1+j2] = bit[j2]
                print(self.CAN)
            for j3 in range(8): #填充中间的那行
                self.CAN[(int(self.start_bit / 8))*8 + 8*2 +j3 ] = bit[high_len + j3]
                print(self.CAN)
            for j4 in range(8): #填充中间的那行
                self.CAN[(int(self.start_bit / 8))*8 + 8 +j4 ] = bit[high_len + 8 + j4]
        else:
            output_message = False
        if output_message:
            self.message_fill()
        else: #暂不支持超过4个字节的情况
            QMessageBox.critical(self, "标题", "暂不支持！！！", QMessageBox.Yes | QMessageBox.No,
                                 QMessageBox.Yes)
        #print(self.CAN)

    def CANMessage_lsb(self):
        print("格式为Motorola LSB")
        output_message = True
        #报文的起始为LSB（最低有效字节）的lsb（最低有效位） 从起始点开始位方向从右向左，字节方向自下至上。
        #判断输入的信号长度正确，不会超过范围 如起始位是 7 信号长度为2
        if (self.bit_length > ((8 - int(self.start_bit % 8)) + int(self.start_bit/8) * 8 )):
            output_message = False
            QMessageBox.critical(self, "标题", "输入的信号长度超过范围，请重新输入", QMessageBox.Yes | QMessageBox.No,
                                 QMessageBox.Yes)
        # 长度未超过1Byte的情况且未跨字节的信号
        elif ((self.start_bit % 8 + self.bit_length) <= 8):
            bit = []  # 已经是二进制倒序排列了
            # setValue的二进制值按字节位从低到高填
            self.octToBin(self.signalphys, bit)
            # 填满字节长度值
            for i in range(self.bit_length):
                self.CAN[self.start_bit + i] = bit[i]
        # 跨字节的信号
        elif (int(self.start_bit % 8) + self.bit_length) -1 <= 15 \
                and (int(self.start_bit % 8) + self.bit_length) -1 >= 8:
            # 共两个字节 跨一个字节的情况
            high_len = 8 - self.start_bit % 8
            low_len = self.bit_length - high_len
            bit = []
            # setValue的二进制值按字节位从低到高填
            self.octToBin(self.signalphys, bit)
            # 先填进信号的高位
            for j1 in range(high_len):
                self.CAN[self.start_bit + j1] = bit[j1]
            # 再填进低字节，低字节一般比起始位第一个8位
            for j2 in range(low_len):
                self.CAN[(int(self.start_bit / 8) - 1) * 8 + j2] = bit[high_len + j2]

        elif (int(self.start_bit % 8) + self.bit_length) -1 <= 23 \
                and (int(self.start_bit % 8) + self.bit_length) -1 >= 16:
            # 共3个字节 跨2个字节的情况
            high_len = 8 - self.start_bit % 8
            low_len = self.bit_length - high_len - 8
            bit = []
            # setValue的二进制值按字节位从低到高填
            self.octToBin(self.signalphys, bit)
            # 先填进信号的高位
            for j1 in range(high_len):
                self.CAN[self.start_bit + j1] = bit[j1]
            # 再填进低字节
            for j2 in range(low_len):
                self.CAN[ (low_len - 1) + (int(self.start_bit / 8) - 2) * 8 - j2] = bit[len(bit) - 1 - j2]
            for j3 in range(8):
                self.CAN[(int(self.start_bit / 8) - 1) * 8 + j3] = bit[high_len + j3]

        elif (int(self.start_bit % 8) + self.bit_length) -1 <= 31 \
                and (int(self.start_bit % 8) + self.bit_length) -1 >= 24:
            # 共4个字节 跨3个字节的情况
            high_len = 8 - self.start_bit % 8
            low_len = self.bit_length - high_len - 8 * 2
            bit = []
            # setValue的二进制值按字节位从低到高填
            self.octToBin(self.signalphys, bit)
            # 先填进信号的高位
            for j1 in range(high_len):
                self.CAN[self.start_bit + j1] = bit[j1]
            # 再填进低字节
            for j2 in range(low_len):
                self.CAN[ (low_len - 1) + (int(self.start_bit / 8) - 3) * 8 - j2] = bit[len(bit) - 1 - j2]
            for j3 in range(8):
                self.CAN[(int(self.start_bit / 8) - 1) * 8 + j3] = bit[high_len + j3]
            for j4 in range(8):
                self.CAN[(int(self.start_bit / 8) - 2) * 8 + j4] = bit[high_len + 8 + j4]
        else:
            output_message = False
        if output_message:
            self.message_fill()
        else: #暂不支持超过4个字节的情况
            QMessageBox.critical(self, "标题", "暂不支持！！！", QMessageBox.Yes | QMessageBox.No,
                                 QMessageBox.Yes)
        print(self.CAN)

    def message_generate(self):
        self.signalphys = int((float(self.signalphys) - float(self.offset)) / float(self.resolution))
        self.start_bit = int(self.start_bit)
        self.bit_length = int(self.bit_length)
        # 判断输入的信号值 是否超过了 信号位数所能承受的范围
        max_value = 2**(self.bit_length)
        if (int(max_value) < int(self.signalphys)):
            QMessageBox.critical(self, "标题", "输入信号值超出范围，请检查信号长度和信号值是否正确！！！", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        else:
            self.CAN = [0] * 64
            # 获取到全部数据，现在对数据进行处理，填充64方格
            if (self.lsb_checked == 1):
                self.CANMessage_lsb()
            if (self.msb_checked == 1):
                self.CANMessage_msb()

    def convertCANMessage(self):
        self.start_bit=self.startbit_le.text()
        self.bit_length=self.bitlength_le.text()
        self.resolution = self.resolution_le.text()
        self.offset = self.offset_le.text()
        self.signalphys = self.signalphys_le.text()
        self.message_le.setText('')
        if self.lsb_rb.isChecked() == True:
            self.lsb_checked = 1
            print("LSB is selected")
        elif self.msb_rb.isChecked() == True:
            self.msb_checked = 1
            print("MSB is selected")
        self.checked_value(self.start_bit, self.bit_length, self.resolution,
                           self.offset, self.signalphys, self.lsb_checked, self.msb_checked)
        self.message_generate()

    def initButton(self):
        '''
        初始化按钮
        '''
        self.generate_pb.clicked.connect(self.convertCANMessage)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    sys.exit(app.exec_())