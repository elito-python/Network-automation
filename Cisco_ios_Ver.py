from netmiko import ConnectHandler
import time

# デバイスへの接続情報を設定します
device = {
    "device_type": "cisco_ios", 
    "ip": "IPアドレス", #IPアドレスを書き換えてください
    "username": "ユーザ名", #ユーザ名を書き換えてください
    "password": "パスワード", #パスワードを書き換えてください
}


# インターフェース名、しきい値、およびBGPネイバーのIPアドレスを設定
interface = "対象のPNIのIF" 
threshold = 100
neighbor_ip = "IPアドレス"  #BGPネイバーのIPアドレスを書き換えてください
neighbor_as = "AS番号"  #AS番号を書き換えてください
route-policy = "ルートポリシ" #ルートポリシを書き換えてください

# 経路の広報を停止する関数
def stop_bgp_advertising():
    net_connect = ConnectHandler(**device)
    net_connect.send_command("router bgp " + neighbor_as)
    net_connect.send_command("neighbor " + neighbor_ip + " route-map " + route-policy + " out")
    net_connect.disconnect()

# 経路の広報を再開する関数
def start_bgp_advertising():
    net_connect = ConnectHandler(**device)
    net_connect.send_command("router bgp " + neighbor_as)
    net_connect.send_command("no neighbor " + neighbor_ip + " route-map " + route-policy + " out")
    net_connect.disconnect()

#show interfaces BExx | i rate
  #30 second input rate 40690331000 bits/sec, 6554136 packets/sec
  #30 second output rate 30269366000 bits/sec, 3587287 packets/sec
    
while True:
    # トラフィック量を取得
    net_connect = ConnectHandler(**device)
    output = net_connect.send_command("show interface " + interface + " | include rate")
    net_connect.disconnect()
    input = int(output.split()[4])
    output = int(output.split()[-4])
    
    if input>output:
        traffic = input
    else:
        traffic = output
    
    # トラフィックが閾値を超えている場合は経路広報を停止
    if traffic > threshold:
        stop_bgp_advertising()
    
    # トラフィックが閾値以下になった場合は経路広報を再開
    if traffic <= threshold * 0.9:
        start_bgp_advertising()
    
    # 5秒間待機してループを再開
    time.sleep(5)
