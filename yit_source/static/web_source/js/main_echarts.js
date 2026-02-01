$(document).ready(function() {
    // --- Configuration ---
    const A_MAP_KEY = 'ba726bed3cf909842a925d513bda506f'; // Replace with your actual key
    /*
    const WELL_API_URL = '/api/wells'; // Example API endpoint
    const PATH_API_URL = '/api/paths'; // Example API endpoint
    const UPDATE_STATUS_API_URL = '/api/paths/{pathId}/status'; // Example API endpoint
    */
    // --- ECharts / Styling Configuration ---
    const wellTypeColors = { // Define colors for ECharts points
        'xj': '#0d6efd', // Blue
        'rdj': '#198754', // Green
        'gj': '#ffc107', // Yellow
        'default': '#6c757d' // Grey for unknown
    };
    const wellSymbolSize = 3; // Size of effectScatter points

    const pathColors = { // Define colors for ECharts lines
        'default': '#007bff', // Blue
        'highlight': '#ff6a00', // Bright Orange for highlight
        'typeX': '#dc3545', // Red
        'typeY': '#28a745', // Green
        // Add more path types/colors as needed
    };
    const pathWidth = 4;
    const pathHighlightWidth = 7;

    const coreStatuses = ['normal', 'unavailable', 'high-loss', 'in-use'];
    const coreStatusClasses = { /* ... same as before ... */
        'normal': 'core-status-normal',
        'unavailable': 'core-status-unavailable',
        'high-loss': 'core-status-high-loss',
        'in-use': 'core-status-in-use',
    };

    // --- State Variables ---
    let amapInstance = null; // AMap instance
    let chartInstance = null; // ECharts instance
    let allWellData = [];
    let allPathData = [];
    let currentChartOption = null; // To store the current ECharts option
    let highlightedLineIndex = -1; // Index of the highlighted line in the ECharts series data
    let originalLineStyle = null;  // To store the original style of the highlighted line
    // --- Initialization ---
    function initializeMapAndChart() {
        // 1. Initialize AMap
        amapInstance = new AMap.Map('map-container', {
            zoom: 16,
            center: [119.538086, 39.904546], // Set initial center
            viewMode: '3D',
            skyColor: '#332c41',
            resizeEnable: true,            // 监听容器尺寸变化
			rotateEnable:true,
			pitchEnable:true,
            pitch: 45,      // 可选：3D 视图下的俯仰角
			rotation: -45, // 初始顺时针旋转角度
        });
        // 2. Add ControlBar Plugin for 3D Controls
        amapInstance.plugin(['AMap.ControlBar'], function() { // Load plugin
            var controlBar = new AMap.ControlBar({
                position: {
                    top: '100px', // Adjust position to avoid overlap with layer controls
                    right: '100px'
                },
                //showZoomBar: true,
                showControlButton: true // Shows Pitch and Rotate controls
            });
            amapInstance.addControl(controlBar); // Add control to the map
            console.log("AMap ControlBar added.");
        });
        
        // 2. Initialize ECharts on the same container
        chartInstance = echarts.init(document.getElementById('map-container'));

        // 3. Load data and set initial ECharts option
        loadDataAndSetOption();

        // 4. Setup UI Controls
        setupControls();

        // 5. Bind ECharts Click Event
        bindChartEvents();

         // 6. Add listener to reset highlight when map is clicked (optional)
        amapInstance.on('click', resetHighlightAndInfo); // AMap click
         // We might also need to handle clicks on ECharts background
         /*
         chartInstance.getZr().on('click', function (event) {
             // If the click is not on a graphic element, reset highlight
             if (!event.target) {
                 resetHighlightAndInfo();
             }
         });
         */
    }

    // --- Data Loading & ECharts Option Setup ---
    function loadDataAndSetOption() {
        Promise.all([
            $.getJSON(WELL_API_URL),
            $.getJSON(PATH_API_URL)
        ])
        .then(([wells, paths]) => {
            allWellData = eval(wells);
            allPathData = eval(paths);

            console.log("Wells Loaded:", allWellData);
            console.log("Paths Loaded:", allPathData);

            // Prepare ECharts options
            currentChartOption = generateChartOption();

            // Set ECharts option
            if (chartInstance && currentChartOption) {
                chartInstance.setOption(currentChartOption);
                console.log(chartInstance);
                console.log("ECharts option set.");

                 // Adjust map view AFTER ECharts has rendered on the map
                // This is a bit tricky as ECharts rendering might take a moment.
                // A small delay might be needed, or use a callback if available.
                setTimeout(() => {
                    adjustMapView();
                }, 500); // Adjust delay as needed

            } else {
                 console.error("ECharts instance or option not available.");
            }
        })
        .catch(error => {
            console.error("Error loading data:", error);
            alert("Failed to load visualization data. Please check the console.");
        });
    }

    // --- Generate ECharts Option ---
    function generateChartOption(showWells = true, showPaths = true) {
        const series = [];

        // 1. Well Series (effectScatter)
        if (showWells) {
            const wellPoints = allWellData.map(well => ({
                name: well.info || `Well ${well.id}`,
                // ECharts value format for effectScatter on map: [lng, lat, optional_value]
                value: [well.location1, well.location2, well.info],
                itemStyle: {
                    color: wellTypeColors[well.dic_guanjing__key] || wellTypeColors.default
                },
                // Store original data for click events
                originalData: well
            }));

            series.push({
                name: '弱电井',
                type: 'effectScatter', // or 'effecteffectScatter' for effects
                rippleEffect: {
                    scale: 8,        // 最大扩散比例
                    period: 3,       // 动画周期(秒)
                    brushType: 'fill' 
                  },
                coordinateSystem: 'amap',
                data: wellPoints,
                symbolSize: wellSymbolSize,
                label: { // Optional: Show labels
                    // formatter: '{b}', // {b} is name
                    // position: 'right',
                    // show: false
                },
                emphasis: { // Style on hover
                     scale: true, // Enlarge symbol
                     label: {
                         show: true,
                         formatter: '{b}' // Show name on hover
                     }
                 }
            });
        }
        
        // 2. Path Series (Lines)
        if (showPaths) {
             // Parse coreStatus JSON if needed (should happen on data load really)
             allPathData.forEach(path => {
                 if (typeof path.zt === 'string') {
                     try {
                         path.zt = JSON.parse(path.zt);
                     } catch (e) {
                         console.error(`Failed to parse coreStatus JSON for path ${path.id}:`, path.zt);
                         path.zt = [];
                     }
                 }
                  if (!Array.isArray(path.zt)) {
                      console.warn(`CoreStatus for path ${path.id} is not an array, defaulting to empty.`);
                      path.zt = [];
                  }
             });

            const pathLines = allPathData.map((path, index) => ({
                name: path.info || `Path ${path.id}`,
                 // ECharts lines expects array of coordinate pairs
                 // IMPORTANT: Ensure coordinates are [[lng1, lat1], [lng2, lat2], ...]
                 coords: eval(path.points),
                 lineStyle: {
                     color: pathColors[path.type] || pathColors.default,
                     width: pathWidth,
                     opacity: 0.8
                 },
                 // Store original data and its index in this array
                 originalData: path,
                 originalIndex: index // Store its own index within this data array
            }));

            series.push({
                name: '光缆路径',
                type: 'lines',
                coordinateSystem: 'amap',
                data: pathLines,
                polyline: true, // Render coords as a single polyline
                lineStyle: {
                    // Default style for lines in this series (can be overridden in data)
                    width: pathWidth,
                    opacity: 0.8
                },
                emphasis: { // Style on hover
                    lineStyle: {
                        width: pathWidth + 2, // Slightly thicker on hover
                        color: 'red',
                        opacity: 1
                    }
                },
                // Effect for drawing lines (optional)
                effect: {
                     show: true,
                     period: 6,
                     trailLength: 0.7,
                     color: '#fff',
                     symbolSize: 4
                 }
            });
        }
        
        // 3. AMap Component Configuration (Links ECharts to AMap)
        const option = {
            // Tooltip configuration (basic info on hover)
            tooltip: {
                trigger: 'item',
                formatter: function (params) {
                    if (params.seriesType === 'effectScatter' && params.data.originalData) {
                         const data = params.data.originalData;
                         return `${data.info || '未命名弱电井'}<br/>类型: ${data.dic_guanjing__key || '未知'}<br/>描述: ${data.remarks || '无'}`;
                    } else if (params.seriesType === 'lines' && params.data.originalData) {
                         const data = params.data.originalData;
                         return `${data.info || '未命名路径'}<br/>描述: ${data.remarks || '无'}`;
                    }
                    return '';
                }
            },
            amap: {
                // AMap options that ECharts should control or sync with
                // center: amapInstance.getCenter(), // Let AMap control center initially
                // zoom: amapInstance.getZoom(), // Let AMap control zoom initially
                viewMode: '3D',
                zoom: 16,
                center: [119.538086, 39.904546], // Set initial center
                resizeEnable: true,            // 监听容器尺寸变化
                rotateEnable:true,
                pitchEnable:true,
                pitch: 45,      // 可选：3D 视图下的俯仰角
                rotation: -45, // 初始顺时针旋转角度
                // mapStyle: 'amap://styles/dark', // Optional: AMap style
                // IMPORTANT: Ensures ECharts redraws when map moves
                renderOnMoving: true, // v1.8.0+
                echartsLayerInteractive: 2000, // Make ECharts layer sit above AMap base layer
                layers: [ // 可选：添加其他图层，如路网、卫星图等
				// !!! 顺序很重要: 卫星图层在最底层
                    //new AMap.TileLayer.Satellite(),
                    // 路网图层（显示道路和地名标签），叠在卫星图上
                    new AMap.TileLayer.RoadNet(),
                    new AMap.Buildings({
                        zooms: [16, 20],
                        zIndex: 10,
                        heightFactor: 1//1倍于默认高度，3D下有效
                    })
             ],
            },
            series: series
        };
        return option;
    }

    // --- Map View Adjustment ---
     function adjustMapView() {
         if (!amapInstance) return;

         const points = [];
         allWellData.forEach(w => points.push([w.location1,w.location2]));
         allPathData.forEach(p => {
             eval(p.points).forEach(c => points.push(c));
         });

         if (points.length > 0) {
             // Create AMap bounds object
             const bounds = new AMap.Bounds(...points[0], ...points[0]);
             points.forEach(p => bounds.extend(new AMap.LngLat(p[0], p[1])));

              if (!bounds.getSouthWest() || !bounds.getNorthEast()){
                  console.warn("Could not determine valid bounds from data.");
                  if(points.length > 0) amapInstance.setCenter(points[0]); // Center on first point at least
                  return;
              }

             // Use AMap's setFitView. Provide bounds directly.
              // Give it some padding [top, right, bottom, left]
              amapInstance.setBounds(bounds, false, [80, 80, 80, 80]);
            
              console.log("MapView adjusted.");
         } else {
              console.log("No points found to adjust map view.");
         }
     }


    // --- Event Handling ---
    function bindChartEvents() {
        if (!chartInstance) return;

        chartInstance.on('click', function (params) {
            console.log("ECharts click:", params);
            resetHighlightAndInfo(false); // Reset previous state but don't hide modal immediately

            if (params.componentType === 'series') {
                const data = params.data?.originalData; // Get our stored original data
                const seriesType = params.seriesType;

                if (seriesType === 'effectScatter' && data) { // Clicked on a Well
                    handleWellClick(data);
                } else if (seriesType === 'lines' && data) { // Clicked on a Path
                    handlePathClick(data, params.data.originalIndex); // Pass original index
                }
            } else {
                 // Clicked on chart background or other components
                  resetHighlightAndInfo();
            }
        });
    }

    function handleWellClick(wellData) {
        console.log("Well clicked (ECharts):", wellData);

        // Option 1: Use a dedicated info panel
        $('#infoTitle').text(wellData.name || '未命名弱电井');
        $('#infoDescription').text(`类型: ${wellData.type || '未知'} | 坐标: ${wellData.coordinates.join(', ')}`);
        $('#infoDetails').text(wellData.description || '无详细描述');
         if(wellData.photo){
             $('#infoPhoto').attr('src', wellData.photo).removeClass('d-none');
         } else {
              $('#infoPhoto').addClass('d-none').attr('src', '');
         }
        $('#infoPanel').removeClass('d-none');

        // Option 2: Open a simple Bootstrap Modal (if info is complex)
        // Option 3: Use ECharts tooltip (already configured for basic info)
    }

    function handlePathClick(pathData, lineIndex) {
        console.log("Path clicked (ECharts):", pathData, "Index:", lineIndex);

        // 1. Highlight Path in ECharts
        highlightEChartsLine(lineIndex);

        // 2. Show Info (e.g., in panel)
        $('#infoTitle').text(pathData.name || '未命名路径');
        $('#infoDescription').text(`总芯数: ${pathData.coreCount || '未知'}`);
        $('#infoDetails').text(pathData.description || '无详细描述');
         $('#infoPhoto').addClass('d-none').attr('src', ''); // Hide photo if shown before
        $('#infoPanel').removeClass('d-none');

        // 3. Open Core Visualization Modal
        populateAndShowCoreModal(pathData);
    }

     function resetHighlightAndInfo(hideModal = true) {
         // 1. Reset ECharts Line Highlight
         if (highlightedLineIndex !== -1 && currentChartOption) {
              const linesSeriesIndex = currentChartOption.series.findIndex(s => s.type === 'lines');
              if(linesSeriesIndex !== -1 && currentChartOption.series[linesSeriesIndex].data[highlightedLineIndex]){
                 // Check if originalLineStyle was stored before attempting to restore
                 if (originalLineStyle) {
                      currentChartOption.series[linesSeriesIndex].data[highlightedLineIndex].lineStyle = { ...originalLineStyle }; // Restore original
                      chartInstance.setOption(currentChartOption); // Update chart
                 } else {
                     // Fallback if original wasn't stored: reset to default path style
                      const path = currentChartOption.series[linesSeriesIndex].data[highlightedLineIndex].originalData;
                      currentChartOption.series[linesSeriesIndex].data[highlightedLineIndex].lineStyle = {
                          color: pathColors[path.type] || pathColors.default,
                          width: pathWidth,
                          opacity: 0.8
                      };
                     chartInstance.setOption(currentChartOption);
                 }
              }
         }
         highlightedLineIndex = -1;
         originalLineStyle = null;

         // 2. Hide Info Panel
         $('#infoPanel').addClass('d-none');

         // 3. Optionally hide Core Modal if open
         if (hideModal) {
            const coreModalInstance = bootstrap.Modal.getInstance(document.getElementById('coreModal'));
            if (coreModalInstance) {
                // coreModalInstance.hide(); // Consider if this is desired behavior on map click
            }
         }
     }

     function highlightEChartsLine(lineIndex) {
        if (!currentChartOption || lineIndex < 0) return;

        const linesSeriesIndex = currentChartOption.series.findIndex(s => s.type === 'lines');
         if (linesSeriesIndex === -1 || !currentChartOption.series[linesSeriesIndex].data[lineIndex]) {
             console.error("Could not find lines series or data for index:", lineIndex);
             return;
         }


        // Store original style *before* changing it
        originalLineStyle = { ... (currentChartOption.series[linesSeriesIndex].data[lineIndex].lineStyle || {}) };

        // Apply highlight style
        currentChartOption.series[linesSeriesIndex].data[lineIndex].lineStyle = {
            // Keep original color or use highlight color? Let's use a dedicated highlight color.
            color: pathColors.highlight,
            width: pathHighlightWidth,
            opacity: 1.0,
            shadowColor: 'rgba(0, 0, 0, 0.5)', // Optional shadow for emphasis
            shadowBlur: 5
        };

        highlightedLineIndex = lineIndex;

        // Update ECharts
        chartInstance.setOption(currentChartOption);
     }


    // --- Core Visualization Modal Logic ---
    function populateAndShowCoreModal(pathData) {
        const $modal = $('#coreModal');
        const $coreGrid = $('#core-grid');

        // Store pathId in the modal for later use during updates
        $modal.data('current-path-id', pathData.id);
        $modal.data('current-path-data', pathData); // Store full data for local updates

        $('#modalPathDescription').text(pathData.description || '无');
        $('#modalCoreCount').text(pathData.coreCount || 0);
        $('#modalPathId').text(pathData.id); // Show Path ID
        $coreGrid.empty();

        // Use the already parsed coreStatus array from pathData
        const coreStatus = pathData.coreStatus || [];

        for (let i = 0; i < (pathData.coreCount || 0); i++) {
            const statusData = coreStatus[i];
             let currentStatus = 'unavailable';
             if (statusData) {
                 // Handle string or object format
                 if (typeof statusData === 'string' && coreStatuses.includes(statusData)) {
                     currentStatus = statusData;
                 } else if (typeof statusData === 'object' && statusData !== null && coreStatuses.includes(statusData.status)) {
                     currentStatus = statusData.status;
                 }
             }

            const statusClass = coreStatusClasses[currentStatus] || coreStatusClasses['unavailable'];

            const $coreItem = $('<div></div>')
                .addClass('core-item')
                .addClass(statusClass)
                .attr('data-core-index', i)
                .attr('data-core-number', i + 1)
                // Removed path-id from item, get it from modal's data
                .attr('data-current-status', currentStatus);

            $coreGrid.append($coreItem);
        }

        // Ensure previous listeners are removed before adding new ones
        $('#core-grid').off('click', '.core-item').on('click', '.core-item', handleCoreItemClick);

        const modalInstance = new bootstrap.Modal($modal);
        modalInstance.show();
    }

     function handleCoreItemClick() { // Changed to be standalone function
         const $coreItem = $(this);
         const $modal = $('#coreModal');
         const pathId = $modal.data('current-path-id'); // Get pathId from modal data
         const pathData = $modal.data('current-path-data'); // Get pathData from modal data

         if (!pathId || !pathData) {
             console.error("Path ID or Data not found in modal context.");
             return;
         }

         const coreIndex = parseInt($coreItem.data('core-index'), 10);
         const currentStatus = $coreItem.data('current-status');

         // Determine next status
         const currentIndex = coreStatuses.indexOf(currentStatus);
         const nextIndex = (currentIndex + 1) % coreStatuses.length;
         const nextStatus = coreStatuses[nextIndex];

         // Update UI
         Object.values(coreStatusClasses).forEach(cls => $coreItem.removeClass(cls));
         $coreItem.addClass(coreStatusClasses[nextStatus]);
         $coreItem.data('current-status', nextStatus);

         console.log(`Path ${pathId}, Core ${coreIndex + 1}: Status changed to ${nextStatus}`);

         // Update local pathData store (critical for sending correct data)
         updateLocalCoreStatus(pathData, coreIndex, nextStatus);

         // Send update to backend
         updateCoreStatusOnServer(pathId, coreIndex, nextStatus, pathData.coreStatus);
     }

     function updateLocalCoreStatus(pathData, coreIndex, newStatus) {
         if (!pathData || !pathData.coreStatus) return;

         // Ensure array length
          while (pathData.coreStatus.length <= coreIndex) {
               pathData.coreStatus.push('unavailable'); // Or default object
          }

         // Update status (handle string/object)
          if (pathData.coreStatus[coreIndex] && typeof pathData.coreStatus[coreIndex] === 'object') {
               pathData.coreStatus[coreIndex].status = newStatus;
          } else {
               pathData.coreStatus[coreIndex] = newStatus;
          }
          console.log("Local coreStatus updated:", pathData.coreStatus);
     }


    // --- Backend Communication (Modified to accept updatedStatusArray) ---
    function updateCoreStatusOnServer(pathId, coreIndex, newStatus, updatedStatusArray) {
        // We now receive the fully updated array from the calling context

        const apiUrl = UPDATE_STATUS_API_URL.replace('{pathId}', pathId);

        $.ajax({
            url: apiUrl,
            type: 'POST', // Or PUT
            contentType: 'application/json',
            data: JSON.stringify({ coreStatus: updatedStatusArray }), // Send the updated array
            success: function(response) {
                console.log(`Successfully updated status for Path ${pathId}, Core ${coreIndex + 1}`, response);
                 // Find the path in the global store and update its status permanently too
                 const globalPathData = allPathData.find(p => p.id === pathId);
                 if (globalPathData) {
                     globalPathData.coreStatus = updatedStatusArray;
                 }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error(`Error updating status for Path ${pathId}, Core ${coreIndex + 1}:`, textStatus, errorThrown);
                alert(`更新纤芯状态失败 (路径: ${pathId}, 纤芯: ${coreIndex + 1}).`);

                 // Revert UI change in modal
                 const $modal = $('#coreModal');
                 const $coreItem = $modal.find(`.core-item[data-core-index='${coreIndex}']`);
                 const originalStatus = coreStatuses[(coreStatuses.indexOf(newStatus) - 1 + coreStatuses.length) % coreStatuses.length];
                 Object.values(coreStatusClasses).forEach(cls => $coreItem.removeClass(cls));
                 $coreItem.addClass(coreStatusClasses[originalStatus]);
                 $coreItem.data('current-status', originalStatus);

                 // Revert local pathData store in modal context
                 const pathData = $modal.data('current-path-data');
                  if(pathData){
                     updateLocalCoreStatus(pathData, coreIndex, originalStatus);
                  }
            }
        });
    }

    // --- UI Controls ---
    function setupControls() {
        $('#toggleWells').on('change', function() {
            toggleSeriesVisibility('effectScatter', $(this).prop('checked'));
        });

        $('#togglePaths').on('change', function() {
            toggleSeriesVisibility('lines', $(this).prop('checked'));
             if (!$(this).prop('checked')) {
                 resetHighlightAndInfo(); // Reset highlight if paths are hidden
             }
        });
    }

    function toggleSeriesVisibility(seriesType, visible) {
        if (!chartInstance || !currentChartOption) return;

        const showWells = seriesType === 'effectScatter' ? visible : $('#toggleWells').prop('checked');
        const showPaths = seriesType === 'lines' ? visible : $('#togglePaths').prop('checked');

        // Regenerate the option with the correct series shown/hidden
        currentChartOption = generateChartOption(showWells, showPaths);
        chartInstance.setOption(currentChartOption, {
             notMerge: false, // Allows adding/removing series cleanly
             lazyUpdate: true // Improve performance slightly
        });
         // Reapply highlight if it existed and the lines series is still visible
         if (showPaths && highlightedLineIndex !== -1) {
             // Small delay might be needed for setOption to apply
              setTimeout(() => {
                  highlightEChartsLine(highlightedLineIndex);
              }, 100);
         }

         console.log(`${seriesType} visibility set to ${visible}`);
    }


    // --- Start ---
    if (!A_MAP_KEY || A_MAP_KEY === 'YOUR_AMAP_API_KEY') {
        alert("请在 app.js 文件中替换 'YOUR_AMAP_API_KEY' 为您的高德地图 API Key!");
    } else {
        initializeMapAndChart();
    }

     // Optional: Resize ECharts when window resizes
     $(window).on('resize', function(){
         if(chartInstance){
             chartInstance.resize();
         }
     });
});