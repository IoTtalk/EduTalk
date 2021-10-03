{%-for df_name, _ in odf_list -%}
    {%- if "_O" in df_name -%}
        {%- set sm_df = df_name -%}
        {%- set df_name = df_name[:-2].lower() -%}
        {%- if df_name == "humidity" or df_name == "uv" or df_name == "alcohol" -%}
{{df_name}} = 0
{{df_name}}_time = '{{df_name}}_time'
def {{sm_df}}(data):
    global {{df_name}}
    global {{df_name}}_time
    if data != None:
        {{df_name}} = data[0]
        {{df_name}}_time = data[1]
        {{ "\n" }}
        {%- else -%}
{{df_name}} = vec(0,0,0)
{{df_name}}_time = '{{df_name}}_time'
def {{sm_df}}(data):
    global {{df_name}}
    global {{df_name}}_time
    if data != None:
        {{df_name}}.x = data[0]
        {{df_name}}.y = data[1]
        {{df_name}}.z = data[2]
        {{df_name}}_time = data[3]
        {{ "\n" }}
        {%- endif -%}
    {%- else -%}
        {%- if "_" in df_name -%}
            {%- set _var = df_name[df_name.find("_")+1:] -%}
        {%- else -%}
            {%- set _var = df_name.lower() -%}
        {%- endif -%}
{{_var}} = {{ df_default_values[df_name] }}
def {{df_name}}(data):
    global {{_var}}
    if data != None:
        {{_var}} = data[0]
        {{ "\n" }}
    {%- endif -%}
{%- endfor -%}


# 設定
def setup():
    profile = {
        'dm_name' : '{{ dm_name }}',
        'idf_list': [],
        'odf_list' : {{ odf_list | todf_list | safe }},
    }
    dai(profile, mac_addr, ida)

setup()

{{ "\n" }}
# {{ odf_list | todf_list | safe }} 讀取感測器後會自動更新
# 請勿修改上方程式碼

freq = 120        # 更新頻率(Hz)

# 初始化場景
def scene_init():
    global label_info
    scene = display(width=800, height=700, center = vector(10, 15, 0), background=vector(0.5, 0.5, 0))
    label_info = label( pos=vec(10,20,0), text='')

# 每秒鐘更新顯示數據
def update_info():
    global label_info
    {% set label_text = {'cont':''} %}
    {%- set value_list = [] -%}
    {%- for df_name, _ in odf_list -%}
        {%- if "_O" in df_name -%}
            {%- set df_name = df_name[:-2].lower() -%}
            {%- if df_name == "humidity" or df_name == "uv" or df_name == "alcohol" -%}
                {%- if value_list.append(df_name) -%}
                {%- endif -%}
                {%- if value_list.append(df_name+'_time') -%}
                {%- endif -%}
                {%- set tmp = df_name+': {:.2f} {}\\n' -%}
            {%- else -%}
                {%- if value_list.append(df_name+'.x') -%}
                {%- endif -%}
                {%- if value_list.append(df_name+'.y') -%}
                {%- endif -%}
                {%- if value_list.append(df_name+'.z') -%}
                {%- endif -%}
                {%- if value_list.append(df_name+'_time') -%}
                {%- endif -%}
                {%- set tmp = df_name+': {:.2f} {:.2f} {:.2f} {}\\n' -%}
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

    label_info.text='{{label_text.cont}}'.format({{value_list|join(',')}})

scene_init()

cnt = 0
while True:
    rate(freq)
    cnt = cnt + 1
    if cnt % (freq // 5) == 0:
        update_info()
