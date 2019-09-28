__author__ = "ZhouLiao"
from pyzil.account import Account
from pyzil.crypto.zilkey import is_bech32_address
from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher

# 将所有的交易中的fromAddr 和toAddr 新增其对应的bech32 格式的地址
uri, user, pwd = "http://localhost:7474", "neo4j", "liaozhou1998"
graph = Graph(uri, username=user, password=pwd)
matcher_node = NodeMatcher(graph)

def getBech32(address):
    if is_bech32_address(address):
        return address
    account = Account(address=address)
    return account.bech32_address

def printf(message):
    print(message)
    with open("../log/update.log", "a") as file:
        file.write(message + '\r')

# txs = matcher_node.match("Tx")
accounts = matcher_node.match("Account")
# for tx in txs:
#     fromAddr, toAddr = tx["fromAddr"], tx["toAddr"]
#     fromAddrNew, toAddrNew = getBech32(fromAddr), getBech32(toAddr)
#     tx.update({"fromAddrNew": fromAddrNew, "toAddrNew": toAddrNew})
#     printf(fromAddr + "," + fromAddrNew + "," + toAddr + "," + toAddrNew)
#     graph.push(tx)

for account in accounts:
    address = account["address"]
    address_new = getBech32(address)
    account.update({"address_new": address_new})
    printf(address + "," + address_new)
    graph.push(account)