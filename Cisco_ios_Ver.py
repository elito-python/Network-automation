from netmiko import ConnectHandler
import time

# Cisco IOSのログイン情報を設定
device = {
    "device_type": "cisco_ios", 
    "ip": "IPアドレス", #IPアドレスを書き換えてください
    "username": "ユーザ名", #ユーザ名を書き換えてください
    "password": "パスワード", #パスワードを書き換えてください
}

# インターフェース名、しきい値、およびBGPネイバーのIPアドレスを設定
interface = "対象のPNIのIF" 
threshold = 100
bgp_neighbor = "IPアドレス" #IPアドレスを書き換えてください

# 経路の広報を停止する関数
def stop_bgp_advertising():
    net_connect = ConnectHandler(**device)
    net_connect.send_command("router bgp AS番号")　#AS番号を書き換えてください
    net_connect.send_command("neighbor " + bgp_neighbor + " route-map STOP_ADVERTISING in")
    net_connect.disconnect()

# 経路の広報を再開する関数
def start_bgp_advertising():
    net_connect = ConnectHandler(**device)
    net_connect.send_command("router bgp AS番号")　#AS番号を書き換えてください
    net_connect.send_command("no neighbor " + bgp_neighbor + " route-map STOP_ADVERTISING in")
    net_connect.disconnect()

while True:
    # トラフィック量を取得
    net_connect = ConnectHandler(**device)
    output = net_connect.send_command("show interface " + interface + " | include rate")
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
