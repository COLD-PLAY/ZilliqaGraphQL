1. Demo's File Structure

```
─Zilliqa
   ├─documets
   |   ├─document.md
   |   ...
   ├─log
   |   ├─out.log
   |   ...
   ├─pictures
   ├─scripts
   |   ├─getdata.py
   |   ...
   ├─static
   │   ├─js
   |   |   ├─jquery-3.4.1.min.js
   |   |   ├─echarts-all.js   
   |   |   ...
   │   ├─css
   |   |   └─style.css
   ├─templates
   │   ├─index.html
   │   ├─result.html
   |   ...
   └─app.py
```
### 2. How to Use
​		the [neo4j url](http://54.254.250.156:7474/), a remote neo4j graph database, check the current `BlockNum` by input `MATCH (n:TxBlock) RETURN COUNT(n)` and input `query` of neo4j to get information you wanna know. And you can find the data in the database at [here](documents/document.md).

​		etc.

### 3. Docs
&emsp;&emsp;the demo's doc is [Demo-Docs](documents/document.md).