from netmiko import ConnectHandler
import time

# デバイスへの接続情報を設定します
device = {
    'device_type': 'cisco_xr',
    'ip': 'IPアドレス', #IPアドレスを書き換えてください
    'username': 'ユーザ名', #ユーザ名を書き換えてください
    'password': 'パスワード', #パスワードを書き換えてください
}

# BGP neighborを設定
neighbor_ip = '192.168.0.2'  # BGP neighborのIPアドレスを設定

# しきい値を設定
threshold = 100  # トラフィックのしきい値をMbpsで設定
recovery_threshold = 90  # トラフィックが戻ったと判定するしきい値をMbpsで設定

# netmikoを使用してデバイスに接続
with ConnectHandler(**device) as net_connect:
    # 無限ループを開始
    while True:
        # インターフェースの情報を取得
        output = net_connect.send_command('show interface GigabitEthernet0/0/0/0')
        
        # トラフィックの情報を取得
        for line in output.splitlines():
            if 'input rate' in line:
                input_rate = int(line.split()[2])
                break
        
        # トラフィックがしきい値を超えた場合
        if input_rate > threshold:
            # 経路の広報を停止
            config_commands = [
                f'router bgp 65000',
                f'neighbor {neighbor_ip} route-policy BLOCK-NEIGHBOR in',
            ]
            net_connect.send_config_set(config_commands)
            print(f'{neighbor_ip}: Traffic exceeded the threshold ({input_rate} Mbps), blocking inbound routes.')
        
        # トラフィックが戻った場合
        elif input_rate < recovery_threshold:
            # 経路の広報を再開
            config_commands = [
                f'router bgp 65000',
                f'no neighbor {neighbor_ip} route-policy BLOCK-NEIGHBOR in',
            ]
            net_connect.send_config_set(config_commands)
            print(f'{neighbor_ip}: Traffic has returned to normal ({input_rate} Mbps), allowing inbound routes.')
        
        # しきい値を超えていない場合は何もしない
        else:
            print(f'{neighbor_ip}: Traffic is normal ({input_rate} Mbps).')
        
        # 10秒間待機してから再度トラフィックをチェック
        time.sleep(10)
