# 物理參數區
ball_radius = 1
height = 30.0     # 初始高度
gravity = 9.8     # 重力加速度
speed = 25.0       # 初始速度
angle = 0.0      # 初始角度
number = 10

# 模擬實驗參數區
freq = 120        # 更新頻率(Hz)
dt = 1.0 / freq   # 更新間隔(second)
reset_flag = False

def rad(x):
    return Math.acos(-1)*x/180.0

def shoot(ball):
    global balls, speed, angle
    ball.pos = vec(0,height,0)
    for b in balls:
        if b.visible == False: continue
        if (b.pos - ball.pos).mag <= ball_radius*2:
            return
    ball.visible = True
    ball.velocity = speed * norm(vec(Math.cos(rad(angle)), Math.sin(rad(angle)), 0))

def scene_init():
    #initial scene
    global scene, balls, height, ball_radius, label_info
    scene = display(autoscale = True, width=800, height=600, center = vec(height, height, 0), background=vec(0.7, 0.7, 0.7))
    label_info = label( pos=vec(10,20,0), text='Speed: {:.2f}\nAngle: {:.2f}'.format(speed,angle))
    balls = []
    while len(balls) < number:
        balls.append(sphere(
            pos = vec(0,height,0),
            radius = ball_radius,
            velocity = speed * norm(vec(Math.cos(rad(angle)), Math.sin(rad(angle)), 0)),
            color = color.red,
            visible = False
        ))
    box(length=2*height, height=2*height, width=2*ball_radius, pos = vec(height,height,ball_radius), opacity=0.1, color=vec(0.2,0.2,1))
    scene.autoscale = False

def Speed(data):
    global speed
    if data != None and data[0] != speed:
        speed = data[0]

def Angle(data):
    global angle
    if data != None and data[0] != angle:
        angle = data[0]

def setup():
    scene_init()
    profile = {
        'dm_name': 'ProjectileMotion',
        'idf_list': [],
        'odf_list' : [Speed, Angle],
    }
    dai(profile, mac_addr, ida)

setup()

cnt = 0
while True:
    rate(freq)
    cnt += 1
    if cnt >= freq/2:
        cnt = 0
        for ball in balls:
            if ball.visible == False:
                shoot(ball)
                break
    label_info.text = 'Speed: {:.2f}\nAngle: {:.2f}\n cnt: {}'.format(speed,angle,cnt)
    # 球與球之間完全彈性碰撞
    for i in range(number):
        if balls[i].visible == False: continue
        for j in range(i+1, number):
            if balls[j].visible == False: continue
            if (balls[i].pos-balls[j].pos).mag <= 2*ball_radius:
                proj_i = balls[i].velocity.proj(balls[i].pos - balls[j].pos)
                proj_j = balls[j].velocity.proj(balls[i].pos - balls[j].pos)
                balls[i].velocity = balls[i].velocity + proj_j - proj_i
                balls[j].velocity = balls[j].velocity + proj_i - proj_j

    for ball in balls:
        if ball.visible == False: continue
        # 球自由落體與地板之間碰撞反彈
        ball.pos = ball.pos + ball.velocity * dt
        ball.velocity.y = ball.velocity.y - gravity*dt
        if ball.pos.y < 0.0  or ball.pos.x > 2*height or ball.pos.y > 2*height:
            ball.visible = False

