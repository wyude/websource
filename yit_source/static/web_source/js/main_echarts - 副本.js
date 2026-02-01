$(document).ready(function() {

    var chartDom = document.getElementById('mapContainer');
	// 注意：初始化时可以指定渲染器为 'canvas' 或 'svg'
    // 对于复杂地图和 ECharts 结合，Canvas 通常性能更好
    //var myChart = echarts.init(chartDom);
	var myChart = echarts.init(chartDom, null, { renderer: 'canvas' })
    var option;

    // --- 1. 定义管道线路数据 ---
    // 原始坐标点数组 [经度, 纬度]
    var pipelinePoints = [
        [119.538086, 39.903423], // 节点 0
        [119.538086, 39.901176], // 节点 1
        [119.538086, 39.904546], // 节点 2
        [119.538086, 39.903757], // 节点 3
        [119.538086, 39.908810]  // 节点 4
    ];

    // --- 2. 将点数据转换为 ECharts lines 系列需要的数据格式 ---
    // ECharts lines 数据格式: [{ coords: [ [lng1, lat1], [lng2, lat2] ], lineStyle: {...}, data: {...} }, ...]
    // 每个对象代表一条线段
    var pipelineLineData = [];
    for (var i = 0; i < pipelinePoints.length - 1; i++) {
        pipelineLineData.push({
            coords: [pipelinePoints[i], pipelinePoints[i + 1]],
            // 可以在这里为特定线段设置独立样式或附加数据
            lineStyle: {
                // color: i % 2 === 0 ? 'red' : 'blue', // 示例：交替颜色
                // width: 8 // 示例：特定线段宽度
            },
            // 附加数据，用于交互时获取
            data: {
                segmentId: 'SEG_' + i,
                fromNode: i,
                toNode: i + 1,
                pressure: Math.random() * 100 + 50 // 示例：随机压力值
            }
        });
    }

     // --- 3. (可选) 定义关键点数据 (用于 scatter 系列) ---
     var keyPointsData = pipelinePoints.map(function(point, index) {
        return {
            name: '节点 ' + index,
            value: point.concat([Math.random() * 50]), // [经度, 纬度, 其他值 (可选)]
            // 可以在这里附加更多节点信息
            nodeInfo: {
                id: 'NODE_' + index,
                type: (index === 0 || index === pipelinePoints.length - 1) ? '端点' : '中间点',
                elevation: Math.random() * 100 // 示例：随机高程
            }
        };
    });


    // --- 4. 配置 ECharts Option ---
    option = {
        // --- 配置 AMap 底图 ---
        amap: {
            center: [119.538086, 39.904546], // 地图中心点
            zoom: 18,                      // 初始缩放级别
			minZoom: 10,
            maxZoom: 20,
            resizeEnable: true,            // 监听容器尺寸变化
			rotateEnable:true,
			pitchEnable:true,
			// 使用 layers 时，通常不设置 mapStyle 或设置为空
            //mapStyle: 'amap://styles/whitesmoke', // 地图样式 (可选: normal, dark, light, whitesmoke, fresh, grey, gravel, blue, darkblue)
            viewMode: '3D', // 可选：开启 3D 视图
            pitch: 45,      // 可选：3D 视图下的俯仰角
			rotation: -45, // 初始顺时针旋转角度
			labelzIndex: 130, // 提高标注图层层级，确保在 ECharts 图形之上 (可选)
			// showLabel: false, // 如果不需要路名等地名标注，可以关闭
            layers: [ // 可选：添加其他图层，如路网、卫星图等
				// !!! 顺序很重要: 卫星图层在最底层
                new AMap.TileLayer.Satellite(),
				// 路网图层（显示道路和地名标签），叠在卫星图上
                new AMap.TileLayer.RoadNet(),
				new AMap.Buildings({
					zooms: [16, 20],
					zIndex: 10,
					heightFactor: 1//1倍于默认高度，3D下有效
				})
             ],
            // 可以配置更多 AMap 初始化参数...
        },
        // --- ECharts 图表系列 ---
        series: [
            // --- 绘制管线的 lines 系列 ---
            {
                name: 'Pipeline',
                type: 'lines',
                coordinateSystem: 'amap', // 关键：指定坐标系为 amap
                data: pipelineLineData,   // 使用转换后的线段数据
                // 线条样式
                lineStyle: {
                    color: '#3366FF', // 默认线条颜色
                    opacity: 0.9,
                    width: 6
                },
                // (可选) 线条高亮状态下的样式
                emphasis: {
                    focus: 'series', // 'series' | 'self'
                    lineStyle: {
                        width: 8,
                        color: '#FF0000' // 高亮时变红
                    }
                },
                // (可选) 线条特效 (如流动效果)
                effect: {
                    show: true,
                    period: 6,          // 特效动画时间，单位 s
                    trailLength: 0.3,   // 特效尾迹长度，0 到 1
                    symbol: 'arrow',    // 特效图形，可选 'circle', 'rect', 'roundRect', 'triangle', 'diamond', 'pin', 'arrow', 'none'
                    symbolSize: 8,     // 特效图形大小
                    color: '#fff'       // 特效颜色
                },
                silent: false // false 表示响应鼠标事件
            },
            // --- (可选) 绘制关键点的 scatter 系列 ---
            {
                name: 'Key Points',
                type: 'scatter', // 或 'effectScatter' 带涟漪效果
                coordinateSystem: 'amap',
                data: keyPointsData,
                symbolSize: 10, // 点的大小
                // (可选) 点的样式
                itemStyle: {
                    color: '#FF5733'
                },
                 // (可选) 点的高亮状态
                 emphasis: {
                    focus: 'series',
                    itemStyle: {
                        borderColor: '#000',
                        borderWidth: 2
                    }
                },
                // (可选) 标签显示
                label: {
                    formatter: '{b}', // 显示 name
                    position: 'right',
                    show: false // 默认不显示，可在 emphasis 中开启
                },
                encode: { // 如果 value 数组包含多个值，指定经纬度来源
                    value: 2 // value[2] 作为视觉映射依据（例如控制点大小或颜色）
                },
                silent: false // 响应鼠标事件
            }
        ],
        // --- (可选) 提示框组件 ---
        tooltip: {
            trigger: 'item', // 'item' 针对数据项（点或线段），'axis' 主要用于笛卡尔坐标系
            formatter: function (params) {
                // console.log(params); // 调试：查看 params 结构
                if (params.componentSubType === 'lines') {
                    // 点击的是线段
                    let data = params.data.data; // 获取附加数据
                    return `管线段: ${data.segmentId}<br/>` +
                           `从: 节点 ${data.fromNode}<br/>` +
                           `到: 节点 ${data.toNode}<br/>` +
                           `压力: ${data.pressure.toFixed(2)} kPa`;
                } else if (params.componentSubType === 'scatter') {
                    // 点击的是点
                    let data = params.data.nodeInfo; // 获取附加数据
                    return `节点: ${params.name}<br/>` +
                           `类型: ${data.type}<br/>` +
                           `高程: ${data.elevation.toFixed(2)} m<br/>`+
                           `坐标: ${params.value[0].toFixed(6)}, ${params.value[1].toFixed(6)}`;
                }
                return '未知元素';
            }
        }
    };

    // --- 5. 设置 ECharts Option ---
	// 在设置 option 之前或之后获取 amap 实例都可以，但添加控件必须在实例创建后
    option && myChart.setOption(option);
	// --- 4. 获取 AMap 实例并添加控件 ---
    // 确保 ECharts 已经初始化了 AMap 实例
    // 使用 try-catch 或延时可能更稳妥，但通常 setOption 后就可以获取
    try {
        var amapInstance = myChart.getModel().getComponent('amap').getAMap();

        // 添加 ControlBar 控件
        var controlBar = new AMap.ControlBar({
            position: {
                top: '80px', // 调整位置，避免和 ECharts tooltip 冲突
                right: '20px'
            },
            showControlButton: true // 显示旋转和倾斜按钮
        });
        amapInstance.addControl(controlBar);

        // (可选) 可以添加其他控件，如比例尺 Scale, 工具条 ToolBar 等
        // amapInstance.addControl(new AMap.Scale());
        // amapInstance.addControl(new AMap.ToolBar({ position: 'LT' }));

        console.log("AMap instance obtained and ControlBar added.");

        // 可以在这里继续监听 AMap 事件
        amapInstance.on('zoomchange', function() {
            console.log('Map Zoom Changed:', amapInstance.getZoom());
        });

    } catch (e) {
        console.error("Failed to get AMap instance or add control:", e);
        // 可以添加一些错误处理或提示
    }

    // --- 6. 添加交互事件监听 ---
    myChart.on('click', function(params) {
        console.log('Clicked:', params); // 在控制台打印点击事件的详细信息

        // 更新信息面板内容
        var infoHtml = '';
        if (params.componentSubType === 'lines' && params.data && params.data.data) {
            let data = params.data.data;
            infoHtml = `<strong>点击了管线段:</strong> ${data.segmentId} (从节点 ${data.fromNode} 到 ${data.toNode}), 压力: ${data.pressure.toFixed(2)} kPa`;
        } else if (params.componentSubType === 'scatter' && params.data && params.data.nodeInfo) {
            let data = params.data.nodeInfo;
            let value = params.value;
            infoHtml = `<strong>点击了节点:</strong> ${params.name} (ID: ${data.id}), 类型: ${data.type}, 高程: ${data.elevation.toFixed(2)} m, 坐标: [${value[0].toFixed(6)}, ${value[1].toFixed(6)}]`;
        } else {
             infoHtml = '点击了地图或其他区域。';
        }

        $('#infoPanel').html(infoHtml).show(); // 使用 jQuery 更新并显示信息面板
    });

    // --- 7. (可选) 监听地图缩放或平移事件 (如果需要的话) ---
    // 注意：AMap 实例是由 echarts-extension-amap 内部管理的
    // 获取 AMap 实例需要稍微迂回一点
    var amapInstance = myChart.getModel().getComponent('amap').getAMap();
    amapInstance.on('zoomchange', function() {
        console.log('Map Zoom Changed:', amapInstance.getZoom());
    });
    amapInstance.on('moveend', function() {
         console.log('Map Move Ended. Center:', amapInstance.getCenter());
    });


    // --- 8. 窗口大小改变时，重绘 ECharts 图表 ---
    $(window).on('resize', function(){
        myChart.resize();
    });

});