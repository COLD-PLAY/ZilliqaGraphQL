function getOption(graphInfo){
	// set style for nodes
	graphInfo.nodes.forEach(function (node) {
		//node.itemStyle = null;//
		//node.symbolSize = node.size; // set size
		// Use random x, y
		node.symbolSize = 20;
		node.x = node.y = null;
		node.draggable = true;
	});

	title=graphInfo['title']
	nodes=graphInfo['nodes']
	links=graphInfo['links']
	categories=graphInfo['categories']
	 
	//设置option样式
	option = {
		title : {
			text:title,
			x:'right',
			y:'bottom'
		},
		tooltip : {
			trigger: 'item',
			formatter: '{a} : {b}'
			//formatter: function(params){ //触发之后返回的参数，这个函数是关键
			//if (params.data.category != undefined) //如果触发节点
			//	window.open("http://www.baidu.com")
			//}
		},
		color:['#EE6A50','#4F94CD','#B3EE3A','#DAA520'],
		toolbox: {
			show : true,
			feature : {
				restore : {show: true},
				magicType: {show: true, type: ['force', 'chord']},
				saveAsImage : {show: true}
			}
		},
		legend: {
			x: 'left',
			data: categories.map(function (a) {
				return a.name;
			})
		},
		series : [
			{
				type:'force',
				name : title,
				ribbonType: false,
				categories : categories,
				itemStyle: {
					normal: {
						label: {
							show: true,
							textStyle: {
								color: '#333'
							}
						},
						nodeStyle : {
							brushType : 'both',
							borderColor : 'rgba(255,215,0,0.4)',
							borderWidth : 1
						},
						linkStyle: {
							type: 'curve'
						}
					},
					emphasis: {
						label: {
							show: false
							// textStyle: null
						},
						nodeStyle : {
							//r: 30
						},
						linkStyle : {}
					}
				},
				useWorker: false,
				minRadius : 15,
				maxRadius : 25,
				gravity: 1.1,
				scaling: 1.1,
				roam: 'move',
				nodes:nodes,
				links :links
			}
		]
	};
	return option
}
function createGraph(myChart,mygraph){
	// set option style
	option = getOption(mygraph)
	// drawl graph by option
	myChart.setOption(option);
	// click to jump
	myChart.on('click', function (params) {
		var data = JSON.stringify(params.value);
		alert(data);
	});
	//myChart.hideLoading();
}