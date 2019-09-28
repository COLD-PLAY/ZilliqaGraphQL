__author__ = "ZhouLiao"
from py2neo import Graph, Node, Relationship, NodeMatcher
import requests, execjs, time, json

data = {
	"id": "1",
	"jsonrpc": "2.0",
	"method": "",
	"params": [""]
}

# curl -d '{
#     "id": "1",
#     "jsonrpc": "2.0",
#     "method": "GetBalance",
#     "params": ["21f50477b4ebecf86a737e22cd0f611b7184665b"]
# }' -H "Content-Type: application/json" -X POST "https://api.zilliqa.com/"

jsCode = '''
	var hashjs = require('hash.js');
	function getAddress(pubKey) {
		return hashjs.sha256().update(pubKey, 'hex').digest('hex').slice(24);
	}
'''
eval = execjs.compile(jsCode)

def getAddress(pubKey):
	return eval.call("getAddress", pubKey[2:])

def getResult(method, params):
	data["method"] = method
	data["params"] = [params]
	try:
		res = requests.post("https://api.zilliqa.com/", json=data, timeout=10).json()
		return res["result"] if "result" in res else res
	except requests.exceptions.RequestException as e:
		print("///////////////////////////连接超时: 重试!")
		print(e)
		return getResult(method, params)
def test():
	res = getResult("GetBalance", "1931e8bb19518a049a2824333baee89a433559c6")
	res = getResult("GetRecentTransactions", "")
	res = getResult("GetTransaction", "7581733a5a7b6edf1778446f8c01565637025cb43fa6240a01ddcaeb6ff80f4d")
	res = getResult("GetTxBlock", "60674")
	res = getResult("GetDsBlock", "1430")
	# 7581733a5a7b6edf1778446f8c01565637025cb43fa6240a01ddcaeb6ff80f4d
	res = getResult("GetTransactionsForTxBlock", "60673")
	print(res)
	txs = 0
	for i in range(59903, 60007):
		print(i)
		res = getResult("GetTxBlock", str(i))
		print(res["header"]["NumTxns"])
		txs += int(res["header"]["NumTxns"])
	print(txs)
	address = getAddress("0x02545402B1D5BCADDAEF278FAEF5FD926C6917A5CB3E17FC838F863ED041B88F5A")
	print(address)
	# 1931e8bb19518a049a2824333baee89a433559c6
	# 26AFb91DC1B2083E64fe58b3CCBe943D945F612E

	file = open("out.log", "a")
	for i in range(4):
		file.write(time.strftime("%y-%m-%d %H:%M:%S", time.localtime())+'\r')
	print("%s" % time.strftime("%y-%m-%d %H:%M:%S", time.localtime()))
	a = []

# res = getResult("GetTransactionsForTxBlock", "175334")
# print(res)
# err, nrr = 0, 0
# for txs in res:
# 	if txs:
# 		for tx in txs:
# 			print(tx)
# 			res_ = getResult("GetTransaction", "tx")
# 			print(res_)
# 			if "error" in res_:
# 				err += 1
# 			else: nrr += 1
# print(err, nrr)

txs = [
	# "93cd69e14e5f624f14a09254c47a729fd2295d69bedfaac03056513b3ff6af29",
	# "8d702cb302fcb25fe0b33b07bbd11c816815dda5747af24326aeac20ecfd6c73",
	# "05bab941d5eeac7ce78b8bc8d890f42675b07975c678ae5184a50df67913ae26",
	# "078efcf10473251f4a4ba8c4ce18810f06d3cafcf2eb8122a5f4293e9d2bdea3",
	# "097a0ef43987adcf511c0f140ac316b3f7ac8b1819fdd6a1c44da82fbad541ae",
	# "0aa3c892a183457dd4b0252e960466635c2508f6a1b6f528e84fbbc7682c6710",
	# "0b6beb2cea06737a531f02493f5aa788afbde15fd3e87006b65800d463909ee8",
	# "1355121906ac35972e6b65026b07b427b5c4ae148c225a9a53b026e5749d4705",
	# "255f44c45f43197cbc53f2b33795093186d4cf12dead77b2e5166a88002f294a",
	# "2909e3341a97d57ffaccd514cb2e9d6ea402b1be927125774ce9501fb813b25b",
	# "297a221754dd0b34b43adeadb762d95ee6bdf0a96fbbc42e06f6ab5a47f559e6",
	# "303908b5ccba037748bb93946092470247192e25c7c0c5f17d55dca19122a9c9",
	# "35ed1d1e0611b805a5de8b5ffa162192c6a7bfb5b592916cdda8fa856bd86a5b",
	# "4fdcb5cee42ca7c0f639101c08658019ed55745094d1d0f6abcca2981ee3adc9",
	# "5161e9eda90904f601d16702586d35bb82db702e88f24b7a36c1691dde6e7f4e",
	# "61be4d61ec71740f835b2910c182fe35d161cfc1f3b2c4b9debef3b229b90ef3",
	# "ada4f7b094d718bedffdc4827ab1e0ab2bd14d5fb2840505f81a4ddcf8c1bff3",
	# "d1b8d0c891e88ea12bea3fb9c58b2fc69a5cdffe46024f6a17f51c4e2cc807b7",
	# "e0b14cba55e1e1e17e5be24a6b77ab3109ed788360aeb8652f74c817b3e4d365",
	"afffe57d469e428c176b4e74ba81fad59525ca34f5380d12ec3fb3985e6db5d6",
	"6eaa46d2e4b6940a0435d90e6bb836f64a3008925d3cb0ae0e603584e6db2dbd"
]

# for tx in txs:
# 	print(tx)
# 	res__ = getResult("GetTransaction", tx)
# 	# while "error" in res__:
# 	# 	res__ = getResult("GetTransaction", tx)
# 	# 	print(tx, "error")
# 	if "error" in res__:
# 		print("error")

# account = Account(address="a11de7664f55f5bdf8544a9ac711691d01378b4c")
# print(account.bech32_address)
print(233)
# res = getResult("GetTxBlock", "202775")
# import requests, json
# res = requests.post("https://api.zilliqa.com/", json={
# 	"id": "1",
# 	"jsonrpc": "2.0",
# 	"method": "GetTxBlock",
# 	"params": ["202775"]
# }, timeout=10).json()
# print(res)
print("../log/%s.log" % time.strftime('%Y-%m-%d',time.localtime(time.time())))