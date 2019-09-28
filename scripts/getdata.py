__author__ = "ZhouLiao"
import requests, execjs, time
from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher
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
		self.graph = Graph(uri, username=user, password=pwd)
		self.matcher_node = NodeMatcher(self.graph)
		self.matcher_relation = RelationshipMatcher(self.graph)
		self.curTxBlockNum = curTxBlockNum
		# self.graph.delete_all()
		self.jsCode = '''
			var hashjs = require('hash.js');
			function getAddress(pubKey) {
				return hashjs.sha256().update(pubKey, 'hex').digest('hex').slice(24);
			}
		'''
		self.eval = execjs.compile(self.jsCode)
	
	# 输出至控制台以及log 文件中
	def printf(self, message):
		# print(message)
		with open("../log/%s.log" % time.strftime('%Y-%m-%d',time.localtime(time.time())), "a") as file:
			file.write(message + '\r')

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
		# 若该Block存在，则删除
		txBlock = self.matcher_node.match("TxBlock", BlockNum=blockNum).first()
		if txBlock:
			self.printf("TxBlock \t%s existed!" % blockNum)
			self.graph.delete(txBlock)

		res = self.getResult("GetTxBlock", blockNum)
		while "header" not in res or res["header"]["Timestamp"] == "0":
			# 表示到达最新的一个块，等一分钟再继续更新
			self.printf("Waiting for Next Block %s" % time.strftime("%y-%m-%d %H:%M:%S", time.localtime()))
			time.sleep(60)
			res = self.getResult("GetTxBlock", blockNum)
		# 创建TxBlock节点以及与所属DSBlock之间的从属关系
		TxBlock = Node("TxBlock")
		TxBlock.update({"HeaderSign": res["body"]["HeaderSign"]})
		TxBlock.update(res["header"])
		# 由于一个TxBlock块由多个MicroBlock组成
		for index, block in enumerate(res["body"]["MicroBlockInfos"]):
			TxBlock.update({"MicroBlock%dHash" % index: block["MicroBlockHash"], "MicroBlock%dTxnRootHash" % index: block["MicroBlockTxnRootHash"]})
		DsBlock = self.matcher_node.match("DsBlock", BlockNum=res["header"]["DSBlockNum"]).first()
		# 更新当前TxBlock 所对应的DsBlock
		if not DsBlock:
			DsBlock = self.getOneDsBlcokData(res["header"]["DSBlockNum"])
		Tx2Ds = Relationship(TxBlock, "in", DsBlock)
		Ds2Tx = Relationship(DsBlock, "has", TxBlock)
		##########################################################
		# 为has 和in 属性添加排序信息，即TxBlock 是DSBlock 中的第几个
		cur_number = len(self.matcher_relation.match([DsBlock], "has"))
		Tx2Ds["order"] = cur_number+1
		Ds2Tx["order"] = cur_number+1

		# 创建Miner节点及其与TxBlock节点之间的挖与被挖关系
		miner_addr_old, miner_addr_new = self.getAddress(res["header"]["MinerPubKey"], type_="pubKey")
		Miner, existed = self.getAccountData(miner_addr_old, miner_addr_new)
		Miner2Tx = Relationship(Miner, "mine", TxBlock)
		Tx2Miner = Relationship(TxBlock, "mined", Miner)

		self.graph.create(TxBlock)
		self.graph.create(Tx2Ds)
		self.graph.create(Ds2Tx)
		if not existed:
			self.graph.create(Miner)
		self.graph.create(Miner2Tx)
		self.graph.create(Tx2Miner)

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
		# 创建DSBlock节点
		DsBlock = Node("DsBlock")
		DsBlock.update(res["header"])
		DsBlock.update({"signature": res["signature"]})

		# 创建Miner节点及其与DsBlock节点之间的挖与被挖关系
		miner_addr_old, miner_addr_new = self.getAddress(res["header"]["LeaderPubKey"], type_="pubKey")
		Miner, existed = self.getAccountData(miner_addr_old, miner_addr_new)
		Miner2Ds = Relationship(Miner, "mine", DsBlock)
		Ds2Miner = Relationship(DsBlock, "mined", Miner)

		self.graph.create(DsBlock)
		if not existed:
			self.graph.create(Miner)
		self.graph.create(Miner2Ds)
		self.graph.create(Ds2Miner)
		return self.matcher_node.match("DsBlock", BlockNum=blockNum).first()
	
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
		Tx = self.matcher_node.match("Tx", ID=txHash).first()
		if Tx:
			self.printf("Tx %s existed!" % txHash)
			# Tx 已存在时，仍需建立TxBlock 与Tx 之间的关系
			TxBlock = self.matcher_node.match("TxBlock", BlockNum=txBlockNum).first()
			Tx2TxBlock = Relationship(Tx, "in", TxBlock)
			TxBlock2Tx = Relationship(TxBlock, "has", Tx)
			##########################################################
			# 为has 和in 属性添加排序信息，即Tx 是TxBlock 中的第几个
			Tx2TxBlock["order"] = order
			TxBlock2Tx["order"] = order
			self.graph.create(Tx2TxBlock)
			self.graph.create(TxBlock2Tx)
			return

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

		from_addr_old, from_addr_new = self.getAddress(res_["senderPubKey"], type_="pubKey")
		to_addr_old, to_addr_new = self.getAddress(res_["toAddr"], type_="toBech32")

		# 创建Tx的节点以及与所属TxBlock之间的从属关系
		Tx = Node("Tx")
		Tx.update(res_)
		# 由于res_["senderPubKey"]不是直接的地址，需要转换一下再将发送者的地址存储，新增bech32 格式地址存储
		Tx.update({"fromAddrNew": from_addr_new, "toAddrNew": to_addr_new})
		
		TxBlock = self.matcher_node.match("TxBlock", BlockNum=txBlockNum).first()
		Tx2TxBlock = Relationship(Tx, "in", TxBlock)
		TxBlock2Tx = Relationship(TxBlock, "has", Tx)
		##########################################################
		# 为has 和in 属性添加排序信息，即Tx 是TxBlock 中的第几个
		Tx2TxBlock["order"] = order
		TxBlock2Tx["order"] = order

		# 创建账户节点以及所参与Tx之间的发送接收关系，其中返回中
		# 有一个标记信息，表示数据库中是否已经存在该节点
		From_Account, existed_from = self.getAccountData(from_addr_old, from_addr_new)
		To_Account, existed_to = self.getAccountData(to_addr_old, to_addr_new)
		From2Tx = Relationship(From_Account, "send", Tx)
		Tx2From = Relationship(Tx, "from", From_Account)
		To2Tx = Relationship(To_Account, "receive", Tx)
		Tx2To = Relationship(Tx, "to", To_Account)

		From2To = Relationship(From_Account, "traded", To_Account)
		###################################################
		# 之前便加过TxHash
		From2To['TxHash'] = txHash
		To2From = Relationship(To_Account, "traded", From_Account)
		To2From['TxHash'] = txHash

		self.graph.create(Tx)
		self.graph.create(Tx2TxBlock)
		self.graph.create(TxBlock2Tx)
		# 若没在数据库中
		if not existed_from:
			self.graph.create(From_Account)
		if not existed_to:
			self.graph.create(To_Account)
		self.graph.create(From2Tx)
		self.graph.create(Tx2From)
		self.graph.create(To2Tx)
		self.graph.create(Tx2To)
		self.graph.create(From2To)
		self.graph.create(To2From)

	def getAccountData(self, address_old, address_new):
		# 当账户已经在数据库中时：
		Account = self.matcher_node.match("Account", address=address_old).first()
		res = self.getResult("GetBalance", address_old)
		if Account:
			# self.printf("account %s existed!" % address)
			if "error" in res:
				Account.update({"balance": "0", "existed": "false"})
			else:
				Account.update({"balance": res["balance"], "existed": "true"})
			self.graph.push(Account)
			return Account, 1
		Account = Node("Account", address=address_old)
		Account.update({"address_new": address_new})
		# 获取账户当前的余额
		if "error" in res:
			Account.update({"balance": "0", "existed": "false"})
		else:
			Account.update({"balance": res["balance"], "existed": "true"})
		return Account, 0

	def run(self):
		# 先对DSBlock进行存储
		# self.getDsBlockData()
		# 在对TxBlock存储的过程中将所有的交易信息
		# 以及交易过程中的账户信息一并存储到数据库
		curTxBlock = self.matcher_node.match("TxBlock", BlockNum=str(self.curTxBlockNum)).first()
		if curTxBlock: self.graph.delete(curTxBlock)
		try:
			while True:
				self.getOneTxBlcokData(str(self.curTxBlockNum))
				self.curTxBlockNum += 1
		except FunctionTimedOut:
			self.printf("ERROR: Running Timeout: Restart!")
			self.run()
		except Exception as e:
			self.printf("ERROR: %s: Restart!" % str(e))
			self.run()

if __name__ == "__main__":
	uri, user, pwd, curTxBlockNum = "http://localhost:7474", "neo4j", "liaozhou1998", 232894
	Geter = GetData(uri, user, pwd, curTxBlockNum)
	Geter.run()