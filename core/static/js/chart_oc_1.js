const getOptionChart = async () => {
    try {
        const response = await fetch("http://127.0.0.1:8000/proveedores/get_chart_oc_1");
        return await response.json();
    } catch (ex) {
        alert(ex);
    }
  };
  
  const initChart = async () => {
    const myChart = echarts.init(document.getElementById("chart_oc1"));
  
    myChart.setOption(await getOptionChart());
  
    myChart.resize();
  };
  
  window.addEventListener("load", async () => {
    await initChart();
  });
  