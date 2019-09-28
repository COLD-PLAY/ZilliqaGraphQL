__author__ = "ZhouLiao"
import requests, execjs, time
# from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher
from func_timeout import *
from pyzil.account import Account
from pyzil.crypto.zilkey import is_bech32_address

data = {
	"id": "1",
	"jsonrpc": "2.0",
	"method": "",
	"params": [""]
}

class GetData(object):
	def __init__(self, uri, user, pwd, curTxBlockNum):
		self.curTxBlockNum = curTxBlockNum
		self.jsCode = '''
			var hashjs = require('hash.js');
			function getAddress(pubKey) {
				return hashjs.sha256().update(pubKey, 'hex').digest('hex').slice(24);
			}
		'''
		self.eval = execjs.compile(self.jsCode)
	
	# 输出至控制台以及log 文件中
	def printf(self, message):
		print(message)

	def getAddress(self, address, type_):
		if type_ == "pubKey":
			old_address = self.eval.call("getAddress", address[2:])
			account = Account(address=old_address)
			return (old_address, account.bech32_address)
		elif type_ == "toBech32":
			if is_bech32_address(address): # no need to transfer to bech32 format
				return (address, address)
			account = Account(address=address)
			return (address, account.bech32_address)

	def getResult(self, method, params):
		data["method"] = method
		data["params"] = [params]
		try:
			res = requests.post("https://api.zilliqa.com/", json=data, timeout=10).json()
			return res["result"] if "result" in res else res
		except requests.exceptions.RequestException as e:
			self.printf("ERROR: Api Connect Timeout: Recall Api!")
			return self.getResult(method, params)

	def getTxBlcokData(self, startBlock, endBlock):
		for i in range(startBlock, endBlock+1):
			self.getOneTxBlcokData(str(i))

	def getOneTxBlcokData(self, blockNum):
		self.printf("the %s TxBlock %s" % (blockNum, time.strftime("%y-%m-%d %H:%M:%S", time.localtime())))

		res = self.getResult("GetTxBlock", blockNum)
		while "header" not in res or res["header"]["Timestamp"] == "0":
			# 表示到达最新的一个块，等一分钟再继续更新
			self.printf("Waiting for Next Block %s" % time.strftime("%y-%m-%d %H:%M:%S", time.localtime()))
			time.sleep(60)
			res = self.getResult("GetTxBlock", blockNum)

		# 当TxBlock中有交易时，获取交易信息以及交易双方的账户信息并存入Neo4j中
		if res["header"]["NumTxns"]:
			self.printf("%d Txs in all" % res["header"]["NumTxns"])
			self.getTxData(res["header"]["BlockNum"])

	def getDsBlockData(self, startBlock, endBlock):
		for i in range(startBlock, endBlock+1):
			self.getOneDsBlcokData(str(i))

	# 返回DsBlock 节点
	def getOneDsBlcokData(self, blockNum):
		self.printf("the %s DsBlock %s" % (blockNum, time.strftime("%y-%m-%d %H:%M:%S", time.localtime())))
		res = self.getResult("GetDsBlock", blockNum)
	
	def getTxData(self, txBlockNum):
		res, order = self.getResult("GetTransactionsForTxBlock", txBlockNum), 1
		while "error" in res:
			self.printf("ERROR: get microblock failed! recatch txs!" + res["error"]["message"])
			res = self.getResult("GetTransactionsForTxBlock", txBlockNum)
		for MicroBlock in res:
			if not MicroBlock:
				continue
			for txHash in MicroBlock:
				self.getOneTxData(txBlockNum, txHash, order)
				order += 1
	
	# 获取一条交易的信息
	@func_set_timeout(60)
	def getOneTxData(self, txBlockNum, txHash, order):
		self.printf("The %s transaction %s" % (txHash, time.strftime("%y-%m-%d %H:%M:%S", time.localtime())))

		res_ = self.getResult("GetTransaction", txHash)
		# 获取交易信息时出错
		############################################# 待修改
		if "error" in res_:
			self.printf("ERROR: get txn info failed!" + res_["error"]["message"])
			return -1
			
		# 解决调用api 时可能产生的问题
		while "receipt" not in res_:
			res_ = self.getResult("GetTransaction", txHash)

		# receipt不符合格式 重新规整一下
		res_["cumulative_gas"] = res_["receipt"]["cumulative_gas"]
		res_["epoch_num"] = res_["receipt"]["epoch_num"]
		res_["success"] = str(res_["receipt"]["success"])
		res_.pop("receipt")

	def run(self):
		while True:
			self.getOneTxBlcokData(str(self.curTxBlockNum))
			self.curTxBlockNum += 1

if __name__ == "__main__":
	uri, user, pwd, curTxBlockNum = "http://localhost:7474", "neo4j", "liaozhou1998", 185174
	Geter = GetData(uri, user, pwd, curTxBlockNum)
	Geter.run()