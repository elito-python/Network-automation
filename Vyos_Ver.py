from netmiko import ConnectHandler
import time

# デバイスへの接続情報を設定します
device = {
    "device_type": "vyos",
    "ip": "IPアドレス", #IPアドレスを書き換えてください
    "username": "ユーザ名", #ユーザ名を書き換えてください
    "password": "パスワード", #パスワードを書き換えてください
}

# インターフェース名、しきい値、およびBGPネイバーのIPアドレスを設定
interface = "対象のPNIのIF" 
threshold = 100
# BGPネイバーのIPアドレスとAS番号を設定します
neighbor_ip = "IPアドレス"  # BGPネイバーのIPアドレスを書き換えてください
neighbor_as = "AS番号"  # BGPネイバーのAS番号に置き換えてください

# 経路の広報を停止する関数
def stop_bgp_advertising():
    net_connect = ConnectHandler(**device)
    net_connect.send_command("configure")
    net_connect.send_command("set protocols bgp neighbor "+ neighbor_ip +" route-map STOP_TRAFFIC out")
    net_connect.send_command("commit")
    net_connect.send_command("save")
    net_connect.send_command("exit")
    net_connect.disconnect()

# 経路の広報を再開する関数
def start_bgp_advertising():
    net_connect = ConnectHandler(**device)
    net_connect.send_command("configure")
    net_connect.send_command("delete protocols bgp neighbor "+ neighbor_ip +" route-map STOP_TRAFFIC out")
    net_connect.send_command("commit")
    net_connect.send_command("save")
    net_connect.send_command("exit")
    net_connect.disconnect()

while True:
    # トラフィック量を取得
    net_connect = ConnectHandler(**device)
    output = net_connect.send_command("show interfaces ethernet "+ interface +" | match rate")
    net_connect.disconnect()
    traffic = int(output.split()[-2])
    
    # トラフィックが閾値を超えている場合は経路広報を停止
    if traffic > threshold:
        stop_bgp_advertising()
    
    # トラフィックが閾値以下になった場合は経路広報を再開
    if traffic <= threshold * 0.9:
        start_bgp_advertising()
    
    # 5秒間待機してループを再開
    time.sleep(5)
