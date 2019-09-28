import requests, time, multiprocessing

data = {
	"id": "1",
	"jsonrpc": "2.0",
	"method": "GetTxBlock",
	"params": [""]
}
r = []
def fun(s, e):
	for i in range(s, e+1):
		print("第%d个TxBlock %s" % (i, time.strftime("%H:%M:%S", time.localtime())))
		data["params"] = [str(i)]
		res = requests.post("https://api.zilliqa.com/", json=data).json()["result"]
		print(res)
		if res["header"]["NumTxns"]:
			print("////////////////////%d: %d" % (i, res["header"]["NumTxns"]))
		print("////////////////////%s" % res["header"]["Rewards"])

if __name__ == "__main__":
	# pool = multiprocessing.Pool(10)
	# for i in range(10):
	# 	pool.apply_async(fun, (50000+1000*i+1, 50000+1000*(i+1)))
	# pool.close()
	# pool.join()

	fun(99, 60000)

# match()-[r:receive]-() delete r;
# match()-[r:send]-() delete r;
# match()-[r:to]-() delete r;
# match()-[r:traded]-() delete r;
# match(n:Tx) detach delete n;
# match(n:TxBlock{BlockNum:"59903"}) detach delete n;
# match(n:TxBlock{BlockNum:"59945"}) detach delete n;
# match(n:TxBlock{BlockNum:"59946"}) detach delete n;
curl -d '{
    "id": "1",
    "jsonrpc": "2.0",
    "method": "GetBalance",
    "params": ["9a690adac3446b2bb6d9f0bf2ef91c1ecdd198f2"]
}' -H "Content-Type: application/json" -X POST "https://api.zilliqa.com/"