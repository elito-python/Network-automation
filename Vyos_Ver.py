from netmiko import ConnectHandler
import time

# デバイス情報を設定します
device = {
    'device_type': 'vyos',
    'ip': 'IPアドレス',  # VyOSデバイスのIPアドレスに置き換えてください
    'username': 'username',  # ユーザー名に置き換えてください
    'password': 'password',  # パスワードに置き換えてください
}

# コマンドを定義します
show_interface_command = 'show interfaces ethernet eth0 | grep "RX rate\|TX rate"'

# BGPネイバーのIPアドレスとAS番号を設定します
neighbor_ip = 'IPアドレス'  # BGPネイバーのIPアドレスを書き換えてください
neighbor_as = 'AS番号'  # BGPネイバーのAS番号に置き換えてください

# 初期トラフィック値を設定します
traffic_value = 0

while True:
    with ConnectHandler(**device) as ssh:
        # インターフェースのトラフィック情報を取得します
        output = ssh.send_command(show_interface_command)

        # トラフィック情報から値を取得します
        rx_value = int(output.split()[3])
        tx_value = int(output.split()[7])
        current_traffic_value = rx_value + tx_value

        # トラフィックが100Mbpsを超えた場合はBGP広報経路を停止します
        if current_traffic_value > 100 and traffic_value <= 100:
            config_commands = [
                'configure',
                'set protocols bgp neighbor {} route-map STOP_TRAFFIC out'.format(neighbor_ip),
                'commit',
                'exit',
                'set firewall name STOP_TRAFFIC default-action drop',
                'commit',
                'exit'
            ]
            ssh.send_config_set(config_commands)
            print(f'Traffic exceeded 100Mbps, BGP route to {neighbor_ip} stopped')

        # トラフィックが90Mbps以下に戻った場合はBGP広報経路を再度開始します
        elif current_traffic_value <= 90 and traffic_value > 90:
            config_commands = [
                'configure',
                'delete protocols bgp neighbor {} route-map STOP_TRAFFIC out'.format(neighbor_ip),
                'commit',
                'exit'
            ]
            ssh.send_config_set(config_commands)
            print(f'Traffic dropped below 90Mbps, BGP route to {neighbor_ip} started')

        # 現在のトラフィック値を更新します
        traffic_value = current_traffic_value

    # 10秒間スリープします
    time.sleep(10)
