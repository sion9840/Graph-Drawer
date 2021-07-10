import tkinter as tk #tk GUI 라이브러리
from pandas import DataFrame #pandas 라이브러리
import matplotlib.pyplot as plt #matplotlib 라이브러리1
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #matplotlib 라이브러리2
import numpy as np #numpy 라이브러리
from matplotlib.backends.backend_tkagg import ( #matplotlib 라이브러리3
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.animation as animation #그래프 애니메이션 라이브러리

def m_selected(): #미분 그래프를 그릴것 인지 여부를 바꾸는 함수
    global M
    if M == 0:
        M = 1
    else:
        M = 0

def g_selected(): #그리드를 그릴것 인지 여부를 바꾸는 함수
    global G
    if G == 0:
        G = 1
    else:
        G = 0

def q_selected(): #축을 그릴것 인지 여부를 바꾸는 함수
    global Q
    if Q == 0:
        Q = 1
    else:
        Q = 0

def draw_graph(title): #그래프 그리는 함수
    global data, line, figure, ax, df1, df2, toolbar
    # 아래는 그래프 그리는 과정
    df1 = DataFrame(data, columns=['x', 'Main Graph'])
    if M == 1: df2 = DataFrame(data, columns=['x', 'Differential Graph'])

    figure = plt.Figure(figsize=(5, 4), dpi=100)
    ax = figure.add_subplot(111)
    line = FigureCanvasTkAgg(figure, root)
    line.get_tk_widget().place(x=0, y=0, width=700, height=570)
    df1 = df1[['x', 'Main Graph']].groupby('x').sum()
    if M == 1: df2 = df2[['x', 'Differential Graph']].groupby('x').sum()
    df1.plot(kind='line', legend=True, ax=ax, color='r', marker='o', fontsize=10)
    if M == 1: df2.plot(kind='line', legend=True, ax=ax, color='b', marker='', fontsize=10)
    ax.set_title(title)
    # 요 아래는 x축,y축,그리드 그리는 과정
    if G == 1: ax.grid(True)
    if Q == 1:
        ax.axvline(x=0, color='black')
        ax.axhline(y=0, color='black')

    # 요 아래는 그래프 toolbar 만드는 과정
    toolbar = NavigationToolbar2Tk(line, root)
    toolbar.update()
    toolbar.place(x=0, y=560, width=701)

def select(self): #SCALE의 실행 함수
    global SIZE
    value="x 범위:"+str(scale.get())
    label.config(text=value)
    SIZE = scale.get()

def press(): #확인 버튼 누르면 실행 되는 함수
    if str(entry.get()) != '' and scale.get() != 0: #다항식을 입력하고 x의 범위까지 설정해야 그래프를 그리도록 하는 조건문
        calc()

def calc():
    global data,line,figure,ax,df1,df2,toolbar

    ######### 아래 부터 입력 받은 다항식 손보는 부분 ##############

    EXPRESS = {} #입력받은 다항식의 지수에 따른 계수 저장하는 딕셔너리 변수

    GET = str(entry.get()) #다항식 입력 받음
    DATA = GET.replace(' ','').replace('+',',+').replace('-',',-').replace('=,',',').replace('=',',').split(',') #입력 받은 다항식을 잘 활용할 수 있게 데이터를 손보는 과정 (예: y = 2x^2 + 5 -> [y,2x^2,5])
    del DATA[0] #DATA 리스트에서 y는 쓸모 없으니깐 제거

    for i in DATA:
        if '^' in i: #2차시 이상인 경우
            if i.replace(i[i.find('x'):],'') == '+' or i.replace(i[i.find('x'):],'') == '': # 계수가 1인 경우
                EXPRESS[int(i[i.find('^') + 1:])] = 1
            elif i.replace(i[i.find('x'):],'') == '-': # 계수가 -1인 경우
                EXPRESS[int(i[i.find('^') + 1:])] = -1
            else: # 계수가 1과-1이 아닌 경우
                EXPRESS[int(i[i.find('^')+1:])] = int(i.replace(i[i.find('x'):],''))
        elif 'x' in i: #1차시인 경우
            if i.replace('x','') == '+' or i.replace('x','') == '': # 계수가 1인 경우
                EXPRESS[1] = 1
            elif i.replace('x','') == '-': # 계수가 -1인 경우
                EXPRESS[1] = -1
            else: #1차시인 경우
                EXPRESS[1] = int(i.replace('x',''))
        else: #상수항인 경우
            EXPRESS[0] = int(i)

    if (0 in EXPRESS.keys()) == False: #입력받은 다항식에 상수항이 있는지 여부를 확인하는 조건문
        EXPRESS[0] = 0 #상수항이 없으면 상수항 0 추가
    elif len(EXPRESS) == 1: #입력받은 다항식에 x가 없는지 여부를 확인하는 조건문
        EXPRESS[1] = 0 #x가 없으면 계수가 0인 x추가

    EXPRESS = sorted(EXPRESS.items(),reverse = True) #다항식의 x들이 순서없이 뒤섞여 있을 수 있으니깐 지수가 큰 순으로 재배열 하는 과정

    length = len(EXPRESS)

    for i in range(length-1):
        if EXPRESS[i][0] - EXPRESS[i+1][0] != 1: #(현 x의 지수 - 다음 x의 지수) 가 1인 아닌 경우를 확인하는 조건문
            EXPRESS = EXPRESS + [(j,0) for j in range(EXPRESS[i][0]-1,EXPRESS[i+1][0],-1)] #그렇다면 (현 x의 지수 - 다음 x의 지수)만큼의 계산에 필요한 x가 부족한거니깐 부족한거 보충시키는 과정

    EXPRESS = sorted(EXPRESS,reverse = True) #다시한번 지수의 크기가 큰 순으로 재배열하는 과정
    EXPRESS = [i[1] for i in EXPRESS] #계산에 필요한 계수들을 모으는 과정

    ######### 아래 부터 메인 그래프선 추가 부분 ##############

    for i in range(-1 * SIZE,SIZE + 1): #사용자가 조정한 x의 범위 만큼 그래프선 추가
        data['x'].append(i)
        data['Main Graph'].append(np.polyval(np.poly1d(EXPRESS),i))

    ######### 아래 부터 미분 그래프선 추가 부분 ##############
    if M == 1:
        print('EXPRESS:', EXPRESS)
        MEXPRESS = np.polyder(np.poly1d(EXPRESS), m = 1)
        print('MEXPRESS:',MEXPRESS)
        for i in range(-1 * SIZE,SIZE + 1): #사용자가 조정한 x의 범위 만큼 미분 그래프선 추가
            # data2['x'].append(i)
            data['Differential Graph'].append(np.polyval(MEXPRESS, i))

    ##-######-########-######-#######-#####-####-#####

    print(data)

    line.get_tk_widget().pack_forget()

    draw_graph(GET)

    data = {'x': [],
             'Main Graph': [],
             'Differential Graph': []
             }

SIZE = 0
M = 0
G = 0
Q = 0

data = {'x': [],
         'Main Graph': [],
         'Differential Graph': []
             }

root = tk.Tk()
root.title("Graph Drawer")
root.geometry("940x599+100+100")
root.resizable(False, False)

draw_graph('Graph Drawer')

#요 아래는 다항식 입력 텍스트 박스 생성하는 것
entry=tk.Entry(root)
entry.place(x = 700,y = 0, width = 240)

#요 아래는 x의 범위를 조정하는 SCALE 생성하는 것
var=tk.IntVar()

scale=tk.Scale(root, variable=var, command=select, orient="horizontal", showvalue=False, tickinterval=5, to=10, length=300)
scale.place(x = 760,y = 20, width = 180)

label=tk.Label(root, text="x 범위:0")
label.place(x = 700,y = 20)

#요 아래는 확인 버튼 생성하는 것
button = tk.Button(root, overrelief="solid", width=15, command = press, repeatdelay=1000, repeatinterval=100, bg = 'light gray', text = '확인')
button.place(x = 700,y = 500, width = 240, height = 100)

#요 아래는 선택 버튼 생성하는 것
checkbutton1=tk.Checkbutton(root, text="미분 그래프", command = m_selected)
checkbutton1.place(x = 700,y = 55)

checkbutton2=tk.Checkbutton(root, text="그리드", command = g_selected)
checkbutton2.place(x = 700,y = 75)

checkbutton3=tk.Checkbutton(root, text="축", command = q_selected)
checkbutton3.place(x = 700,y = 95)

root.mainloop()