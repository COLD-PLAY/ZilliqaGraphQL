from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher, walk
import time, json

##连接neo4j数据库，输入地址、用户名、密码
graph = Graph('http://localhost:7474', username='neo4j', password='liaozhou1998')
matcher = NodeMatcher(graph)
matcher_r = RelationshipMatcher(graph)

def test():
	block = matcher.match("TxBlock", BlockNum=str(122)).first()
	mined = matcher_r.match([block], "mined").first()
	for _ in walk(mined):
		print(type(_), _)
	txss = matcher.match("Tx", epoch_num="59903")
	txs = []
	for tx in txss:
		txs.append(tx)
	txs = sorted(txs, key=lambda tx: int(tx["amount"]))
	for tx in txs:
		print(tx)
	address = "46c39a963a1f26e08de63d0a27c88e01c6d8a6f5"
	account = matcher.match("Account", address=address).first()
	print(account)

	txs = matcher.match("Tx")
	i = 2
	for tx in txs:
		print(tx)
		if not i:
			break
		i -= 1

def deleteTxBlock(start, end):
	for i in range(start, end):
		print(i)
		txblock = matcher.match("TxBlock").where(BlockNum=str(i)).first()
		if txblock:
			print("delete")
			graph.delete(txblock)

# 获取BlockNum 从start到end过程中的矿工
def getMiners(start, end):
	miners = []
	for i in range(start, end+1):
		block = matcher.match("TxBlock", BlockNum=str(i)).first()
		mined = matcher_r.match([block], "mined").first()
		miners.append(mined.end_node)
	return miners

def getAccountTxs(address):
	txs = []
	account = matcher.match("Account", address=address).first()
	sends = matcher_r.match([account], "send")
	reces = matcher_r.match([account], "receive")
	for send in sends:
		j = 0
		for _ in walk(send):
			j += 1
			if j == 3:
				txs.append(_)
	for rece in reces:
		j = 0
		for _ in walk(rece):
			j += 1
			if j == 3:
				txs.append(_)
	return txs

	# txs = getAccountTxs("A1E7973854dE977A86e307F127Ad4B00312ae03F")
	# for tx in txs:
	# 	print(tx)

# 返回address 账户挖的所有块
def getMinedBlocks(address):
	account, blocks = matcher.match("Account", address=address).first(), []
	mines = matcher_r.match([account], "mine")
	for mine in mines:
		# print(list(mine.types()[0]))
		blocks.append(mine.end_node)
		break
	return blocks

	# address = "9b9527237c8b64daa54229a2e290ae6ab563a380"
	# blocks = getMinedBlocks(address)
	# for block in blocks:
	# 	num = block["NumTxns"]
	# blocks = [dict(block) for block in blocks]
	# print(json.dumps(blocks))

def getBalance(address):
	return matcher.match("Account", address=address).first()

	# address = "9b9527237c8b64daa54229a2e290ae6ab563a380"
	# # account = graph.run("match(n:Account{address:'9b9527237c8b64daa54229a2e290ae6ab563a380'}) return n")
	# accounts = graph.run("match (a:TxBlock)-[r:has]->(b:Tx) return r limit 10")
	# print(accounts.keys())

	# res = getBalance("2333")
	# if not res[0]:
	# 	print("error")
	# address = "9b9527237c8b64daa54229a2e290ae6ab563a380"
	# account = getBalance(address)
	# print(account)
	# label_attr = {"TxBlock": "BlockNum", "DsBlock": "BlockNum", "Account": "address", "Tx": "TxHash"}
	# nodes = [getBalance("9b9527237c8b64daa54229a2e290ae6ab563a380")]
	# label = "has"
	# print("Relation %s of <%s: %s> is not existed!" % (
	# 	label, list(nodes[0].labels)[0], nodes[0][label_attr[list(nodes[0].labels)[0]]]
	# ))

	# rels = matcher_r.match(r_type="233")
	# for _ in rels:
	# 	print(_)

# miners = getMiners(1, 100)
# for miner in miners:
# 	print(miner)
deleteTxBlock(175334, 183160)