gravity = 0
def Gravity(data):
    global gravity
    if data != None:
        gravity = data[0]

speed = 0
def Speed(data):
    global speed
    if data != None:
        speed = data[0]


# 設定
def setup():
    profile = {
        'dm_name' : 'Universe',
        'idf_list': [],
        'odf_list' : ['Gravity', 'Speed'],
    }
    dai(profile, mac_addr, ida)

setup()

# gravity, speed 讀取感測器後會自動更新
# 請勿修改上方程式碼

ball_radius = 0.8 # 球半徑(m)
height = 12.0     # 初始高度(m)
speed = 25.0        # 初始速度
gravity = 5.0          # 萬有引力常數
direction = vec(1,0,0) # 初始方向

# 模擬實驗參數區
freq = 120        # 更新頻率(Hz)
dt = 1.0 / freq   # 更新間隔(second)

# 事件旗標區
reset_flag = False

# 重置
def reset_ball():
    global ball, reset_flag
    # 復位
    ball.pos = vec(0, height, 0)
    # 速度歸零
    ball.velocity = speed*norm(direction)
    # 洗去旗標
    reset_flag = False

# 初始化場景
def scene_init():
    global scene, ball, floor, height, ball_radius, label_gravity
    scene = display(width=800, height=700, center = vec(0, 0, 0), background=vec(0.5, 0.5, 0))
    label_gravity = label( pos=vec(0.8*height,0.8*height,0), text='Gravity: {:.3f}\nSpeed: {:.3f}'.format(gravity,speed))
    floor = sphere(
        pos = vec(0, 0, 0),
        radius = 2*ball_radius,
        velocity = vec(0, 0, 0),
        color = color.red
    )
    ball = sphere(
        pos = vec(0, height, 0),
        radius = ball_radius,
        velocity = speed*norm(direction),
        color = color.green
    )
    scene.autoscale = False

scene_init()

#用來判斷萬有引力常數、速度是否改變
prev_state = (gravity, speed)
while True:
    rate(freq)
    label_gravity.text = 'Gravity: {:.3f}\nSpeed: {:.3f}'.format(gravity,speed)
    # 模擬天體運動
    if (ball.pos-floor.pos).mag > floor.radius+ball_radius and ball.pos.mag < height*2:
        ball.pos = ball.pos + ball.velocity * dt
    ball.velocity = ball.velocity - gravity * norm(ball.pos - floor.pos) / (ball.pos - floor.pos).mag2
    #如果萬有引力常數、速度已改變，重置畫面
    if prev_state != (gravity, speed):
        reset_flag = True
    if reset_flag == True:
        reset_ball()
    prev_state = (gravity, speed)
