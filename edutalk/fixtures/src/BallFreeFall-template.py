{%- if 'Gravity' not in odf_list-%}
gravity = 5
{{ "\n" }}
{%- endif -%}
{%- if 'Radius' not in odf_list-%}
radius = 5
{{ "\n" }}
{%- endif -%}

{%-for df_name in odf_list -%}
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
{{df_name.lower()}} = {{ df_default_values[df_name] }}
def {{df_name}}(data):
    global {{df_name.lower()}}
    if data != None:
        {{df_name.lower()}} = data[0]
        {{ "\n" }}
    {%- endif -%}
{%- endfor -%}


# 設定
def setup():
    profile = {
        'dm_name' : '{{ dm_name }}',
        'idf_list': [],
        'odf_list': {{ odf_list | todf_list | safe }},
    }
    dai(profile, mac_addr, ida)

setup()

# {{ odf_list | tojson | safe }} 讀取感測器後會自動更新
# 請勿修改上方程式碼

# 物理參數區
height = 15.0     # 初始高度(m)
restitution = 1.0 # 恢復係數

# 模擬實驗參數區
freq = 120        # 更新頻率(Hz)
dt = 1.0 / freq   # 更新間隔(second)

# 與流程控制有關參數
g = 5.0          # 定義初始重力加速度

# 初始化場景
def scene_init():
    # 初始場景、球、地板、文字方塊
    global scene, ball, floor, height, label_info
    scene = display(width=800, height=700, center = vec(0, height/2, 0), background=vec(0.5, 0.5, 0))
    floor = box(length=30, height=0.01, width=10, texture=textures.wood )
    ball = sphere(
        pos = vec(0, height, 0),
        radius = 0.5,
        color = color.green,
        velocity = vector(0,0,0),
        visible = True
    )
    label_info = label( pos=vec(10,20,0), text='', color = color.white)

scene_init()

while True:
    # 在每秒重畫 freq 次
    rate(freq)

    # 更新顯示數據
    {% set label_text = {'cont':''} %}
    {%- set value_list = [] -%}
    {%- for default_df in ['Gravity', 'Radius']-%}
        {%- if default_df not in odf_list-%}
            {%- set tmp = default_df.lower() + ': {:.2f}\\n'-%}
            {%- if label_text.update({'cont':label_text.cont+ tmp }) -%}
            {%- endif -%}
            {%- if value_list.append(default_df.lower()) -%}
            {%- endif -%}
        {%- endif -%}
    {%- endfor -%}

    {%- for df_name in odf_list -%}
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
            {%- if "_" in df_name -%}
                {%- set df_name = df_name[df_name.find("_")+1:] -%}
            {%- else -%}
                {%- set df_name = df_name.lower() -%}
            {%- endif -%}
            {%- if value_list.append(df_name) -%}
            {%- endif -%}
            {%- set tmp = df_name + ': {:.2f}\\n' -%}
        {%- endif -%}
        {%- if label_text.update({'cont':label_text.cont+tmp}) -%}
        {%- endif -%}
    {%- endfor -%}

    {%- if label_text.update({'cont':label_text.cont+ 'current_speed: {:.2f}\\nheight: {:.2f}\\n'}) -%}
    {%- endif -%}

    label_info.text='{{label_text.cont}}'.format({{value_list|join(',')}},abs(ball.velocity.y),ball.pos.y)

    # 更新球半徑、重力加速度
    ball.radius = radius
    g = gravity

    # 計算下一個時間點的資料並將改變畫出
    # 球的位置變化量是 速度 乘上 時間
    ball.pos = ball.pos + ball.velocity * dt
    # 判斷球的新位置是否高於地面
    if ball.pos.y > ball.radius:
        # 如是，依重力加速度修改速度
        ball.velocity.y = ball.velocity.y -g*dt
    else:
        # 如否，依恢復係數計算出反彈後速度，並設定球的位置在地面上
        ball.velocity.y = -ball.velocity.y * restitution
        ball.pos.y = ball.radius
