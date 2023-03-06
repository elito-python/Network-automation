import time
from netmiko import ConnectHandler

# デバイスへの接続情報を設定します
device = {
    'device_type': 'cisco_xr',　
    'ip': 'IPアドレス', #IPアドレスを書き換えてください
    'username': 'ユーザー名', #ユーザ名を書き換えてください
    'password': 'パスワード', #パスワードを書き換えてください
}

# BGP経路をdenyするためのコマンドを設定します
deny_command = 'router bgp AS番号\n neighbor IPアドレス route-policy deny_traffic out\n' #AS番号とIPアドレスを書き換えてください

# BGP経路を再度広報するためのコマンドを設定します
allow_command = 'router bgp AS番号\n neighbor IPアドレス route-policy allow_traffic out\n'#AS番号とIPアドレスを書き換えてください

# トラフィックレートを監視するためのインターバルを設定します（秒単位）
monitor_interval = 5

# ネットワーク上のトラフィックレートのしきい値を設定します（Mbps単位）
traffic_threshold = 90

# Netmikoを使用してデバイスに接続します
with ConnectHandler(**device) as net_connect:
    while True:
        # show interfacesコマンドを実行して、インタフェースのトラフィックレートを取得します
        output = net_connect.send_command('show interfaces bundle-ether1 | include rate')
        traffic_rate = int(output.split()[1]) / 1000000  # Mbps単位に変換します

        # トラフィックレートがしきい値を超えた場合、BGP経路をdenyします
        if traffic_rate > traffic_threshold:
            net_connect.send_config_set(deny_command)
            print(f'Traffic rate is {traffic_rate} Mbps. Denying BGP routes...')
        
        # トラフィックレートがしきい値を下回った場合、BGP経路を再度広報します
        elif traffic_rate <= traffic_threshold * 0.9:  # しきい値の90%以下になったらBGP広報を再開します
            net_connect.send_config_set(allow_command)
            print(f'Traffic rate is {traffic_rate} Mbps. Allowing BGP routes...')
        
        # 監視インターバルを待ちます
        time.sleep(monitor_interval)
