speed = 25
def Speed(data):
    global speed
    if data != None:
        speed = data[0]

friction = 0.5
def Friction(data):
    global friction
    if data != None:
        friction = data[0]
{{ "\n" }}

{%-for df_name, _ in odf_list -%}
    {%- if df_name != 'Speed' and df_name != 'Friction'-%}
        {%- if "_O" in df_name -%}
            {%- set sm_df = df_name -%}
            {%- set df_name = df_name[:-2].lower() -%}
            {%- if df_name == "humidity" or df_name == "uv" or df_name == "alcohol" -%}
{{df_name}} = 0
def {{sm_df}}(data):
    global {{df_name}}
    if data != None:
        {{df_name}} = data[0]
        {{ "\n" }}
            {%- else -%}
{{df_name}} = vec(0,0,0)
def {{sm_df}}(data):
    global {{df_name}}
    if data != None:
        {{df_name}}.x = data[0]
        {{df_name}}.y = data[1]
        {{df_name}}.z = data[2]
        {{ "\n" }}
            {%- endif -%}
        {%- else -%}
{{df_name.lower()}} = {{ df_means[df_name] }}
def {{df_name}}(data):
    global {{df_name.lower()}}
    if data != None:
        {{df_name.lower()}} = data[0]
        {{ "\n" }}
        {%- endif -%}
    {%- endif -%}
{%- endfor -%}


# 設定
def setup():
    profile = {
        'dm_name': '{{ dm_name }}',
        'idf_list': [],
        'odf_list': {{ odf_list | todf_list | safe }},
    }
    dai(profile, mac_addr, ida)

setup()

{{ "\n" }}
# {{ odf_list | tojson | safe }} 讀取感測器後會自動更新
# 請勿修改上方程式碼

freq = 120        # 更新頻率(Hz)
g = 9.8
m = 1.0
s = 0.1
ball_inertia = 2 * m * 0.35 ** 2 / 3
dt = 1 / freq

# 初始化場景
def scene_init():
    global scene, init_value_box, ball_spd_box, ball, is_running
    # 設定場景寬、高、中心位置及顏色
    scene = display(width = 700, height = 700, background = vec(1, 1, 1),center = vec(0, 0.25, 0), range = 1.5, forward = vec(0, -0.8, -1))
    # 設定標語位置、內容、高度、字體及顏色
    init_value_box = label(pos=vec(-0.35, 1.40, 0), text = '', height = 25, border = 15, font = 'monospace', color = color.black)
    ball_spd_box = label(pos=vec(0.55, 1.40, 0), text = 'Speed:', height = 25, border = 15, font = 'monospace', color = color.black)
    # 設定球的半徑、位置及貼在球上的圖
    ball = sphere(radius = 0.35, pos = vec(0, 0.35, 0.1), texture={'file':textures.earth, 'bumpmap':bumpmaps.stucco})

# 每秒鐘更新顯示數據
def update_init():
    global init_value_box
    {% set label_text = {'cont':'Initial values:\\nFriction: {:.2f}\\nSpeed: {:.2f}'} %}
    {%- set value_list = [] -%}
    {%- for df_name, _ in odf_list -%}
        {%- if df_name != 'Friction' and df_name != 'Speed'-%}
            {%- if "_O" in df_name -%}
                {%- set df_name = df_name[:-2].lower() -%}
                {%- if df_name == "humidity" or df_name == "uv" or df_name == "alcohol" -%}
                    {%- if value_list.append(df_name) -%}
                    {%- endif -%}
                    {%- set tmp = df_name+': {:.2f}\\n' -%}
                {%- else -%}
                    {%- if value_list.append(df_name+'.x') -%}
                    {%- endif -%}
                    {%- if value_list.append(df_name+'.y') -%}
                    {%- endif -%}
                    {%- if value_list.append(df_name+'.z') -%}
                    {%- endif -%}
                    {%- set tmp = df_name+': {:.2f} {:.2f} {:.2f}\\n' -%}
                {%- endif -%}
            {%- else -%}
            {%- set df_name = df_name.lower() -%}
                {%- if value_list.append(df_name) -%}
                {%- endif -%}
                {%- set tmp = df_name+': {:.2f}\\n' -%}
            {%- endif -%}
            {%- if label_text.update({'cont':label_text.cont+tmp}) -%}
            {%- endif -%}
        {%- endif -%}
    {%- endfor -%}
    init_value_box.text='{{label_text.cont}}'.format(friction,speed,{{value_list|join(',')}})

def update_info():
    global ball_spd_box, current_speed
    ball_spd_box.text = 'Speed: {:.2f}'.format(current_speed, 1)

# 重設各項參數
def reset():
    global prev_state, current_speed, torque, a
    update_init()
    # 將現有(速度、摩擦力係數)數值存至prev_state中
    prev_state = ({{odf_list|e|replace("&#39;", "")|replace("_O","")|lower()}}) # FIXME
    current_speed = speed
    # 計算摩擦力
    torque = friction * m * g * s
    if speed > 0:
        a = -torque / ball_inertia
    elif speed < 0:
        a = torque / ball_inertia
    else:
        a = 0

scene_init()
reset()

cnt = 0
while True:
    # 等待(1.0/freq)秒
    rate(freq)
    # 檢查現有(速度、摩擦力係數)數值不等於prev_state中的數值是否相同
    # 即檢查是否有新的速度或新的摩擦力係數傳入
    if prev_state != ({{odf_list|e|replace("&#39;", "")|replace("_O","")|lower()}}):  #FIXME
        reset()
    # 用cnt記數使每(1.0/freq)*(freq//5) = 0.2秒更新資訊
    if cnt % (freq // 5) == 0:
        update_info()
    # 如果球現在速度不等於0，計算新的速度。等於0的話表示球已停下，不用計算
    if current_speed != 0:
        current_speed += a * dt
        delta_angle = current_speed * dt + 0.5 * a * dt ** 2
        ball.rotate(angle = delta_angle, axis = vec(0,1,0))
        # 如果算出來的速度是負的，表示球已停下，將球的速度設為0
        if current_speed * speed <= 0:
            current_speed = 0

    cnt = cnt + 1
