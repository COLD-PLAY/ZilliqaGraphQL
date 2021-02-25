## APIs INTRODUCTION
---
### getBalance
Returns the <Account [py2neo.data.Node](https://py2neo.org/v4/data.html#py2neo.data.Node) Type> with its balance. You can use dict(result) function to get the result of <Python Dict Type>.

#### ARGUMENTS
|Parameter|Type|Required|Description|
|--|--|--|--|
|**address**|string|Required|"The account's address"|

#### Example response:
```json
{
	address: '46c39a963a1f26e08de63d0a27c88e01c6d8a6f5',
	balance: '97000000000',
	existed: 'true'
}
```
---
### getTxs
Returns the sorted array of <Tx [py2neo.data.Node](https://py2neo.org/v4/data.html#py2neo.data.Node) Type> between 2 account.

#### ARGUMENTS
|Parameter|Type|Required|Description|
|--|--|--|--|
|**address1**|string|Required|"The account1's address"|
|**address2**|string|Required|"The account2's address"|
|**type**|string|Required|"The query type('all'[default], 'recent', 'period')"|
|**start**|int|Optional **Required if type='period'**|"Start blocknum"|
|**end**|int|Optional **Required if type='period'**|"End blocknum"|

#### Example response:
```json
[{
	ID: '1f6c2d39cdf657e2253bb9fcf414b5988ad007818b4f2b19a1beff7e136318a2',
	amount: '674962570466901',
	cumulative_gas: '1',
	epoch_num: '59903',
	fromAddr: '7ccce6d75c35e1866b87ada3c0f965aae725d49a',
	gasLimit: '1',
	gasPrice: '1000000000',
	nonce: '1',
	senderPubKey: '0x024EAF6FCD4223E66A851856AD3B5FE5E96E835F9B4EA7C4385ED3A4ED8744227B',
	signature: '0x3FA9F64FA030774A331C3E743375DFC12924CCA770705E82A44FC018E208E5614DA32AD745BC8F1D72F01335CBFF212E078964F93E0F792E1F2D6C54B0C14C24',
	success: 'True',
	toAddr: 'd942c5606f3fb2e34f1c0933c9406f0453be7f9a',
	version: '65537'
},
{
	ID: '211283d4f97f6e45cc051cacbd8dc7ea854f8bce41ec818b464fd0531cafedbd',
	amount: '676921020823241',
	cumulative_gas: '1',
	epoch_num: '59903',
	fromAddr: 'c0985f691456b5e6b386840b97d8cf5325bbe076',
	gasLimit: '1',
	gasPrice: '1000000000',
	nonce: '1',
	senderPubKey: '0x0248670D4586B012452CCE3C379CFABB7A8C51E3FEECF3DE69D4083BA2BDDBDAF3', signature: '0x1AFC8E44530DA1165D9FB8A13936990C7F1157A230DD8ADDA7DBCB6A78B8CC0B9948A13B2C3A362C5982E2622AEF1AB199664F06B28F6D0440526207AFC4EFA3',
	success: 'True',
	toAddr: 'd942c5606f3fb2e34f1c0933c9406f0453be7f9a',
	version: '65537'
}]
```
---
### getMiners
Returns the array of <Account [py2neo.data.Node](https://py2neo.org/v4/data.html#py2neo.data.Node) Type> between 2 blocknum.

#### ARGUMENTS
|Parameter|Type|Required|Description|
|--|--|--|--|
|**start**|int|Required|"The start blocknum"|
|**end**|int|Required|"The end blocknum"|

#### Example response:
```json
[{
	address: '0a8323ac339f42fbc2670f9de68390fa43c77c2e',
	balance: '0',
	existed: 'false'
},
{
	address: 'd8b4397a0303c12830a95abc225585af71f41d89',
	balance: '0',
	existed: 'false'
}]
```
---
### getAccountTxs
Returns the array of <Tx [py2neo.data.Node](https://py2neo.org/v4/data.html#py2neo.data.Node) Type> of an account.

#### ARGUMENTS
|Parameter|Type|Required|Description|
|--|--|--|--|
|**address**|string|Required|"The account's address"|

#### Example response:
```json
[{
	ID: '825878decc4fe3f202815817c27c558dd0f5890514821dfc8aeeea03753e5bd6',
	amount: '669700111576395',
	cumulative_gas: '1',
	epoch_num: '59903',
	fromAddr: '93d2ea3c47b084bd358629d3ac741e080ac72ac7',
	gasLimit: '1',
	gasPrice: '1000000000',
	nonce: '1',
	senderPubKey: '0x025B0D54DFCABB3FC095A2577F60D6A4909FEDB3FCC0DA5920B2AFF77272E25B40',
	signature: '0x0D1A1F37EAA28529380CF4FA6FA878902BE9E995636F0D74387952B70DEACFA9854F69D28510A7273F9B45BEE8A272C803C9A9901A78200325172C3E238058AD',
	success: 'True',
	toAddr: 'd942c5606f3fb2e34f1c0933c9406f0453be7f9a',
	version: '65537'
},
{
	ID: '8afe62bff3532c8d582437cf9f1fa9fa8beb22a74898e773036e521156ee11cb',
	amount: '242137739980056',
	cumulative_gas: '1',
	epoch_num: '59903',
	fromAddr: '272115809054dd02ec5488601a8d5c883bedac83',
	gasLimit: '1',
	gasPrice: '1000000000',
	nonce: '1',
	senderPubKey: '0x027DEEF14A42798159216692B0F7683A069D3D5A9C16866204D95F06D11789A457',
	signature: '0xD78EAC5804AF62E9FFB9138FFF4446BFA55BC5A8B5FEA78ED161A05D620775D0302BFB54DFCC62A4F1294E442FF6D8F793F56B89635B3825F6DE38BF2D6DE4A4',
	success: 'True',
	toAddr: '422c85ab78f955776898c646f4a81a2d4c0b0f4d',
	version: '65537'
}]
```
---
### getMinedBlock
Returns the array of <Tx/DsBlock [py2neo.data.Node](https://py2neo.org/v4/data.html#py2neo.data.Node) Type> mined by an account.

#### ARGUMENTS
|Parameter|Type|Required|Description|
|--|--|--|--|
|**address**|string|Required|"The account's address"|

#### Example response:
```json
{
	BlockNum: '61261',
	DSBlockNum: '613',
	GasLimit: '2000000',
	GasUsed: '0',
	HeaderSign: '13BA2E480D49BB6060B5E2D4FB6B25F9E43C86DCD1160A20F2FB44BFB487A0C6CA1B9F7CB297A94434D02A8E791236D60968AF6EA2343298B45AE6BD27BBC24F',
	MbInfoHash: 'e77327418034db80637759eec72181a9cb6b29b448763aad7cc883215865d87c',
	MicroBlock0Hash: '2a7ce94a4a26dfe2e1d10cbe85cab05162c450027b1ae0f81410fd9b71bf24e6',
	MicroBlock0TxnRootHash: '0000000000000000000000000000000000000000000000000000000000000000',
	MicroBlock1Hash: 'f2c1135635a4160cbc324aa93a3897859958ea6672abe7632aa775adcd315029',
	MicroBlock1TxnRootHash: '0000000000000000000000000000000000000000000000000000000000000000',
	MicroBlock2Hash: 'e589c735198da5436aaa0dbaf8c0f84fa0191580f02d21b43c7971370067f146',
	MicroBlock2TxnRootHash: '0000000000000000000000000000000000000000000000000000000000000000',
	MicroBlock3Hash: 'd1bea3286727b46d0029e8b59f7be34d67f6d7fc3cdb1ad435e754a1aa8f1ec5',
	MicroBlock3TxnRootHash: '0000000000000000000000000000000000000000000000000000000000000000',
	MinerPubKey: '0x0204D5A9E32D12412DCAC740C11CBFE85555C3A22591BF733AF6E65C2A3E69F06D',
	NumMicroBlocks: 4,
	NumTxns: 0,
	PrevBlockHash: '52fa49fdca8ca999644ca140c4d595839d450b2c207574ca8938cbef3a12101d',
	Rewards: '0',
	StateDeltaHash: '0000000000000000000000000000000000000000000000000000000000000000',
	StateRootHash: '442b66ad1758906e3c8997e3f5681c50f819a5d3ea357dbe3e154666afff4be4',
	Timestamp: '1554284563581924',
	Version: 1
}
```