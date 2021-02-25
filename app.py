__author__ = 'ZhouLiao'
from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher
from flask import Flask, render_template, request, jsonify, Response
from logging.config import dictConfig
import json, time
# from flask_talisman import Talisman
from flask_sslify import SSLify

class Core(object):
	def __init__(self, uri, user, pwd):
		self.graph = Graph(uri, username=user, password=pwd)
		self.matcher_node = NodeMatcher(self.graph)
		self.matcher_relation = RelationshipMatcher(self.graph)

	# 将py2neo.data.Node 转换成echarts 可渲染的数据并返回
	def toEchartsNode(self, node):
		label_category = {
			"TxBlock": [node["BlockNum"], 0], "Tx": [node["ID"], 3],
			"Account": [node["address"], 2], "DsBlock": [node["BlockNum"], 1]
		}
		data = {
			"name": str(node.identity), "label": label_category[list(node.labels)[0]][0],
			"category": label_category[list(node.labels)[0]][1]
		}
		data.update(dict(node))
		return data

	def toEchartsRelation(self, relation):
		data = {"id": str(relation.identity),
				"source": str(relation.start_node.identity),
				"target": str(relation.end_node.identity),
				"relationship": list(relation.types())[0]}
		data.update(dict(relation))
		return data

	def getNode(self, label, value):
		if label == "TxBlock" or label == "DsBlock":
			nodes = self.matcher_node.match(label, BlockNum=value)
		elif label == "Account":
			nodes = self.matcher_node.match(label, address=value)
			if not nodes: nodes = self.matcher_node.match(label, address_new=value)
		elif label == "Tx":
			nodes = self.matcher_node.match(label, ID=value)
		if not nodes: self.error("%s %s is not existed!" % (label, value))
		return nodes.first()

	def getRelation(self, nodes, label):
		rels = self.matcher_relation.match(nodes, label)
		label_attr = {"TxBlock": "BlockNum", "DsBlock": "BlockNum", "Account": "address", "Tx": "TxHash"}
		if not rels:
			if len(nodes) == 0:
				self.error("Relation %s is not existed!" % (label))
			elif len(nodes) == 1:
				self.error("Relation %s of <%s: %s> is not existed!" % (
					label, list(nodes[0].labels)[0],
					nodes[0][label_attr[list(nodes[0].labels)[0]]]
				))
			elif len(nodes) == 2:
				self.error("Relation %s between <%s: %s> & <%s: %s> is not existed!" % (
					label, list(nodes[0].labels)[0], nodes[0][label_attr[list(nodes[0].labels)[0]]],
					list(nodes[1].labels)[0], nodes[1][label_attr[list(nodes[1].labels)[0]]]
				))
			else:
				self.error("getRelation() Parameters Wrong!")

		return rels

	# 更新至上一次交易（或矿工）中出现该address 时的官方API 得到的balance
	def getBalance(self, address):
		account = self.getNode("Account", address)
		return [account]

	# 获取address1 和address2 的交易
	# type:
	# 	1. "recent": 返回最近的1个（如果不足则返回全部）交易
	# 	2. "all": 返回所有交易（排序后）
	# 	3. "period": 返回两个TxBlock 之间的交易（排序后）
	def getTxs(self, address1, address2, type="all", start=None, end=None):
		if start and end:
			start, end = int(start), int(end)
		account1 = self.getNode("Account", address1)
		account2 = self.getNode("Account", address2)
		txs_hash, txs = [tx["TxHash"] for tx in self.getRelation([account1, account2], "traded")], []
		for tx_hash in txs_hash:
			txs.append(self.getTx(tx_hash))
		# 按所在的TxBlock 顺序排列
		txs = self.sortTxs(txs)

		if type == "all":
			return txs
		elif type == "recent":
			return txs[0]
		elif type == "period" and start and end and start <= end:
			res = []
			for tx in txs:
				if start <= int(tx["epoch_num"]) <= end:
					res.append(tx)
			return res
		else:
			self.error("getTxs() Parameters Wrong!")
	
	# 对交易节点按所在的TxBlock 倒序排列
	def sortTxs(self, txs):
		return sorted(txs, key=lambda tx: int(tx["epoch_num"]), reverse=True)

	# 对块节点按块号BlockNum 倒序排列
	def sortBlocks(self, blocks):
		return sorted(blocks, key=lambda block: int(block["BlockNum"]), reverse=True)

	# 账户1、2是否发生过交易
	def isTraded(self, address1, address2):
		account1 = self.getNode("Account", address1)
		account2 = self.getNode("Account", address2)
		if not account1 or not account2:
			self.error("Account Not Existed!")
			return False
		if len(self.getRelation([account1, account2], "traded")):
			return True
		return False

	# 获取BlockNum 从start到end过程中的矿工
	def getMiners(self, start, end):
		if not start.isdigit() or not end.isdigit():
			self.error("getMiners() Parameters Wrong: Start & End Should Be Number!")
		miners, start, end = [], int(start), int(end)
		for i in range(start, end+1):
			block = self.getNode("TxBlock", str(i))
			mined = self.getRelation([block], "mined").first()
			miners.append(mined.end_node)
		return miners
	
	# 返回address 账户的所有交易
	def getAccountTxs(self, address):
		txs = []
		account = self.getNode("Account", address)
		sends = self.matcher_relation.match([account], "send")
		reces = self.matcher_relation.match([account], "receive")
		for send in sends:
			txs.append(send.end_node)
		for rece in reces:
			txs.append(rece.end_node)
		txs = self.sortTxs(txs)
		return txs

	# 返回address 账户挖的所有块
	def getMinedBlocks(self, address):
		account, blocks = self.getNode("Account", address), []
		mines = self.getRelation([account], "mine")
		for mine in mines:
			blocks.append(mine.end_node)
		blocks = self.sortBlocks(blocks)
		return blocks

	def error(self, message):
		self.printf("ERROR: %s %s" % (message, time.strftime("%y-%m-%d %H:%M:%S", time.localtime())))
		raise Exception("ERROR: " + message)
	
	def printf(self, message):
		print(message)
		with open("log/query.log", "a") as file:
			file.write(message + '\r')

app = Flask(__name__)
# csp = {
# 	'default-src': '\'self\'',
# 	'script-src': '\'self\''
# }
# Talisman(
# 	app,
# 	content_security_policy=csp,
# 	content_security_policy_nonce_in=['script-src']
# )
SSLify(app)
uri, user, pwd = "http://localhost:7474", "neo4j", "liaozhou1998"
core = Core(uri, user, pwd)

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/docs/')
def docs():
	return render_template("docs.html")

@app.route('/query/', methods=['POST', 'GET'])
def query():
	for key, value in request.form.items():
		if value:
			core.printf("key: %s value: %s %s" % (key, value, time.strftime("%y-%m-%d %H:%M:%S", time.localtime())))

	try:
		if request.form["method"] == "api":
			method = request.form["api_method"]
			if method == "getBalance":
				res = core.getBalance(request.form["parameter1"])
			elif method == "getTxs":
				address1, address2, type_ = request.form["parameter1"], request.form["parameter2"], request.form["parameter3"]
				start, end = request.form["parameter4"], request.form["parameter5"]
				res = core.getTxs(address1, address2, type_, start, end)
			elif method == "getMiners":
				res = core.getMiners(request.form["parameter1"], request.form["parameter2"])
			elif method == "getAccountTxs":
				res = core.getAccountTxs(request.form["parameter1"])
			else:
				res = core.getMinedBlocks(request.form["parameter1"])
			res_ = [core.toEchartsNode(_) for _ in res]
			res_ = {"nodes": res_, "links": []}
		else:
			res = core.graph.run(request.form["cql"])
			# 表示是node
			if res.keys()[0] == 'n':
				res = [_.values()[0] for _ in res]
				res_ = [core.toEchartsNode(_) for _ in res]
				res_ = {"nodes": res_, "links": []}
			# 否则是relation
			else:
				res = [_.values()[0] for _ in res]
				res_ = [core.toEchartsRelation(_) for _ in res]
				res_ = {"nodes": [], "links": res_}
		res = [dict(_) for _ in res]
		return render_template("result.html", res=json.dumps(res), res_=json.dumps(res_))
	except Exception as e:
		return render_template("error.html", message=str(e))

# app.run(host="0.0.0.0", port=1116, ssl_context=('cert/server.crt', 'cert/server.key'))
# app.run(host="0.0.0.0", port=1116)
app.run(host="0.0.0.0", port=1116, ssl_context=('cert/2968267_zilliqagraph.com.pem', 'cert/2968267_zilliqagraph.com.key'))