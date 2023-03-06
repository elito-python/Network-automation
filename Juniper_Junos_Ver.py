from netmiko import ConnectHandler
import time

# デバイスへの接続情報を設定します
device = {
    'device_type': 'juniper_junos', 
    'ip': 'IPアドレス', #IPアドレスを書き換えてください
    'username': 'ユーザ名', #ユーザ名を書き換えてください
    'password': 'パスワード', #パスワードを書き換えてください
}

# IFの監視対象となるIF名
interface = '対象のPNIのIF' 

# 監視間隔（秒）
monitor_interval = 60

# BGP広報用のポリシー名
bgp_policy_name = 'my-policy'

# ポリシーに設定する条件（トラフィック量）
traffic_threshold = 100000000

# Netmikoを使用してJuniper Junosデバイスに接続する
with ConnectHandler(**device) as net_connect:
    while True:
        # IFの統計情報を取得する
        output = net_connect.send_command(f'show interfaces {interface} extensive')

        # 統計情報からIFのトラフィック情報を抽出する
        for line in output.splitlines():
            if 'Input rate' in line:
                input_rate = int(line.split()[-2])
            elif 'Output rate' in line:
                output_rate = int(line.split()[-2])

        # IFのトラフィックが指定の閾値を超えた場合
        if input_rate > traffic_threshold or output_rate > traffic_threshold:
            # BGPのポリシーを変更して広報するルートをフィルタリングする
            net_connect.send_config_set([
                f'set policy-options policy-statement {bgp_policy_name} term 1 from protocol bgp',
                'set policy-options policy-statement {} term 1 then reject'.format(bgp_policy_name),
                'commit'
            ])
        # トラフィックが閾値以下に戻った場合
        elif input_rate <= traffic_threshold and output_rate <= traffic_threshold:
            # BGPのポリシーを変更してフィルタリングを解除する
            net_connect.send_config_set([
                f'delete policy-options policy-statement {bgp_policy_name}',
                'commit'
            ])

        # 監視間隔だけスリープする
        time.sleep(monitor_interval)
